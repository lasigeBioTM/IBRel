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

        logging.info("loading annotations file...")
        with codecs.open(ann_dir, 'r', "utf-8") as inputfile:
            for line in inputfile:
                # logging.info("processing annotation %s/%s" % (n_lines, total_lines))
                did, offset, text = line.strip().split('|')
                start, end = offset.split(" ")
                start, end = int(start), int(end) + 1
                # pmid = "PMID" + pmid
                if did in self.documents:
                    sentence = self.documents[did].find_sentence_containing(start, end, chemdner=False)
                    if sentence is not None:
                        # "IMPORTANT: The start and end offsets do not count white space characters."
                        space_offset = sentence.text[:start].count(" ")
                        space_offset = sentence.text[:start + space_offset+1].count(" ")
                        end_space_offset = sentence.text[:end].count(" ")
                        end_space_offset = sentence.text[:end + end_space_offset + 1].count(" ")
                        # print start, sentence.offset, space_offset, sentence.text[:start+space_offset+1]
                        start_offset = start - sentence.offset + sentence.text[:start+space_offset+1].count(" ")
                        end_offset = end - sentence.offset + sentence.text[:end+end_space_offset+1].count(" ")
                        sentence.tag_entity(start_offset, end_offset,
                                            "protein", text=text)
                    else:
                        print "could not find sentence for this span: {}-{}".format(start, end)
                else:
                    logging.info("%s not found!" % did)






