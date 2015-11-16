__author__ = 'Andre'
import codecs
import time
import logging
import sys
import os
from bs4 import BeautifulSoup
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '../..'))
from text.corpus import Corpus
from text.document import Document
from text.sentence import Sentence


class GeniaCorpus(Corpus):
    def __init__(self, corpusdir, **kwargs):
        super(GeniaCorpus, self).__init__(corpusdir, **kwargs)
        self.subtypes = ["protein", "DNA"]

    def load_corpus(self, corenlpserver, process=True):
        time_per_abs = []
        soup = BeautifulSoup(codecs.open(self.path, 'r', "utf-8"), 'html.parser')
        docs = soup.find_all("article")
        for doc in docs:
            did = "GENIA" + doc.articleinfo.bibliomisc.text.split(":")[1]
            title = doc.title.sentence.get_text()
            sentences = doc.abstract.find_all("sentence")
            doc_sentences = []
            doc_text = title + " "
            doc_offset = 0
            for si, s in enumerate(sentences):
                t = time.time()
                stext = s.get_text()
                sid = did + ".s" + str(si)
                doc_text += stext + " "
                this_sentence = Sentence(stext, offset=doc_offset, sid=sid, did=did)
                doc_offset = len(doc_text)
                doc_sentences.append(this_sentence)
            newdoc = Document(doc_text, process=False, did=did)
            newdoc.sentences = doc_sentences[:]
            newdoc.process_document(corenlpserver, "biomedical")
            #logging.info(len(newdoc.sentences))
            self.documents[newdoc.did] = newdoc
            abs_time = time.time() - t
            time_per_abs.append(abs_time)
            logging.info("%s sentences, %ss processing time" % (len(newdoc.sentences), abs_time))
        abs_avg = sum(time_per_abs)*1.0/len(time_per_abs)
        logging.info("average time per abstract: %ss" % abs_avg)

    def load_annotations(self, ann_dir):
        time_per_abs = []
        skipped = 0
        notskipped = 0
        soup = BeautifulSoup(codecs.open(self.path, 'r', "utf-8"), 'html.parser')
        docs = soup.find_all("article")
        all_entities = {}
        for doc in docs:
            did = "GENIA" + doc.articleinfo.bibliomisc.text.split(":")[1]
            title = doc.title.find_all("sentence")
            # TODO: title also has annotations...
            sentences = doc.abstract.find_all("sentence")
            for si, s in enumerate(sentences):
                stext = s.get_text()
                sid = did + ".s" + str(si)
                this_sentence = self.documents[did].get_sentence(sid)
                sentities = s.find_all("cons")
                lastindex = 0
                for ei, e in enumerate(sentities):
                    estart = stext.find(e.text, lastindex)
                    eend = estart + len(e.text)
                    etext = stext[estart:eend]
                    # print etext, stext[estart:eend]
                    sems = e.get("sem")
                    '''if sems is not None and len(sems.split(" ")) > 1: # parent cons, skip
                        skipped += 1
                        print "skipped", sems, sems.split(" ")
                        continue
                    if sems is None: # get the sem of parent - but for now slip
                        # skipped += 1
                        # print "skipped", sems
                        continue
                        sems = e.parent.get("sem")
                        sems = sems.split(" ")
                        sems = sems[1:]
                        sibs = [x for x in e.parent.find_all("cons")]
                        i = e.parent.index(e)/2
                        # print etext, sems, sibs, i
                        if i > len(sems)-1:
                            # i = len(sems) - 1
                            continue
                        sem = sems[i]
                    else:
                        sem = sems
                    # print sem
                    if sem.endswith(")"):
                        sem = sem[:-1]
                    if sem.startswith("("):
                        sem = sem[1:]
                    eid = sid + ".e" + str(ei)'''
                    if sems is None or len(sems.split(" ")) > 1: # parent cons, skip
                        continue
                    sem = sems
                    # print sem
                    if sem.endswith(")"):
                        sem = sem[:-1]
                    if sem.startswith("("):
                        sem = sem[1:]
                    if sem.startswith("G#protein"):
                        eid = this_sentence.tag_entity(estart, eend, "protein",
                                                     text=e.text)
                        if eid is None:
                            print "did not add this entity: {}".format(e.text)
                        # print e.text
                        notskipped += 1

                    t = sem.split("_")[0]
                    if t not in all_entities:
                        all_entities[t] = []
                    all_entities[t].append(etext)
                    #if sem is not None and sem.startswith("G#protein"):
                    #    print e.text, "|", etext, eindex, stext[0:20]
                    lastindex = estart
        for s in all_entities:
            print s, len(all_entities[s])




def main():
    logging.basicConfig(level=logging.DEBUG)
    c = GeniaCorpus(sys.argv[1])
    c.load_corpus("")
    c.load_annotations(sys.argv[1])
if __name__ == "__main__":
    main()