import codecs
import time
import sys
import logging

from text.corpus import Corpus
from text.document import Document


class ChemdnerCorpus(Corpus):
    """Chemdner corpus from BioCreative IV and V"""
    def __init__(self, corpusdir, **kwargs):
        super(ChemdnerCorpus, self).__init__(corpusdir, **kwargs)
        self.subtypes = ["IDENTIFIER", "MULTIPLE", "FAMILY", "FORMULA", "SYSTEMATIC", "ABBREVIATION", "TRIVIAL"]

    def progress(self, count, total, suffix=''):
        #TODO: generalize to other corpus
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '=' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))

    def load_corpus(self, corenlpserver, process=True):
        """Load the CHEMDNER corpus file on the dir element"""
        # open filename and parse lines
        total_lines = sum(1 for line in open(self.path))
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
                logging.info("processing " + newdoc.did + ": " + str(n_lines) + "/" + str(total_lines))
                newdoc.sentence_tokenize("biomedical")
                if process:
                    newdoc.process_document(corenlpserver, "biomedical")
                self.documents[newdoc.did] = newdoc
                n_lines += 1

                #percent = (n_lines*100)/total_lines
                actual = str(n_lines)+"/"+str(total_lines)
                #print '\r[{0}] {1}% - {2}'.format('|'*(percent), percent,actual)
                self.progress(n_lines,total_lines, actual)


                abs_time = time.time() - t
                time_per_abs.append(abs_time)
                logging.info("%s sentences, %ss processing time" % (len(newdoc.sentences), abs_time))
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