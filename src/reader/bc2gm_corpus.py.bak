import codecs
import logging
import os
import sys

import itertools
import progressbar as pb
import time

import re

from text.corpus import Corpus
from text.document import Document
from text.sentence import Sentence


class BC2GMCorpus(Corpus):
    """

    """
    def __init__(self, corpusdir, **kwargs):
        super(BC2GMCorpus, self).__init__(corpusdir, **kwargs)

    def load_corpus(self, corenlpserver, process=True):
        total_lines = sum(1 for line in open(self.path))
        widgets = [pb.Percentage(), ' ', pb.Bar(), ' ', pb.AdaptiveETA(), ' ', pb.Timer()]
        pbar = pb.ProgressBar(widgets=widgets, maxval=total_lines, redirect_stdout=True).start()
        time_per_abs = []
        with codecs.open(self.path, 'r', "utf-8") as trainfile:
            current = 0
            for line in trainfile:
                #logging.debug('%s:%s/%s', f, current + 1, total)
                x = line.strip().split(" ")
                did = x[0]
                doctext = " ".join(x[1:])
                newdoc = Document(doctext, process=False, did=did)
                #newdoc.sentence_tokenize("biomedical")
                sid = did + ".s0"
                newdoc.sentences.append(Sentence(doctext, offset=0, sid=sid, did=did))
                if process:
                    newdoc.process_document(corenlpserver, "biomedical")
                self.documents[newdoc.did] = newdoc
                # abs_time = time.time() - t
                # time_per_abs.append(abs_time)
                #logging.info("%s sentences, %ss processing time" % (len(newdoc.sentences), abs_time))
                pbar.update(current+1)
                current += 1
        pbar.finish()
        # abs_avg = sum(time_per_abs)*1.0/len(time_per_abs)
        # logging.info("average time per abstract: %ss" % abs_avg)

    def load_annotations(self, ann_dir, etype, pairtype="all"):
        pmids = []
        pmid_regex = re.compile(r"(P)(\d+)(\D)")
        tagged = 0
        not_tagged = 0
        logging.info("loading annotations file...")
        with codecs.open(ann_dir, 'r', "utf-8") as inputfile:
            for line in inputfile:
                # logging.info("processing annotation %s/%s" % (n_lines, total_lines))
                did, offset, text = line.strip().split('|')
                # P00064414A1098
                #print did
                pmid = pmid_regex.match(did)
                pmid = str(int(pmid.group(2)))
                #pmid = str(int(did[5:]))
                pmids.append(pmid)
                start, end = offset.split(" ")
                start, end = int(start), int(end)
                # pmid = "PMID" + pmid
                if did in self.documents:
                    sentence = self.documents[did].find_sentence_containing(start, end, chemdner=False)
                    sentence_space_offsets = {} # number of spaces until each char in this sentence
                    current_spaces = 0
                    # store how many spaces until a given char index, where the index does not account for spaces
                    # used to match the GENETAG notation to the more normal notation used by IBEnt where the spaces are
                    # accounted for
                    for ic, char in enumerate(sentence.text):
                        if char.isspace():
                            current_spaces += 1
                            continue
                        sentence_space_offsets[ic-current_spaces] = current_spaces

                    if sentence is not None:
                        # "IMPORTANT: The start and end offsets do not count white space characters."
                        #space_offset = sentence.text[:start].count(" ")
                        #space_offset = sentence.text[:start + space_offset+1].count(" ")
                        #end_space_offset = sentence.text[:end].count(" ")
                        #end_space_offset = sentence.text[:end + end_space_offset + 1].count(" ")
                        # print start, sentence.offset, space_offset, sentence.text[:start+space_offset+1]
                        start_offset = start - sentence.offset #+ sentence.text[:start+space_offset+1].count(" ")
                        start_offset += sentence_space_offsets[start_offset]
                        end_offset = end - sentence.offset # +  sentence.text[:end+end_space_offset+1].count(" ")
                        # + 1 because this corpus considers the last index to be part of the entity
                        end_offset += sentence_space_offsets[end_offset] + 1
                        eid = sentence.tag_entity(start_offset, end_offset,
                                                  "protein", text=text)
                        if eid is None:
                            not_tagged += 1
                            print sentence.sid, text, start, end, sentence.offset, sentence_space_offsets
                        else:
                            tagged += 1
                    else:
                        print "could not find sentence for this span: {}-{}".format(start, end)
                else:
                    logging.info("%s not found!" % did)
        print "tagged: {} not tagged: {}".format(tagged, not_tagged)
        with codecs.open(ann_dir + "-pmids.txt", 'w', "utf-8") as pmid_list:
            pmid_list.write("\n".join(pmids) + "\n")


def get_b2gm_gold_ann_set(goldann, text_path):
    gold_offsets = set()
    sentences = {}
    with open(text_path, "r") as textfile:
        for line in textfile:
            x = line.strip().split(" ")
            sentences[x[0]] = " ".join(x[1:])

    logging.info("loading annotations file...")
    with codecs.open(goldann, 'r', "utf-8") as inputfile:
        for line in inputfile:
            # logging.info("processing annotation %s/%s" % (n_lines, total_lines))
            did, offset, text = line.strip().split('|')
            start, end = offset.split(" ")
            start, end = int(start), int(end)
            sentence_text = sentences[did]
            sentence_space_offsets = {}  # number of spaces until each char in this sentence
            current_spaces = 0
            for ic, char in enumerate(sentence_text):
                if char.isspace():
                    current_spaces += 1
                    continue
                sentence_space_offsets[ic - current_spaces] = current_spaces
            # pmid = "PMID" + pmid
            # "IMPORTANT: The start and end offsets do not count white space characters."
            #space_offset = sentence_text[:start].count(" ")
            #space_offset = sentence_text[:start + space_offset + 1].count(" ")
            #end_space_offset = sentence_text[:end].count(" ")
            #end_space_offset = sentence_text[:end + end_space_offset + 1].count(" ")
            # print start, sentence.offset, space_offset, sentence.text[:start+space_offset+1]
            start_offset = start + sentence_space_offsets[start] # sentence_text[:start + space_offset + 1].count(" ")
            end_offset = end + sentence_space_offsets[end] # + sentence_text[:end + end_space_offset + 1].count(" ")
            gold_offsets.add((did, start_offset, end_offset + 1, text))
    return gold_offsets, None







