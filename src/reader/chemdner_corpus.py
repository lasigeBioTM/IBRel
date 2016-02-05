import codecs
import time
import sys
import logging
from operator import itemgetter

import progressbar as pb
from subprocess import check_output

from text.corpus import Corpus
from text.document import Document


class ChemdnerCorpus(Corpus):
    """Chemdner corpus from BioCreative IV and V"""
    def __init__(self, corpusdir, **kwargs):
        super(ChemdnerCorpus, self).__init__(corpusdir, **kwargs)
        self.subtypes = ["IDENTIFIER", "MULTIPLE", "FAMILY", "FORMULA", "SYSTEMATIC", "ABBREVIATION", "TRIVIAL"]

    def load_corpus(self, corenlpserver, process=True):
        """Load the CHEMDNER corpus file on the dir element"""
        # open filename and parse lines
        total_lines = sum(1 for line in open(self.path))
        widgets = [pb.Percentage(), ' ', pb.Bar(), ' ', pb.ETA(), ' ', pb.Timer()]
        pbar = pb.ProgressBar(widgets=widgets, maxval=total_lines).start()
        n_lines = 1
        time_per_abs = []
        with codecs.open(self.path, 'r', "utf-8") as inputfile:
            for line in inputfile:
                t = time.time()
                # each line is PMID  title   abs
                tsv = line.split('\t')
                doctext = tsv[2].strip().replace("<", "(").replace(">", ")")
                newdoc = Document(doctext, process=False,
                                  did=tsv[0], title=tsv[1].strip())
                newdoc.sentence_tokenize("biomedical")
                if process:
                    newdoc.process_document(corenlpserver, "biomedical")
                self.documents[newdoc.did] = newdoc
                n_lines += 1
                abs_time = time.time() - t
                time_per_abs.append(abs_time)
                pbar.update(n_lines+1)
        pbar.finish()
        abs_avg = sum(time_per_abs)*1.0/len(time_per_abs)
        logging.info("average time per abstract: %ss" % abs_avg)

    def load_annotations(self, ann_dir, entitytype="chemical"):
        # total_lines = sum(1 for line in open(ann_dir))
        # n_lines = 1
        logging.info("loading annotations file...")
        with codecs.open(ann_dir, 'r', "utf-8") as inputfile:
            for line in inputfile:
                # logging.info("processing annotation %s/%s" % (n_lines, total_lines))
                pmid, doct, start, end, text, chemt = line.strip().split('\t')
                #pmid = "PMID" + pmid
                if pmid in self.documents:
                    if entitytype == "all" or entitytype == "chemical" or entitytype == chemt:
                        self.documents[pmid].tag_chemdner_entity(int(start), int(end),
                                                             chemt, text=text, doct=doct)
                else:
                    logging.info("%s not found!" % pmid)

def write_chemdner_files(results, models, goldset, ths, rules):
    """ results files for CHEMDNER CEMP and CPD tasks"""
    print "saving results to {}".format(results.path + ".tsv")
    with codecs.open(results.path + ".tsv", 'w', 'utf-8') as outfile:
        cpdlines, max_entities = results.corpus.write_chemdner_results(models, outfile, ths, rules)
    cpdlines = sorted(cpdlines, key=itemgetter(2))
    with open(results.path + "_cpd.tsv", "w") as cpdfile:
        for i, l in enumerate(cpdlines):
            if l[2] == 0:
                cpdfile.write("{}_{}\t0\t{}\t1\n".format(l[0], l[1], i+1))
            else:
                cpdfile.write("{}_{}\t1\t{}\t{}\n".format(l[0], l[1], i+1, l[2]*1.0/max_entities))

def run_chemdner_evaluation(goldstd, results, format=""):
    """
    Use the official BioCreative evaluation script (should be installed in the system)
    :param goldstd: Gold standard file path
    :param results: Results file path
    :param: format option
    :return: Output of the evaluation script
    """
    # TODO: copy to chemdner_corpus.py
    cem_command = ["bc-evaluate", results, goldstd]
    if format != "":
        cem_command = cem_command[:1] + [format] + cem_command[1:]
    r = check_output(cem_command)
    return r


def get_chemdner_gold_ann_set(goldann="CHEMDNER/CHEMDNER_TEST_ANNOTATION/chemdner_ann_test_13-09-13.txt"):
    """
    Load the CHEMDNER annotations to a set
    :param goldann: Path to CHEMDNER annotation file
    :return: Set of gold standard annotations
    """
    # TODO: copy to chemdner:corpus
    with codecs.open(goldann, 'r', 'utf-8') as goldfile:
            gold = goldfile.readlines()
    goldlist = []
    for line in gold:
        #pmid, T/A, start, end
        x = line.strip().split('\t')
        goldlist.append((x[0], x[1] + ":" + x[2] + ":" + x[3], '1'))
    #print goldlist[0:2]
    goldset = set(goldlist)
    return goldset