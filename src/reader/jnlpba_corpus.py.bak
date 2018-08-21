import codecs
import logging
import xml.etree.ElementTree as ET
import os
import sys
import progressbar as pb
import time
import progressbar as pb
from text.corpus import Corpus
from text.document import Document
from text.sentence import Sentence

type_match = {"DNA": "dna",
              "protein": "protein",
              "cell_type": "",
              "cell_line": "",
              "RNA": ""}

class JNLPBACorpus(Corpus):
    def __init__(self, corpusdir, **kwargs):
        super(JNLPBACorpus, self).__init__(corpusdir, **kwargs)
        self.subtypes = ["protein", "DNA"]

    def load_corpus(self, corenlpserver, process=True):
        widgets = [pb.Percentage(), ' ', pb.Bar(), ' ', pb.ETA(), ' ', pb.Timer()]
        nlines = 0
        with open(self.path) as f:
            for nlines, l in enumerate(f):
                pass
        print nlines
        pbar = pb.ProgressBar(widgets=widgets, maxval=nlines).start()
        with codecs.open(self.path, 'r', "utf-8") as corpusfile:
            doc_text = ""
            sentences = []
            for i,l in enumerate(corpusfile):
                if l.startswith("###"): # new doc
                    if doc_text != "":
                        logging.debug("creating document: {}".format(doc_text))
                        newdoc = Document(doc_text, process=False, did=did)
                        newdoc.sentences = sentences[:]
                        newdoc.process_document(corenlpserver, "biomedical")
                        # logging.info(len(newdoc.sentences))
                        self.documents[newdoc.did] = newdoc
                        doc_text = ""
                    did = "JNLPBA" + l.strip().split(":")[-1]
                    logging.debug("starting new document:" + did)
                    sentence_text = ""
                    doc_offset = 0
                    sentences = []
                elif l.strip() == "" and sentence_text != "": # new sentence
                    #logging.debug("creating mew sentence: {}".format(sentence_text))
                    sid = did + ".s" + str(len(sentences))
                    this_sentence = Sentence(sentence_text, offset=doc_offset, sid=sid, did=did)
                    doc_offset += len(sentence_text) + 1
                    doc_text += sentence_text + " "
                    sentences.append(this_sentence)
                    if i == nlines:
                        logging.debug("creating document: {}".format(doc_text))
                        newdoc = Document(doc_text, process=False, did=did)
                        newdoc.sentences = sentences[:]
                        newdoc.process_document(corenlpserver, "biomedical")
                        # logging.info(len(newdoc.sentences))
                        self.documents[newdoc.did] = newdoc
                        doc_text = ""
                    # start new sentence
                    sentence_text = ""
                else:
                    #logging.debug(str(i) + "/" + str(l))
                    t = l.strip().split("\t")
                    if sentence_text != "":
                        sentence_text += " "
                    #if t[1] == "B-protein"
                    sentence_text += t[0]
                pbar.update(i)
            pbar.finish()

    def load_annotations(self, ann_dir, etype, ptype):
        added = True
        pmids = []
        tagged = 0
        not_tagged = 0
        with codecs.open(ann_dir, 'r', "utf-8") as corpusfile:
            doc_text = ""
            sentences = []
            for i, l in enumerate(corpusfile):
                if l.startswith("###"):  # new doc
                    if doc_text != "":
                        # logging.info(len(newdoc.sentences))
                        doc_text = ""
                    pmid = l.strip().split(":")[-1]
                    pmids.append(pmid)
                    did = "JNLPBA" + pmid
                    self.documents[did].get_abbreviations()
                    logging.debug("starting new document:" + did)
                    sentence_text = ""
                    sentence_entities = []
                    doc_offset = 0
                    sentences = []
                elif l.strip() == "" and sentence_text != "":  # new sentence
                    #logging.debug("creating mew sentence: {}".format(sentence_text))
                    sid = did + ".s" + str(len(sentences))
                    this_sentence = self.documents[did].get_sentence(sid)
                    if not added: # in case the last token was an entity
                        sentence_entities.append((estart, eend, entity_text))
                        added = True
                    #print sentence_entities
                    for e in sentence_entities:
                        #logging.debug("adding this entity: {}".format(e[2]))
                        eid = this_sentence.tag_entity(e[0], e[1], etype,
                                                  text=e[2])
                        if eid is None:
                            print "did not add this entity: {}".format(e[2])
                            not_tagged += 1
                        else:
                            tagged += 1
                        #    this_sentence.entities.get_entity(eid).normalize()
                    doc_offset += len(sentence_text) + 1
                    doc_text += sentence_text + " "
                    sentences.append(this_sentence)
                    # start new sentence
                    sentence_text = ""
                    sentence_entities = []
                else:
                    # logging.debug(str(i) + "/" + str(l))
                    if sentence_text != "":
                        sentence_text += " "
                    t = l.strip().split("\t")
                    if len(t) > 1 and t[1] != "O" and "B-" + type_match[t[1].split("-")[1]] == "B-" + etype:
                        estart = len(sentence_text)
                        eend = estart + len(t[0])
                        entity_text = t[0]
                        added = False
                    elif len(t) > 1 and t[1] != "O" and "I-" + type_match[t[1].split("-")[1]] == "I-" + etype:
                        eend += 1 + len(t[0])
                        entity_text += " " + t[0]
                    else: # not B- I-
                        if not added:
                            sentence_entities.append((estart, eend, entity_text))
                            added = True
                    sentence_text += t[0]
        print "tagged: {} not tagged: {}".format(tagged, not_tagged)
        with codecs.open(ann_dir + "-pmids.txt", 'w', "utf-8") as pmidsfile:
            pmidsfile.write("\n".join(pmids))

def get_jnlpba_gold_ann_set(goldann, etype):
    gold_offsets = set()
    added = True
    with codecs.open(goldann, 'r', "utf-8") as corpusfile:
        doc_text = ""
        sentences = []
        for i, l in enumerate(corpusfile):
            if l.startswith("###"):  # new doc
                if doc_text != "":
                    # logging.info(len(newdoc.sentences))
                    doc_text = ""
                did = "JNLPBA" + l.strip().split(":")[-1]
                logging.debug("starting new document:" + did)
                sentence_text = ""
                sentence_entities = []
                doc_offset = 0
                sentences = []
            elif l.strip() == "" and sentence_text != "":  # new sentence
                #logging.debug("creating mew sentence: {}".format(sentence_text))
                if not added:  # in case the last token was an entity
                    gold_offsets.add((did, doc_offset + estart, doc_offset + eend, entity_text))
                    added = True
                doc_offset += len(sentence_text) + 1
                doc_text += sentence_text + " "
                # start new sentence
                sentence_text = ""
                sentence_entities = []
            else:
                # logging.debug(str(i) + "/" + str(l))
                if sentence_text != "":
                    sentence_text += " "
                t = l.strip().split("\t")
                if len(t) > 1 and t[1] != "O" and "B-" + type_match[t[1].split("-")[1]] == "B-" + etype:
                    estart = len(sentence_text)
                    eend = estart + len(t[0])
                    entity_text = t[0]
                    added = False
                elif len(t) > 1 and t[1] != "O" and "I-" + type_match[t[1].split("-")[1]] == "I-" + etype:
                    eend += 1 + len(t[0])
                    entity_text += " " + t[0]
                else:  # not B- I-
                    if not added:
                        gold_offsets.add((did, doc_offset + estart, doc_offset + eend, entity_text))
                        added = True
                sentence_text += t[0]
    return gold_offsets, None