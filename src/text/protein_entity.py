from __future__ import unicode_literals
import atexit
import logging
import pickle
import re
import MySQLdb
import sys
import os

import requests

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '../..'))
from config.config import use_go
if use_go:
    from config.config import go_conn as db
from config import config
from text.entity import Entity
from text.token2 import Token2

__author__ = 'Andre'
prot_words = set()
prot_stopwords = set(["chromosome", "factor", "conserved", "gene", "anti", "mir", "regulatory", "terminal", "element",
                      "activator", "cell", "box", "transcriptional", "transcription", "growth", "talk", "epithelial",
                      "alpha", "microrna", "micrornas", "chip", "chipseq", "interferons", "tweak", "allele", "mirnas",
                      "mirs", "protein", "proteins", "hsa", "genotype", "mRNA"])
# words that may seem like they are not part of named chemical entities but they are

# words that are never part of chemical entities
with open(config.stoplist, 'r') as stopfile:
    for l in stopfile:
        w = l.strip().lower()
        if w not in prot_words and len(w) > 1:
            prot_stopwords.add(w)

uniprotdic = "data/uniprot_dic.pickle"

if os.path.isfile(uniprotdic):
    logging.info("loading uniprot cache...")
    uniprot = pickle.load(open(uniprotdic, "rb"))
    loadeduniprot = True
    logging.info("loaded uniprot dictionary with %s entries", str(len(uniprot)))
else:
    uniprot = {}
    loadeduniprot = False
    logging.info("new uniprot dictionary")

def exit_handler():
    logging.info('Saving uniprot cache...!')
    pickle.dump(uniprot, open(uniprotdic, "wb"))

atexit.register(exit_handler)


def get_uniprot_name(text):
    global uniprot
    # first check if a chebi mappings dictionary is loaded in memory
    if text in uniprot:
        c = uniprot[text]
    else:
        query = {"query": text + ' AND organism:9606',
                 "sort": "score",
                 "columns": "id,entry name,reviewed,protein names,organism,go,go-id",
                 "format": "tab",
                 "limit": "1"}
        headers = {'User-Agent': 'IBEnt (CentOS) alamurias@lasige.di.fc.ul.pt'}
        r = requests.get('http://www.uniprot.org/uniprot/', query, headers=headers)
        # logging.debug("Request Status: " + str(r.status_code))

        c = r.text
        if "\n" not in c:
            logging.info("nothing found on uniprot for {}".format(text))
            c = text + "\t0\t" + "NA\t" * 4
        else:
            c = c.split("\n")[1].strip()
            uniprot[text] = c
    values = c.split("\t")
    normalized = text.strip()
    normalized_score = 0
    go_ids = []
    if len(values) > 3:

        # print
        # print self.text, values[0], values[1]
        # print values[3]
        normalized = values[0]
        normalized_score = 100

        if len(values) > 5:
            # gos = values[5].split(";")
            # print values[6]
            go_ids = [v.strip() for v in values[6].split(";")]
    #logging.info("mapped  {} to {}".format(text, normalized))
    return normalized, normalized_score, go_ids

