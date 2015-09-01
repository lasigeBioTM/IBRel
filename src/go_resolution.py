#!/usr/bin/env python
from __future__ import division, unicode_literals
import MySQLdb
import re
import sys
import xml.etree.ElementTree as ET
import os
import shutil
from subprocess import Popen, PIPE
from optparse import OptionParser
import cPickle as pickle
import logging
from sys import platform as _platform
import requests
import atexit
import multiprocessing
from config import chebi_conn as db

amino_acids = {
    'Ala': '',
    'Arg': '',
    'Ans': '',
    'Asp': '',
    'Cys': '',
    'Glu': '',
    'Gln': '',
    'Gly': '',
    'His': '',
    'Ile': '',
    'Leu': '',
    'Lys': '',
    'Met': '',
    'Phe': '',
    'Pro': '',
    'Ser': '',
    'Thr': '',
    'Trp': '',
    'Tyr': '',
    'Val': '',
    'Sec': '',
    'Pyl': '',
}

godic = "data/go_dic.pickle"
method = [0,0,0,0,0,0,0]
if os.path.isfile(godic):
    logging.info("loading GO...")
    go = pickle.load(open(godic, "rb"))
    loadedgo = True
    logging.info("loaded GO dictionary with %s entries", str(len(go)))
else:
    go = {}
    gochebi = False
    logging.info("new GO dictionary")
# [2, 4, 77, 18, 50, 1, 14]
# [2, 11, 152, 28, 83, 1, 34]
# [7, 48, 766, 169, 773, 20, 196]
# [19, 24, 542, 81, 0, 0, 147]
# [9, 49, 609, 101, 582, 0, 141]
# [0, 19, 114, 56, 241, 0, 0]
# [0, 19, 114, 56, 241, 0, 0]



def query_with_timeout(cur, timeout, query, *a, **k):
  conn1, conn2 = multiprocessing.Pipe(False)
  subproc = multiprocessing.Process(target=do_query,
                                    args=(cur, query, conn2)+a,
                                    kwargs=k)
  subproc.start()
  subproc.join(timeout)
  if conn1.poll():
    return conn1.recv()
  subproc.terminate()
  logging.debug(("Query %r ran for >%r" % (query, timeout)))

def do_query(cur, query, conn, *a, **k):
  cur.execute(query, *a, **k)
  return cur.fetchone()

def get_go_annotations(protid):
    '''
    :param protid
    :return: List of GOs associated with this protein
    '''
    gos = []
    payload = {"format":"tsv", "protein":protid, "db": "UniProtKB"}
    headers = {'user-agent': 'iice.fc.ul.pt/3.0 alamurias@lasige.fc.ul.pt'}
    try:
        r = requests.get("https://www.ebi.ac.uk/QuickGO/GAnnotation", params=payload, headers=headers)
    except requests.exceptions.ConnectionError:
        return None
    if r.text != "" and r.status_code != 400 and r.status_code != 404:
        try:
            response = r.text
            lines = response.split("\n")
            for l in lines[1:-1]:
                go = l.split('\t')[6]
                if go.startswith("GO:"):
                    gos.append(go)
                else:
                    logging.debug("what is this? {} in {}".format(go, l))
        except ValueError:
            logging.debug("error decoding json")
    return gos


def get_uniprot(term):
    payload = {'query': term + " AND reviewed:yes", 'format': 'json', "sort": "score"}
    headers = {'user-agent': 'iice.fc.ul.pt/3.0 alamurias@lasige.fc.ul.pt'}
    try:
        r = requests.get("http://www.uniprot.org/uniprot/", params=payload, headers=headers)
    except requests.exceptions.ConnectionError:
        return None
    if r.text != "" and r.status_code != 400:
        try:
            res = r.json()
            return res[0]["id"]
        except ValueError:
            logging.debug("error decoding json")
    return None

