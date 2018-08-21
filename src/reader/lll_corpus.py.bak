import codecs
import logging
import os
import sys

import itertools
import progressbar as pb
import time

from text.corpus import Corpus
from text.document import Document
from text.sentence import Sentence


class LLLCorpus(Corpus):
    """

    """
    def __init__(self, corpusdir, **kwargs):
        super(LLLCorpus, self).__init__(corpusdir, **kwargs)
        self.pmid_list = []

    def load_corpus(self, corenlpserver, process=True):
        total_lines = sum(1 for line in open(self.path))
        time_per_abs = []
        with codecs.open(self.path, 'r', "utf-8") as trainfile:
            current = 0
            ddi = ""
            for line in trainfile:
                #logging.debug('%s:%s/%s', f, current + 1, total)
                if line.startswith("ID"):
                    did = line.strip().split("\t")[1]
                    print did
                elif line.startswith("sentence"):
                    doctext = line.strip().split("\t")[1]
                    newdoc = Document(doctext, process=False, did=did)
                    sid = did + ".s0"
                    newdoc.sentences.append(Sentence(doctext, offset=0, sid=sid, did=did))
                    if process:
                        newdoc.process_document(corenlpserver)
                    self.documents[newdoc.did] = newdoc
                    # abs_time = time.time() - t
                    # time_per_abs.append(abs_time)
                    #logging.info("%s sentences, %ss processing time" % (len(newdoc.sentences), abs_time))

        # abs_avg = sum(time_per_abs)*1.0/len(time_per_abs)
        # logging.info("average time per abstract: %ss" % abs_avg)

    def load_annotations(self, ann_dir, etype, pairtype="all"):
        pmids = []
        logging.info("loading annotations file...")
        with codecs.open(ann_dir, 'r', "utf-8") as trainfile:
            for line in trainfile:
                # logging.debug('%s:%s/%s', f, current + 1, total)
                if line.startswith("ID"):
                    did = line.strip().split("\t")[1]
                    pmid = did.split("-")[0]
                    pmids.append(pmid)
                    sid = did + ".s0"
                    sentence = self.documents[did].sentences[0]
                elif line.startswith("words"):
                    offsets = {}
                    words = line.strip().split("\t")[1:]
                    for w in words:
                        x = w.split(",")
                        wid = int(x[0][5:])
                        wtext = x[1][1:-1]
                        wstart = int(x[-2])
                        wend = int(x[-1][:-1]) + 1
                        offsets[wid] = (wstart, wend, wtext)
                elif line.startswith("agents") or line.startswith("targets"):
                    entities = line.strip().split("\t")[1:]
                    # pmid = "PMID" + pmid
                    for e in entities:
                        wid = int(e.split("(")[1][:-1])
                        # print offsets[wid]
                        start, end, text = offsets[wid] # get agent(6)
                        sentence.tag_entity(start, end, "protein", text=text)
        with codecs.open(ann_dir + "-pmids.txt", 'w', "utf-8") as pmidfile:
            pmidfile.write("\n".join(pmids))