class ProteinEntity(Entity):
    def __init__(self, tokens, sid, *args, **kwargs):
        # Entity.__init__(self, kwargs)
        super(ProteinEntity, self).__init__(tokens, *args, **kwargs)
        self.type = "protein"
        self.subtype = kwargs.get("subtype")
        self.sid = sid
        self.go_ids = []
        self.best_go = None
        # self.normalize()

    tf_regex = re.compile(r"\A[A-Z]+\d*\w*\d*\Z")

    def get_dic(self):
        dic = super(ProteinEntity, self).get_dic()
        dic["subtype"] = self.subtype
        dic["ssm_score"] = self.ssm_score
        dic["ssm_entity"] = self.ssm_go_ID
        return dic

    def validate(self, ths, rules, *args, **kwargs):
        """
        Use rules to validate if the entity was correctly identified
        :param rules:
        :return: True if entity does not fall into any of the rules, False if it does
        """
        self.normalize()
        final_entities = [self]
        if "ssm" in ths and self.ssm_score < ths["ssm"]:
            logging.info("excluded {} because of ssm ({}<{})".format(self.text, str(self.ssm_score), str(ths["ssm"])))
            return False
        if "stopwords" in rules:
            words = re.split(' |-', self.text)
            # words += self.text.split("-")
            stop = False
            for s in prot_stopwords:
                if any([s == w.lower() for w in words]):
                    logging.debug("ignored stopword %s" % self.text)
                    stop = True
            if stop:
                return False
            elif self.text.startswith("let-") or self.text.startswith("miR-") or self.text.startswith("micro") or \
                    self.text.startswith("miRNAs") or  self.text.startswith("mir-") or  self.text.startswith("Mir"):
                return False
        if "alpha" in rules and not self.text[0].isalpha():
            logging.debug("not alpha %s" % self.text)
            return False
        if "nwords" in rules:
            words = self.text.split(" ")
            if len(words) > 1:
                return False
        if "codeonly" in rules:
            if self.tf_regex.match(self.text) is None:
                return False
        if "fixdash" in rules:
            self.text = self.text.replace("-", "")
        if "uniprot" in rules:
            if self.normalized_score <= 0:
                logging.info("excluded {} because of uniprot".format(self.text))
                return False
        return final_entities

    def normalize_entrez(self):
        global ncbigene
        if self.text in uniprot:
            c = uniprot[self.text]
        else:
            query = {"term": self.text,
                     "db": "gene"}
            headers = {'User-Agent': 'IBEnt (CentOS) alamurias@lasige.di.fc.ul.pt'}
            r = requests.get('http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?', query, headers=headers)
            logging.debug("Request Status: " + str(r.status_code))

    def normalize(self):
        if self.text.lower() in ("hsa", "mir", "99b", "pre"):
            self.normalized = self.text
            self.normalized_score = 0
            self.normalized_ref = "text"
            return
        uniprot_values = get_uniprot_name(self.text)

        self.normalized = uniprot_values[0]
        self.normalized_score = uniprot_values[1]
        self.normalized_ref = "uniprot"

        self.go_ids = uniprot_values[2]
        # self.normalized = self.text
        # self.normalized_score = 0
        if uniprot_values[1] < 100:
            self.normalized_ref = "text"
            self.normalized = self.text
            self.normalized_score = 0
        # if len(self.go_ids) > 0:
        #     self.get_best_go()
        # else:
        #     logging.info("NO GO for {}".format(self.text))
        #     self.best_go = ""


    def get_best_go(self):
        cur = db.cursor()
        # synonym

        query = """SELECT DISTINCT t.acc, t.name, t.ic
                       FROM term t
                       WHERE t.acc IN (%s)
                       ORDER BY t.ic ASC
                       LIMIT 1;""" # or DESC
            # print "QUERY", query


        format_strings = ','.join(['%s'] * len(self.go_ids))
        cur.execute(query % format_strings, (self.go_ids))
        res = cur.fetchone()
        if res is not None:
            # print self.text, res[1:]
            logging.info("best GO for {}: {}".format(self.text, " ".join([str(r) for r in res])))
            self.best_go = res[0]
        else:
            logging.info("NO GO for {}".format(self.text))
            self.best_go = ""

    # def normalize(self):
    #     term = MySQLdb.escape_string(self.text)
    #     # adjust - adjust the final score
    #     match = ()
    #     cur = db.cursor()
    #     # synonym
    #     query = """SELECT DISTINCT t.acc, t.name, s.term_synonym
    #                    FROM term t, term_synonym s
    #                    WHERE s.term_synonym LIKE %s and s.term_id = t.id
    #                    ORDER BY t.ic ASC
    #                    LIMIT 1;""" # or DESC
    #         # print "QUERY", query
    #
    #     cur.execute(query, ("%" + term + "%",))
    #
    #     res = cur.fetchone()
    #     if res is not None:
    #         print res
    #     else:
    #         query = """SELECT DISTINCT t.acc, t.name, p.name
    #                    FROM term t, prot p, prot_GOA_BP a
    #                    WHERE p.name LIKE %s and p.id = a.prot_id and a.term_id = t.id
    #                    ORDER BY t.ic ASC
    #                    LIMIT 1;""" # or DESC
    #         cur.execute(query, (term,))
    #         res = cur.fetchone()
    #         print res

# token = Token2("IL-2")
# token.start, token.dstart, token.end, token.dend = 0,0,0,0
# p = ProteinEntity([token], "", text=sys.argv[1])
# p.normalize()