def find_go_term(term):
    ''' returns tuple (chebiID, chebiTerm, score)
        if resolution fails, return ('0', 'null', 0.0)
    '''
    # print "TERM", term
    term = MySQLdb.escape_string(term)
    # adjust - adjust the final score
    match = ()
    cur = db.cursor()
    # cur.execute("SET NAMES utf8")
    # check for exact match
    logging.debug("exact match")
    query = """SELECT distinct acc, a.name
                   FROM term a 
                   WHERE name = %s and LENGTH(a.name)>0 and is_obsolete=0 ORDER BY a.ic DESC;"""
    # print "QUERY", query
    cur.execute(query, (term,))

    res = cur.fetchone()
    if res is not None:
        # print "1"
        score = 1.0
        match = (str(res[0]), res[1], score)
        method[0] += 1
    else:
        # synonyms
        logging.debug("synonym exact match")
        cur.execute("""SELECT b.acc, a.term_synonym, b.name
                       FROM term_synonym a, term b
                       WHERE a.term_synonym = %s
                        and b.id=a.term_id
                        and LENGTH(a.term_synonym)>0
                        and is_obsolete=0 ORDER BY b.ic DESC;""", (term,))
        res = cur.fetchone()
        if res is not None:
            # print "2"
            score = 0.9
            match = (str(res[0]), res[2], score)
            method[1] += 1

        else:
            # plural - tb pode ser recursivo
            if len(term) > 0 and term[-1] == 's':
                logging.debug("trying plural - {}...".format(term))
                match = find_go_term(term[:-1])

    if not match:
        logging.debug("partial match")
        query = """SELECT distinct acc, name
               FROM term a
               WHERE name LIKE %s and LENGTH(a.name)>0 and is_obsolete=0 ORDER BY a.ic DESC;"""
        # print "QUERY", query
        cur.execute(query, ("%" + term.decode("latin1") + "%",))

        res = cur.fetchone()
        if res is not None:
            # print "1"
            score = 0.8
            match = (str(res[0]), res[1], score)
            method[2] += 1

    if not match:
        logging.debug("partial synonym match")
        cur.execute("""SELECT b.acc, a.term_synonym, b.name
                       FROM term_synonym a, term b
                       WHERE a.term_synonym LIKE %s
                        and b.id=a.term_id
                        and LENGTH(a.term_synonym)>0
                        and is_obsolete=0 ORDER BY b.ic DESC LIMIT 5;""", ("%" + term.decode("latin") + "%",))
        res = cur.fetchone()
        if res is not None:
            # print "2"
            score = 0.7
            match = (str(res[0]), res[2], score)
            method[3] += 1

    if not match:
        logging.debug("uniprot match")
        uniprot = get_uniprot(term)
        if uniprot is not None:
            logging.debug("got uniprot {}".format(uniprot))
            gos = get_go_annotations(uniprot)
            # q = """SELECT t.acc, t.name
            #       FROM term as t, prot_GOA_MF as g, prot_acc as a
            #      WHERE a.acc = %s and a.prot_id = g.prot_id and g.term_id = t.id and g.is_redundant = 0
            #      ORDER BY t.ic DESC;
            #       """
            q = """SELECT t.acc, t.name
                   FROM term t
                   WHERE FIND_IN_SET(t.acc, %s)
                   ORDER BY t.ic DESC
                """
            #res = query_with_timeout(cur, 120, q, (','.join(gos),))
            cur.execute(q, (','.join(gos),))
            res = cur.fetchone()
            if res is not None:
                score = 0.6
                match = (str(res[0]), res[1], score)
                method[4] += 1
    '''if not match:
        logging.debug("term definition match")
        q = """SELECT b.acc, b.name
                       FROM term_definition a, term b
                       WHERE a.term_definition LIKE %s
                        and b.id LIKE a.term_id
                        and is_obsolete=0 ORDER BY b.ic DESC;"""
        #cur.execute(q, ("%" + term.decode("latin") + "%",))
        res = query_with_timeout(cur, 60, q, ("%" + term.decode("latin") + "%",))
        # res = cur.fetchone()
        if res is not None:
            score = 0.5
            match = (str(res[0]), res[1], score)
            method[5] += 1'''

    '''if not match and (' ' in term.decode("utf8") or '-' in term.decode("utf8")):
        termslist = term.decode("utf8").split(" ")
        termslist = [t.split("-") for t in termslist]
        termslist = [t for sublist in termslist for t in sublist]
        termslist = [t for t in termslist if len(t) > 3]
        logging.debug(termslist)
        if len(termslist) > 1:
            logging.debug("split term match")
            bestres = ('0', 'null', 0.0)
            for t in termslist:
                res = find_go_term(t.encode("utf8"))
                if res[2] > bestres[2]:
                    bestres = res
            if res[2] > 0:
                method[6] += 1
                match = res'''

    if not match or match[2] < 0.0:
        match = ('0', 'null', 0.0)

    return match

def find_go_term3(term):
    global go
    # first check if a chebi mappings dictionary is loaded in memory
    if term in go:
        c = go[term]
        # chebi mappings are not loaded, or this text is not mapped yet, so update chebi dictionary
    else:
        try:
            c = find_go_term(term)
            go[term] = c
            logging.info("mapped %s to %s", term.decode("utf8"), c)
        except UnicodeDecodeError or UnicodeEncodeError:
            logging.debug("UnicodeError error mapping")
            c = ('0', 'null', 0.0)

    return c


def exit_handler():
    print method
    print 'Saving GO dictionary...!'
    pickle.dump(go, open(godic, "wb"))

