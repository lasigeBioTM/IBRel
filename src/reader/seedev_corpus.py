import argparse
import codecs
import logging
import pickle
import xml.etree.ElementTree as ET
import os
import sys

import itertools
import progressbar as pb
import time

from pycorenlp import StanfordCoreNLP

from classification.rext.jsrekernel import JSREKernel
from classification.rext.multir import MultiR
from classification.rext.rules import RuleClassifier
from classification.rext.scikitre import ScikitRE
from classification.rext.stanfordre import StanfordRE
from classification.rext.svmtk import SVMTKernel
from config import config
from text.corpus import Corpus
from text.document import Document
from text.sentence import Sentence



class SeeDevCorpus(Corpus):
    """
    Corpus for the BioNLP SeeDev task
    self.path is the base directory of the files of this corpus.
    """
    def __init__(self, corpusdir, **kwargs):
        super(SeeDevCorpus, self).__init__(corpusdir, **kwargs)
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
            did = f.split(".")[0].split("/")[-1]
            t = time.time()
            with codecs.open(f, 'r', 'utf-8') as txt:
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

    def load_annotations(self, ann_dir, etype, pairtype="all"):
        annfiles = [ann_dir + '/' + f for f in os.listdir(ann_dir) if f.endswith('.a1')]
        total = len(annfiles)
        time_per_abs = []
        originalid_to_eid = {}
        for current, f in enumerate(annfiles):
            logging.debug('%s:%s/%s', f, current + 1, total)
            did = f.split(".")[0].split("/")[-1]
            with codecs.open(f, 'r', 'utf-8') as txt:
                for line in txt:
                    # print line
                    tid, ann, etext = line.strip().split("\t")
                    if ";" in ann:
                        print "multiple offsets:", ann
                        continue
                    entity_type, dstart, dend = ann.split(" ")
                    # load all entities
                    #if etype == "all" or (etype != "all" and etype == type_match[entity_type]):
                    dstart, dend = int(dstart), int(dend)
                    sentence = self.documents[did].find_sentence_containing(dstart, dend, chemdner=False)
                    if sentence is not None:
                        # e[0] and e[1] are relative to the document, so subtract sentence offset
                        start = dstart - sentence.offset
                        end = dend - sentence.offset
                        eid = sentence.tag_entity(start, end, entity_type, text=etext, original_id=tid)
                        originalid_to_eid[did + "." + tid] = eid
                    else:
                        print "{}: could not find sentence for this span: {}-{}|{}".format(did, dstart, dend, etext.encode("utf-8"))

        annfiles = [ann_dir + '/' + f for f in os.listdir(ann_dir) if f.endswith('.a2')]
        total = len(annfiles)
        time_per_abs = []
        for current, f in enumerate(annfiles):
            logging.debug('%s:%s/%s', f, current + 1, total)
            did = f.split(".")[0].split("/")[-1]
            with codecs.open(f, 'r', 'utf-8') as txt:
                for line in txt:
                    eid, ann = line.strip().split("\t")
                    etype, sourceid, targetid = ann.split(" ")
                    sourceid = did + "." + sourceid.split(":")[-1]
                    targetid = did + "." + targetid.split(":")[-1]
                    if sourceid not in originalid_to_eid or targetid not in originalid_to_eid:
                        print "{}: entity not found: {}=>{}".format(did, sourceid, targetid)
                        print "skipped relation {}".format(etype)
                        continue
                    sourceid, targetid = originalid_to_eid[sourceid], originalid_to_eid[targetid]
                    sid1 = '.'.join(sourceid.split(".")[:-1])
                    sid2 = '.'.join(targetid.split(".")[:-1])
                    #if sid1 != sid2:
                    #    print "relation {} between entities on different sentences: {}=>{}".format(etype, sourceid, targetid)
                    #    continue
                    sentence1 = self.documents[did].get_sentence(sid1)
                    if sentence1 is None:
                        print did, sid1, sourceid, targetid, len(self.documents[did].sentences)
                        continue
                    else:
                        entity1 = sentence1.entities.get_entity(sourceid)
                        entity1.targets.append((targetid, etype))
                        print "{}: {}=>{}".format(etype, entity1.text.encode("utf-8"), targetid)



def get_seedev_gold_ann_set(goldpath, entitytype, pairtype):
    logging.info("loading gold standard annotations... {}".format(goldpath))
    annfiles = [goldpath + '/' + f for f in os.listdir(goldpath) if f.endswith('.a1')]
    gold_offsets = set()
    tid_to_offsets = {}
    for current, f in enumerate(annfiles):
            did = f.split(".")[0]
            with open(f, 'r') as txt:
                for line in txt:
                    tid, ann, etext = line.strip().split("\t")
                    etype, dstart, dend = ann.split(" ")
                    dstart, dend = int(dstart), int(dend)
                    tid_to_offsets[tid] = (did, dstart, dend, etext)
    gold_relations = set()
    annfiles = [goldpath + '/' + f for f in os.listdir(goldpath) if f.endswith('.a2')]
    for current, f in enumerate(annfiles):
            did = f.split(".")[0]
            with open(f, 'r') as txt:
                for line in txt:
                    eid, ann = line.strip().split("\t")
                    etype, sourceid, targetid = ann.split(" ")
                    sourceid = sourceid.split(":")[-1]
                    targetid = targetid.split(":")[-1]
                    source = tid_to_offsets[sourceid]
                    target = tid_to_offsets[targetid]
                    gold_relations.add((did, source, target))
    return gold_offsets, gold_relations

