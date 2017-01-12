from __future__ import division, absolute_import
#from nltk.stem.porter import PorterStemmer
#import jsonrpclib
#from simplejson import loads
import io
import logging
import os
from subprocess import Popen, PIPE
import codecs
import xml.etree.ElementTree as ET
import sys
from config.config import geniass_path
from text.sentence import Sentence
from text.token2 import Token2
from text.pair import Pair, Pairs

from text.tlink import TLink

whitespace = [u"\u2002", u"\u2003", u"\u00A0", u"\u2009", u"\u200C", u"\u200D",
              u'\u2005', u'\u2009', u'\u200A']
# tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
#porter = PorterStemmer()


def clean_whitespace(text):
    'replace all whitespace for a regular space " "'
    replacedtext = text
    for code in whitespace:
        replacedtext = replacedtext.replace(code, " ")
    return replacedtext

sources = ("PubMed", "PMC")

class Document(object):
    """A document is constituted by one or more sentences. It should have an ID and
    title. s0, the first sentence, is always the title sentence."""

    def __init__(self, text, process=False, doctype="biomedical", ssplit=False, **kwargs):
        self.text = text
        self.title = kwargs.get("title")
        self.sentences = kwargs.get("sentences", [])
        self.did = kwargs.get("did", "d0")
        self.invalid_sids = []
        self.title_sids = []
        self.source = kwargs.get("source")
        self.pairs = Pairs()
        if ssplit:
            self.sentence_tokenize(doctype)
        if process:
            self.process_document(doctype)

    def sentence_tokenize(self, doctype):
        """
        Split the document text into sentences, add to self.sentences list
        :param doctype: Can be used in the future to choose different methods
        """
        # first sentence should be the title if it exists
        #if self.title:
        #    sid = self.did + ".s0"
        #    self.sentences.append(Sentence(self.title, sid=sid, did=self.did))
        # inputtext = clean_whitespace(self.text)
        inputtext = self.text
        with io.open("/tmp/geniainput.txt", 'w', encoding='utf-8') as geniainput:
            geniainput.write(inputtext)
        current_dir = os.getcwd()
        os.chdir(geniass_path)
        geniaargs = ["./geniass", "/tmp/geniainput.txt", "/tmp/geniaoutput.txt"]
        Popen(geniaargs, stdout=PIPE, stderr=PIPE).communicate()
        os.chdir(current_dir)
        offset = 0
        with io.open("/tmp/geniaoutput.txt", 'r', encoding="utf-8") as geniaoutput:
            for l in geniaoutput:
                stext = l.strip()
                if stext == "":
                    offset = self.get_space_between_sentences(offset)
                    continue
                sid = self.did + ".s" + str(len(self.sentences))
                self.sentences.append(Sentence(stext, offset=offset, sid=sid, did=self.did))
                offset += len(stext)
                offset = self.get_space_between_sentences(offset)

    def process_document(self, corenlpserver, doctype="biomedical"):
        """
        Process each sentence in the text (sentence split if there are no sentences) using Stanford CoreNLP
        :param corenlpserver:
        :param doctype:
        :return:
        """
        if len(self.sentences) == 0:
            # use specific sentence splitter
            self.sentence_tokenize(doctype)
        for s in self.sentences:
            #corenlpres = corenlpserver.raw_parse(s.text)
            corenlpres = corenlpserver.annotate(s.text.encode("utf8"), properties={
                'ssplit.eolonly': True,
                'annotators': 'tokenize,ssplit,pos,ner,lemma',
                #'annotators': 'tokenize,ssplit,pos,parse,ner,lemma,depparse',
                'outputFormat': 'json',
            })
            if isinstance(corenlpres, basestring):
                print corenlpres
                corenlpres = corenlpserver.annotate(s.text.encode("utf8"), properties={
                'ssplit.eolonly': True,
                # 'annotators': 'tokenize,ssplit,pos,depparse,parse',
                'annotators': 'tokenize,ssplit,pos,ner,lemma',
                'outputFormat': 'json',
            })
            if isinstance(corenlpres, basestring):
                print "could not process this sentence:", s.text.encode("utf8")
                print corenlpres
                continue
            else:
                s.process_corenlp_output(corenlpres)


    def tag_chemdner_entity(self, start, end, subtype, source="goldstandard", **kwargs):
        """
        Create an CHEMDNER entity relative to this document.
        :param start: Start index of entity
        :param end: End index of entity
        :param subtype: Subtype of CHEMDNER entity
        :param kwargs: Extra stuff like the text
        :return:
        """
        doct = kwargs.get("doct")
        title_offset = 0
        if doct == "A":
            title_offset = len(self.title) + 1  # account for extra .
        start, end = start + title_offset, end + title_offset
        sentence = self.find_sentence_containing(start, end, chemdner=False)
        if sentence:
            sentence.tag_entity(start - sentence.offset, end - sentence.offset, "chemical", text=kwargs.get("text"),
                                subtype=subtype)
        else:
            print "sentence not found between:", start, end
            print "ignored ", kwargs.get("text")
            # print len(self.documents[pmid].title), self.documents[pmid].title
            # for s in self.documents[pmid].sentences:
            #    print s.sid, s.tokens[0].dstart, s.tokens[-1].dend, s.text

    def add_relation(self, entity1, entity2, subtype, relation, source="goldstandard", **kwargs):
        if self.pairs.pairs:
            pid = self.did + ".p" + str(len(self.pairs.pairs))
        else:
            pid = self.did + ".p0"
        between_text = self.text[entity1.dend:entity2.start]
        logging.info("adding {}:{}=>{}".format(pid, entity1.text.encode("utf8"), entity2.text.encode("utf8")))
        # print between_text
        if subtype == "tlink":
            pair = TLink(entity1, entity2, relation=relation, original_id=kwargs.get("original_id"),
                                     did=self.did, pid=pid, rtype=subtype, between_text=between_text)
        else:
            pair = Pair((entity1, entity2), subtype, did=self.did, pid=pid, original_id=kwargs.get("original_id"), between_text=between_text)
        self.pairs.add_pair(pair, source)
        return pair

    def get_space_between_sentences(self, totalchars):
        """
        When the sentences are split, the whitespace between each sentence is not preserved, so we need to get it back
        :param totalchars: offset of the end of sentence
        :return: Index where the next sentence starts
        """
        while totalchars < len(self.text) and self.text[totalchars].isspace():
            totalchars += 1
        return totalchars

    def get_unique_results(self, source, ths, rules, mode):
        doc_entities = {}
        for s in self.sentences:
            if s.entities:
                if mode == "ner":
                    sentence_entitites = s.entities.get_unique_entities(source, ths, rules)
                    for e in sentence_entitites:
                        sentence_entitites[e].append(s.text[int(sentence_entitites[e][1]):int(sentence_entitites[e][2])])
                    # print sentence_entitites
                elif mode == "re":
                    sentence_entitites = s.entities.get_unique_relations(source)
            # print doc_entities, sentence_entitites
            doc_entities.update(sentence_entitites)
            # print doc_entities
            # print
        logging.info("{} has {} unique entities".format(self.did, len(doc_entities)))
        return doc_entities

    def write_chemdner_results(self, source, outfile, ths={"chebi":0.0}, rules=[]):
        lines = []
        totalentities = 0
        for s in self.sentences:
            # print "processing", s.sid, "with", len(s.entities.elist[source]), "entities"
            if s.entities:
                res = s.entities.write_chemdner_results(source, outfile, len(self.sentences[0].text), ths, rules, totalentities+1)
                lines += res[0]
                totalentities = res[1]
        return lines

    def write_bioc_results(self, parent, source, ths={}):
        bioc_document = ET.SubElement(parent, "document")
        bioc_id = ET.SubElement(bioc_document, "id")
        bioc_id.text = self.did

        bioc_title_passage = ET.SubElement(bioc_document, "passage")
        bioc_title_info = ET.SubElement(bioc_title_passage, "infon", {"key":"type"})
        bioc_title_info.text = "title"
        bioc_title_offset = ET.SubElement(bioc_title_passage, "offset")
        bioc_title_offset.text = str(0)
        bioc_title = self.sentences[0].write_bioc_results(bioc_title_passage, source)

        bioc_abstract_passage = ET.SubElement(bioc_document, "passage")
        bioc_abstract_info = ET.SubElement(bioc_abstract_passage, "infon", {"key":"type"})
        bioc_abstract_info.text = "abstract"
        bioc_abstract_offset = ET.SubElement(bioc_title_passage, "offset")
        bioc_abstract_offset.text = str(len(self.sentences[0].text) + 1)
        for i, sentence in enumerate(self.sentences[1:]):
            bioc_sentence = sentence.write_bioc_results(bioc_abstract_passage, source)
        return bioc_document

    def get_dic(self, source, ths={}):
        dic = {"title":{}, "abstract":{}}
        dic = {"abstract":{}}
        # dic["title"]["offset"] = "0"
        # dic["title"]["sentences"] = self.sentences[0].get_dic(source)

        dic["abstract"]["offset"] = str(len(self.sentences[0].text) + 1)
        dic["abstract"]["sentences"] = []
        for i, sentence in enumerate(self.sentences[1:]):
            dic["abstract"]["sentences"].append(sentence.get_dic(source))
        return dic

    def get_sentence(self, sid):
        """
        Get the sentence by sentence ID
        :param sid: sentence ID
        :return: the sentence object if it exists
        """
        for s in self.sentences:
            # logging.debug([(t.start, t.end) for t in s.tokens])
            if s.sid == sid:
                # logging.debug("found sid: {}".format(sid))
                return s
        return None

    def find_sentence_containing(self, start, end, chemdner=True):
        """
            Find the sentence between start and end. If chemdner, do not consider the first sentence, which
            is the title.
        """
        if chemdner:
            firstsent = 1
        else:
            firstsent = 0
        for i, s in enumerate(self.sentences[firstsent:]):
            if len(s.tokens) == 0:
                #logging.debug("sentence without tokens: {} {}".format(s.sid, s.text.encoding("utf-8")))
                continue
            if s.tokens[0].dstart <= start and s.tokens[-1].dend >= end:
                # print "found it!"
                return s
        for s in self.sentences:
            if len(s.tokens) > 0:
                logging.debug("{} {} {} {} {}".format(s.tokens[0].dstart <= start, s.tokens[-1].dend >= end,
                                                    s.tokens[0].dstart, s.tokens[-1].dend, s.text.encode("utf-8")))
        return None

    def get_entity_offsets(self, esource, ths, rules):
        offsets = []
        for s in self.sentences:
            if s.entities:
                offsets += s.entities.get_entity_offsets(esource, ths, rules)
        return offsets

    def get_entity(self, eid, source="goldstandard"):
        for sentence in self.sentences:
            for e in sentence.entities.elist[source]:
                if e.eid == eid:
                   return e
        print "no entity found for eid {}".format(eid)
        return None

    def get_entities(self, source):
        entities = []
        for s in self.sentences:
            if source in s.entities.elist:
                for e in s.entities.elist[source]:
                    entities.append(e)
        return entities

    def get_abbreviations(self):
        self.abbreviations = {}
        first_elem = []
        second_elem = []
        open_paren = False
        for sentence in self.sentences:
            # print sentence.text
            for i, t in enumerate(sentence.tokens):
                if t.text == "-LRB-":
                    open_paren = True
                    last_token = sentence.tokens[i-1]
                    while last_token.pos.startswith("NN") or last_token.pos.startswith("JJ"): # use nouns before the parenthesis
                        first_elem.insert(0, last_token)
                        if last_token.order == 0:
                            break
                        else:
                            last_token = sentence.tokens[last_token.order - 1]  # check the token before this one
                    if len(first_elem) > 0:
                        logging.info("starting abbreviation for this text: " + str([tt.text for tt in first_elem]))
                    else:
                        open_paren = False
                elif t.text == "-RRB-" and open_paren == True:
                    first_text = sentence.text[first_elem[0].start:first_elem[-1].end]
                    second_text = sentence.text[second_elem[0].start:second_elem[-1].end]
                    if len(first_text) > len(second_text): #abbreviation is the smallest word
                        second_text, first_text = first_text, second_text
                    # rules
                    if not first_text.islower() and len(first_text) > 1:
                        self.abbreviations[first_text] = second_text
                    open_paren = False
                    first_elem = []
                    second_elem = []
                elif open_paren:
                    second_elem.append(t)
        for abv in self.abbreviations:
            if not any([c.isalpha() for c in abv]):
                print abv, ":", self.abbreviations[abv]