atexit.register(exit_handler)


def get_description(id):
    cur = db.cursor()
    query = """SELECT term_definition
           FROM term_definition as d, term as t
           WHERE t.acc = %s and t.id == d.term_id""" % id
    cur.execute(query)
    res = cur.fetchone()

    if res is not None:
        return res[0]
    else:
        return "NA"


def load_synonyms():
    syns = []
    cur = db.cursor()
    query = """SELECT id, name
           FROM term """
    cur.execute(query)
    ids = cur.fetchall()
    for i in ids:
        print "getting synonyms for" + i[1].lower() + '(' + str(i[0]) + ')',
        synset = set()
        synset.add(i[1].lower())
        query = """SELECT term_synonym
           FROM term_synonym
           WHERE term_id = %s""" % i[0]
        cur.execute(query)
        names = cur.fetchall()
        print len(names)
        for name in names:
            #print name[0], 
            synset.add(name[0].lower())
        syns.append(synset)
    pickle.dump(syns, open("data/go_synonyms.pickle", 'wb'))
    print "done"


def check_dist_between(cid1, cid2):
    cur = db.cursor()
    query = """SELECT distance 
               FROM graph_path 
               WHERE term1_id = %s and term2_id = %s""" % (cid1, cid2)
    cur.execute(query)
    res = cur.fetchone()
    if res is None:
        dist = -1
    else:
        dist = int(res[0])
    return dist


def main():
    ''' test resolution method by trying with every CEM on CHEMDNER gold standard
        returns '' if resolution fails
    '''
    parser = OptionParser(usage='Perform GO resoltion')
    parser.add_option("-f", "--file", dest="file",  action="store", default="chebi_dic.pickle",
                      help="Pickle file to load/store the data")
    parser.add_option("-d", "--dir", action="store", dest="dir", type="string", default=".",
                      help="Corpus directory with chebi mappings to measure SSM between pairs (CHEMDNER format)")
    parser.add_option("--reload", action="store_true", default=False, dest="reload",
                      help="Reload pickle data")
    parser.add_option(
        "--log", action="store", dest="loglevel", type="string", default="WARNING",
        help="Log level")
    parser.add_option(
        "--logfile", action="store", dest="logfile", type="string", default="kernel.log",
        help="Log file")
    parser.add_option("--text", action="store", dest="text", type="string", default="water",
                      help="Text to map to ChEBI")
    parser.add_option(
        "--datatype", action="store", dest="type", type="string", default="chemdner",
        help="Data type to test (chemdner, patents or ddi)")
    parser.add_option("--action", action="store", dest="action", type="string", default="map",
                      help="test, batch, info, map, chebi2go")
    (options, args) = parser.parse_args()
    numeric_level = getattr(logging, options.loglevel.upper(), None)
    #if not isinstance(numeric_level, int):
    #    raise ValueError('Invalid log level: %s' % loglevel)

    while len(logging.root.handlers) > 0:
        logging.root.removeHandler(logging.root.handlers[-1])
    logging.basicConfig(level=numeric_level, format='%(asctime)s %(levelname)s %(message)s')

    if options.action == "test":
        chemlist = {}
        if options.type == 'chemdner':
            with open("CHEMDNER/CHEMDNER_DEV_TRAIN_V02/chemdner_ann.txt", 'r') as chems:
                for line in chems:
                    tsv = line.strip().split('\t')
                    if tsv[5] not in chemlist:
                        chemlist[tsv[5]] = []
                    chemlist[tsv[5]].append((tsv[4]))

        elif options.type == 'patents':
            for f in os.listdir("patents_corpus/PatentsGoldStandardEnriched"):
                tree = ET.parse("patents_corpus/PatentsGoldStandardEnriched/" + f)
                root = tree.getroot()
                for chem in re.findall('.//ne'):
                    type = chem.get('type')
                    if type not in chemlist:
                        chemlist[type] = []
                    if chem.get("chebi-id") != '':
                        chemlist[type].append(
                            (chem.get("name"), chem.get("chebi-id").split(':')[1]))

        for type in chemlist:
            i = 0
            count = 0
            errors = 0
            print type
            sys.stdout.flush()
            for chem in chemlist[type]:
                count += 1
                res = find_go_term(chem[0], 0)
                if res[1] == 'null':
                    i += 1
                elif len(chem) > 1:
                    if chem[1] != res[0]:
                        errors += 1
            print type + " nulls: " + str(i) + ' errors:' + str(errors) + ' total:' + str(count)
    elif options.action == "map":
        print find_go_term(options.text)
    elif options.action == "synonyms":
        load_synonyms()

if __name__ == "__main__":
    main()
