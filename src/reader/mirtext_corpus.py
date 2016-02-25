import logging
import xml.etree.ElementTree as ET
import os
import sys
import progressbar as pb
import time

from text.corpus import Corpus
from text.document import Document
from text.sentence import Sentence

type_match = {"MiRNA": "mirna",
              "Gene": "protein"}
class MirtexCorpus(Corpus):
    """
    DDI corpus used for NER and RE on the SemEval DDI tasks of 2011 and 2013.
    self.path is the base directory of the files of this corpus.
    Each file is a document, DDI XML format, sentences already separated.
    """
    def __init__(self, corpusdir, **kwargs):
        super(MirtexCorpus, self).__init__(corpusdir, **kwargs)
        self.subtypes = []

    def load_corpus(self, corenlpserver, process=True):
        # self.path is the base directory of the files of this corpus
        trainfiles = [self.path + '/' + f for f in os.listdir(self.path) if f.endswith('.txt')]
        total = len(trainfiles)
        widgets = [pb.Percentage(), ' ', pb.Bar(), ' ', pb.AdaptiveETA(), ' ', pb.Timer()]
        pbar = pb.ProgressBar(widgets=widgets, maxval=total, redirect_stdout=True).start()
        time_per_abs = []
        for current, f in enumerate(trainfiles):
            #logging.debug('%s:%s/%s', f, current + 1, total)
            print '{}:{}/{}'.format(f, current + 1, total)
            did = f.split(".")[0]
            t = time.time()
            with open(f, 'r') as txt:
                doctext = txt.read()
            newdoc = Document(doctext, process=False, did=did)
            newdoc.sentence_tokenize("biomedical")
            if process:
                newdoc.process_document(corenlpserver, "biomedical")
            self.documents[newdoc.did] = newdoc
            abs_time = time.time() - t
            time_per_abs.append(abs_time)
            #logging.info("%s sentences, %ss processing time" % (len(newdoc.sentences), abs_time))
            pbar.update(current+1)
        pbar.finish()
        abs_avg = sum(time_per_abs)*1.0/len(time_per_abs)
        logging.info("average time per abstract: %ss" % abs_avg)

    def load_annotations(self, ann_dir, etype):
        annfiles = [ann_dir + '/' + f for f in os.listdir(ann_dir) if f.endswith('.ann')]
        total = len(annfiles)
        time_per_abs = []
        for current, f in enumerate(annfiles):
            logging.debug('%s:%s/%s', f, current + 1, total)
            did = f.split(".")[0]
            with open(f, 'r') as txt:
                for line in txt:
                    # print line
                    if line.startswith("T"):
                        tid, ann, etext = line.strip().split("\t")
                        entity_type, dstart, dend = ann.split(" ")
                        if etype == "all" or (etype != "all" and etype == type_match[entity_type]):
                            dstart, dend = int(dstart), int(dend)
                            sentence = self.documents[did].find_sentence_containing(dstart, dend, chemdner=False)
                            if sentence is not None:
                                # e[0] and e[1] are relative to the document, so subtract sentence offset
                                start = dstart - sentence.offset
                                end = dend - sentence.offset
                                sentence.tag_entity(start, end, type_match[entity_type], text=etext)
                            else:
                                print "could not find sentence for this span: {}-{}".format(dstart, dend)
        self.evaluate_normalization()


def get_mirtex_gold_ann_set(goldpath, entitytype):
    logging.info("loading gold standard... {}".format(goldpath))
    annfiles = [goldpath + '/' + f for f in os.listdir(goldpath) if f.endswith('.ann')]
    gold_offsets = set()
    for current, f in enumerate(annfiles):
            did = f.split(".")[0]
            with open(f, 'r') as txt:
                for line in txt:
                    if line.startswith("T"):
                        tid, ann, etext = line.strip().split("\t")
                        etype, dstart, dend = ann.split(" ")
                        if entitytype == type_match[etype]:
                            dstart, dend = int(dstart), int(dend)
                            gold_offsets.add((did, dstart, dend, etext))
    return gold_offsets