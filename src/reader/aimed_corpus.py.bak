__author__ = 'Andre'
import codecs
import time
import logging
import sys
import os
from bs4 import BeautifulSoup
import progressbar as pb
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '../..'))
from text.corpus import Corpus
from text.document import Document
from text.sentence import Sentence


class AIMedCorpus(Corpus):
    def __init__(self, corpusdir, **kwargs):
        super(AIMedCorpus, self).__init__(corpusdir, **kwargs)

    def load_corpus(self, corenlpserver, process=True):
        trainfiles = [self.path + '/' + f for f in os.listdir(self.path)]
        total = len(trainfiles)
        widgets = [pb.Percentage(), ' ', pb.Bar(), ' ', pb.AdaptiveETA(), ' ', pb.Timer()]
        pbar = pb.ProgressBar(widgets=widgets, maxval=total, redirect_stdout=True).start()
        time_per_abs = []
        for current, f in enumerate(trainfiles):
            #logging.debug('%s:%s/%s', f, current + 1, total)
            print '{}:{}/{}'.format(f, current + 1, total)
            did = f
            t = time.time()
            with open(f, 'r') as f:
                article = "<Article>" + f.read() +  "</Article>"
            soup = BeautifulSoup(article, 'xml')
            #doc = soup.find_all("article")
            title = soup.ArticleTitle.get_text()
            abstract = soup.AbstractText.get_text()
            doc_text = title + " " + abstract

            newdoc = Document(doc_text, process=False, did=did)
            newdoc.sentence_tokenize("biomedical")
            newdoc.process_document(corenlpserver, "biomedical")
            #logging.info(len(newdoc.sentences))
            self.documents[newdoc.did] = newdoc
            abs_time = time.time() - t
            time_per_abs.append(abs_time)
            logging.debug("%s sentences, %ss processing time" % (len(newdoc.sentences), abs_time))
            pbar.update(current)
        pbar.finish()
        abs_avg = sum(time_per_abs)*1.0/len(time_per_abs)
        logging.info("average time per abstract: %ss" % abs_avg)


    def load_annotations(self, ann_dir, etype, ptype):
        trainfiles = [ann_dir + '/' + f for f in os.listdir(self.path)]
        total = len(trainfiles)
        widgets = [pb.Percentage(), ' ', pb.Bar(), ' ', pb.AdaptiveETA(), ' ', pb.Timer()]
        pbar = pb.ProgressBar(widgets=widgets, maxval=total, redirect_stdout=True).start()
        time_per_abs = []
        for current, f in enumerate(trainfiles):
            # logging.debug('%s:%s/%s', f, current + 1, total)
            print '{}:{}/{}'.format(f, current + 1, total)
            did = f
            with open(f, 'r') as f:
                article = "<Article>" + f.read() +  "</Article>"
            soup = BeautifulSoup(article, 'xml')
            title = soup.ArticleTitle
            abstract = soup.AbstractText
            title_text = title.get_text()
            abstract_text = abstract.get_text()
            abs_offset = len(title.get_text()) + 1
            title_entities = title.find_all("prot", recursive=False)
            abs_entities = abstract.find_all("prot", recursive=False)
            lastindex = 0
            for ei, e in enumerate(title_entities):
                estart = title_text.find(e.text, lastindex)
                eend = estart + len(e.text)
                etext = title_text[estart:eend]
                #print etext, estart, eend, self.documents[did].text
                this_sentence = self.documents[did].find_sentence_containing(estart, eend, chemdner=False)
                eid = this_sentence.tag_entity(estart, eend, "protein", text=e.text)
                if eid is None:
                    print "did not add this entity: {}".format(e.text)
                # print e.text
                lastindex = estart
            lastindex = 0
            for ei, e in enumerate(abs_entities):
                estart = abstract_text.find(e.text, lastindex)
                eend = estart + len(e.text)
                etext = self.documents[did].text[estart:eend]
                # logging.info("{} - {}".format(lastindex, e.text))
                #logging.info(estart)
                #logging.info("{} + {} {}: {}-{}: {}".format(abstract_text.find(e.text, lastindex), abs_offset, e.text, estart,
                 #                                           eend, "-".join([str(s.offset) for s in self.documents[did].sentences])))
                #logging.info(abstract_text)
                this_sentence = self.documents[did].find_sentence_containing(estart + abs_offset, eend + abs_offset, chemdner=False)
                eid = this_sentence.tag_entity(estart + abs_offset - this_sentence.offset , eend + abs_offset - this_sentence.offset,
                                               "protein", text=e.text)
                if eid is None:
                    print "did not add this entity: {}".format(e.text)
                # print e.text
                lastindex = estart
        #for s in all_entities:
        #    print s, len(all_entities[s])


def get_genia_gold_ann_set(goldann, etype):
    gold_offsets = set()
    soup = BeautifulSoup(codecs.open(goldann, 'r', "utf-8"), 'html.parser')
    docs = soup.find_all("article")
    all_entities = {}
    for doc in docs:
        did = "GENIA" + doc.articleinfo.bibliomisc.text.split(":")[1]
        title = doc.title.sentence.get_text()
        doc_text = title + " "
        doc_offset = 0
        sentences = doc.abstract.find_all("sentence")
        for si, s in enumerate(sentences):
            stext = s.get_text()
            sentities = s.find_all("cons", recursive=False)
            lastindex = 0
            for ei, e in enumerate(sentities):
                estart = stext.find(e.text, lastindex) + doc_offset # relative to document
                eend = estart + len(e.text)
                sem = e.get("sem")
                if sem.startswith("("):
                    #TODO: Deal with overlapping entities
                    continue
                entity_type = sem.split("_")[0]
                if etype == "all" or type_match.get(entity_type) == etype:
                    gold_offsets.add((did, estart, eend, e.text))
                # etext = doc_text[estart:eend]
                # logging.info("gold annotation: {}".format(e.text))

            doc_text += stext + " "
            doc_offset = len(doc_text)
    return gold_offsets, None

def main():
    logging.basicConfig(level=logging.DEBUG)
    c = GeniaCorpus(sys.argv[1])
    c.load_corpus("")
    c.load_annotations(sys.argv[1])
if __name__ == "__main__":
    main()