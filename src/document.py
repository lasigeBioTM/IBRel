from __future__ import division, absolute_import, unicode_literals
from nltk.stem.porter import PorterStemmer
#import jsonrpclib
#from simplejson import loads
import logging
import os
import sys
from subprocess import Popen, PIPE
import codecs
import re
import xml.etree.ElementTree as ET
from config import geniass_path

from entity import Entity, ChemdnerAnnotation, Entities


SENTENCE_ORIGINAL_TEXT = 'original_text'
SENTENCE_TEXT = 'text'
SENTENCE_TOKENS = 'tokens'
SENTENCE_POS = 'partofspeech'
SENTENCE_LEMMAS = 'lemmas'
SENTENCE_NER = "stanford_ner"
SENTENCE_OFFSETS = "soffsets"
SENTENCE_PARSE = "sparse"
SENTENCE_STEMS = 'stems'
SENTENCE_TOKENS_FEATURES = 't_features'
SENTENCE_ENTITIES = 'entities'
SENTENCE_PAIRS = 'pairs'
SENTENCE_ENTITIES_ORDER = 'entity_order'
whitespace = [u"\u2002", u"\u2003", u"\u00A0", u"\u2009", u"\u200C", u"\u200D",
              u'\u2005', u'\u2009', u'\u200A']
# tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
porter = PorterStemmer()


def clean_whitespace(text):
    'replace all whitespace for a regular space " "'
    replacedtext = text
    for code in whitespace:
        replacedtext = replacedtext.replace(code, " ")
    return replacedtext


class Document(object):
    '''A document is constituted by one or more sentences. It should have an ID and
    title. s0, the first sentence, is always the title sentence.'''

    def __init__(self, text, process=False, doctype="biomedical", ssplit=False, **kwargs):
        self.text = text
        self.title = kwargs.get("title")
        self.sentences = kwargs.get("sentences", [])
        self.did = kwargs.get("did", "d0")
        if ssplit:
            self.sentence_tokenize(doctype)
        if process:
            self.process_document(doctype)

    def sentence_tokenize(self, doctype):
        #self.sentences = []
        # first sentence should be the title if it exists
        if self.title:
            sid = self.did + ".s0"
            self.sentences.append(Sentence(self.title, sid=sid, did=self.did))
        # inputtext = clean_whitespace(self.text)
        inputtext = self.text
        with codecs.open("/tmp/geniainput.txt", 'w', 'utf-8') as geniainput:
            geniainput.write(inputtext)
        current_dir = os.getcwd()
        os.chdir(geniass_path)
        geniaargs = ["./geniass", "/tmp/geniainput.txt", "/tmp/geniaoutput.txt"]
        Popen(geniaargs, stdout=PIPE, stderr=PIPE).communicate()
        os.chdir(current_dir)
        offset = 0
        with codecs.open("/tmp/geniaoutput.txt", 'r', "utf-8") as geniaoutput:
            for l in geniaoutput:
                stext = l.strip()
                sid = self.did + ".s" + str(len(self.sentences))
                self.sentences.append(Sentence(stext, offset=offset, sid=sid, did=self.did))
                offset += len(stext)
                offset = self.get_space_between_sentences(offset)

    def process_document(self, corenlpserver, doctype="biomedical"):
        if len(self.sentences) == 0:
            # use specific sentence splitter
            self.sentence_tokenize(doctype)
        # docsentences = '\n'.join([s.text for s in self.sentences])
        for s in self.sentences:
            logging.debug(s.sid)
            # corenlpres = loads(corenlpserver.parse(s.text))
            # print s.text
            corenlpres = corenlpserver.raw_parse(s.text)
            # corenlpres = corenlpserver.parse_doc(s.text)
            s.process_corenlp_sentence(corenlpres)
            # TODO: bllip parser biomodel
        # print self

    def process_corenlp_sentences(self, corenlpres):
        self.sentences = []
        # create new sentence object
        for sentence in corenlpres['sentences']:  # sentence is a dict
            newsent = Sentence(sentence["text"])
            # print newsent.text
            newsent.parsetree = sentence['parsetree']
            newsent.tokens = []
            for t in sentence['words']:
                newtoken = Token(t[0])
                newtoken.lemma = t[1]["Lemma"]
                newtoken.start_offset = int(t[1]["CharacterOffsetBegin"])
                newtoken.end_offset = int(t[1]["CharacterOffsetEnd"])
                newtoken.pos = t[1]["PartOfSpeech"]
                newtoken.tag = t[1]["NamedEntityTag"]
                newtoken.stem = porter.stem_word(newtoken.text)
                newsent.tokens.append(newtoken)
        self.sentences.append(newsent)

    def tag_chemdner_entity(self, start, end, subtype, **kwargs):
        doct = kwargs.get("doct")
        if doct == "T":
            # entity = ChemdnerAnnotation([], sentenceid=self.sentences[0].sid)
            self.sentences[0].tag_entity(start, end, subtype, **kwargs)
            # print self.text[start:end], kwargs.get("text")
            # newentity = ChemdnerAnnotation(text=kwargs.get("text"), sentenceid=sid)
        else:
            found = False
            totalchars = 0
            #print "start", start, "end", end
            for s in self.sentences[1:]:
                #print totalchars
                if totalchars <= start and totalchars + len(s.text) >= end:  # entity is in this sentence
                    # entity = ChemdnerAnnotation([], sentenceid=s.sid)
                    s.tag_entity(start-totalchars, end-totalchars, subtype,
                                 totalchars=totalchars, **kwargs)
                    # print "found entity on sentence %s" % s.sid
                    found = True
                    break

                totalchars += len(s.text)
                totalchars = self.get_space_between_sentences(totalchars)
                # print totalchars
                # account for space between sentences
                # print totalchars
            if not found:
                print "could not find sentence for %s:%s on %s!" % (start,
                                                                       end, self.did)
                # sys.exit()

    def get_space_between_sentences(self, totalchars):
        while totalchars < len(self.text) and self.text[totalchars].isspace():
            totalchars += 1
        return totalchars

    def write_chemdner_results(self, source, outfile, ths={"chebi":0.0}, rules=[]):
        lines = []
        totalentities = 0
        for s in self.sentences:
            # print "processing", s.sid, "with", len(s.entities.elist[source]), "entities"
            if s.entities:
                res = s.entities.write_chemdner_results(source, outfile, ths, rules, totalentities+1)
                lines += res[0]
                totalentities = res[1]
                '''if source in s.entities.elist:
                    logging.info("%s: %s entities -> %s lines" % (s.sid, len(s.entities.elist[source]), len(lines)))
                    logging.info(' '.join([str(e.dstart) + ":" + str(e.dend) for e in s.entities.elist[source]]))
                else:
                    logging.info("no results for this sentence: %s", s.sid  )
                    logging.info(' '.join(s.entities.elist.keys()))'''
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
        dic["title"]["offset"] = "0"
        dic["title"]["sentences"] = self.sentences[0].get_dic(source)

        dic["abstract"]["offset"] = str(len(self.sentences[0].text) + 1)
        dic["abstract"]["sentences"] = []
        for i, sentence in enumerate(self.sentences[1:]):
            dic["abstract"]["sentences"].append(sentence.get_dic(source))
        return dic

    def get_sentence(self, sid):
        for s in self.sentences:
            # logging.debug([(t.start, t.end) for t in s.tokens])
            if s.sid == sid:
                # logging.debug("found sid: {}".format(sid))
                return s
        return None

    def find_sentence_containing(self, start, end, chemdner=True):
        '''
            Find the sentence between start and end. If chemdner, do not consider the first sentence, which
            is the title.
        '''
        if chemdner:
            firstsent = 1
        else:
            firstsent = 0
        for i, s in enumerate(self.sentences[firstsent:]):
            if len(s.tokens) == 0:
                logging.debug("sentence without tokens: {} {}".format(s.sid, s.text))
                continue
            #print s.tokens[0].dstart, s.tokens[-1].dend
            if s.tokens[0].dstart <= start and s.tokens[-1].dend >= end:
                # print "found it!"
                return s
        return None

class Sentence(object):
    '''Sentence from a document, to be annotated'''
    def __init__(self, text, offset=0, **kwargs):
        self.text = text
        self.sid = kwargs.get("sid")
        self.did = kwargs.get("did")
        self.entities = Entities(sid=self.sid, did=self.did)
        self.offset = offset

    def process_corenlp_sentence(self, corenlpres):
        # self.sentences = []
        if len(corenlpres['sentences']) > 1:
            sys.exit("Number of sentences from CoreNLP is not 1.")
        # for sentence in corenlpres['sentences']: # sentence is a dict
            # newsent = Sentence(sentence["text"])
            # print newsent.text
        if len(corenlpres['sentences']) == 0:
            self.tokens = []
            self.create_newtoken("", {})
            logging.debug("no sentences")
            logging.debug(self.text)
            return
        sentence = corenlpres['sentences'][0]
        # print sentence
        self.parsetree = sentence['parsetree']
        # print self.parsetree
        # self.parsetree = sentence['parse']
        self.tokens = []
        for t in sentence['words']:
            # print t[0]
            if t[0]:
                # separate "-" when between words with more than 4 chars
                token_seq = re.split(r'-|/|\\|\+|\.', t[0])

                if len(token_seq) > 1 and all([len(elem) > 1 for elem in token_seq]):

                    for its, ts in enumerate(token_seq):
                        #print token_seq[:its]
                        charoffset_begin = int(t[1]["CharacterOffsetBegin"])
                        if token_seq[:its]:
                            charoffset_begin += sum([len(x) for x in token_seq[:its]])
                        charoffset_begin += its
                        charoffset_end = len(ts) + charoffset_begin
                        #logging.info(str(charoffset_begin) + ":" + str(charoffset_end))
                        ts_props = {"CharacterOffsetBegin": charoffset_begin,
                                    "CharacterOffsetEnd": charoffset_end,
                                    "PartOfSpeech": t[1]["PartOfSpeech"],
                                    "NamedEntityTag": t[1]["NamedEntityTag"],
                                    "Lemma": t[1]["Lemma"]}
                        self.create_newtoken(ts, ts_props)

                else:
                    self.create_newtoken(t[0], t[1])

                #self.tokens.append(newtoken)
        # logging.debug([(t.start, t.end) for t in self.tokens])

    def create_newtoken(self, text, props):
        newtoken = Token(text)
        try:
            newtoken.start = int(props["CharacterOffsetBegin"])
            newtoken.dstart = newtoken.start + self.offset
            newtoken.end = int(props["CharacterOffsetEnd"])
            newtoken.dend = newtoken.end + self.offset
            newtoken.pos = props["PartOfSpeech"]
            newtoken.tag = props["NamedEntityTag"]
            newtoken.lemma = props["Lemma"]
            newtoken.stem = porter.stem_word(newtoken.text)
            newtoken.tid = self.sid + ".t" + str(len(self.tokens))
            self.tokens.append(newtoken)
            # print "|{}| <=> |{}|".format(text, self.text[newtoken.start:newtoken.end])
        except KeyError:
            logging.debug("error: text={} props={}".format(text, props))
            return None
        # logging.debug(newtoken.text)
        return newtoken

    def tag_entity(self, start, end, subtype, entity=None, totalchars=0, source="goldstandard", **kwargs):
        '''Find the tokens that match this entity. start and end are relative to the sentence. 
           Totalchars is the offset of the sentence on the document.'''
        tlist = []
        #logging.debug("lets tag this entity")
        # print self.tokens
        for t in self.tokens:
            # discard tokens that intersect the entity for now
            # print t.start, t.end, t.text
            if t.start >= start and t.end <= end:
                tlist.append(t)
        if tlist:
            newtext = self.text[tlist[0].start:tlist[-1].end]
            if entity:
                entity.text = newtext
            if "text" in kwargs and newtext != kwargs["text"]:
                if newtext not in kwargs["text"] and kwargs["text"] not in newtext:
                    return None
                else:
                    print tlist[0].start, tlist[-1].end, "|" + newtext + "|", "=>", "|" + kwargs["text"] + "|", start, end, self.sid, self.text
            #     print "tokens found:", [t.text for t in tlist]
                # sys.exit()
            # else:
            # print "found the tokens!", start, end, kwargs["text"], self.sid
            if self.entities.elist.get(source):
                eid = self.sid + ".e" + str(len(self.entities.elist[source]))
            else:
                eid = self.sid + ".e0"
            if entity:
                self.entities.add_entity(entity, source)
            else:
                self.entities.add_entity(ChemdnerAnnotation(tlist, self.sid, text=newtext,
                                         did=self.did, eid=eid, subtype=subtype), source)

            self.label_tokens(tlist, source, subtype)
            #logging.debug("added new entity to %s, now with %s entities" % (self.sid,
            #                                                                 len(self.entities.elist[source])))
            return eid
        #else:
        #    print "no tokens found:", start, end, kwargs.get("text"), self.text
        #    print self.text[:start]
            # [(t.start, t.end, t.text) for t in self.tokens]


    def label_tokens(self, tlist, source, subtype="entity"):
        if len(tlist) == 1:
            tlist[0].tags[source] = "single"
            tlist[0].tags[source + "_subtype"] = subtype
        else:
            for t in range(len(tlist)):
                if t == 0:
                    tlist[t].tags[source] = "start"
                    tlist[t].tags[source + "_subtype"] = subtype
                elif t == len(tlist) - 1:
                    tlist[t].tags[source] = "end"
                    tlist[t].tags[source + "_subtype"] = subtype
                else:
                    tlist[t].tags[source] = "middle"
                    tlist[t].tags[source + "_subtype"] = subtype
        #logging.debug([t.tags for t in self.tokens])

    def write_bioc_results(self, parent, source):
        bioc_sentence = ET.SubElement(parent, "sentence")
        bioc_sentence_offset = ET.SubElement(bioc_sentence, "offset")
        bioc_sentence_offset.text = str(self.tokens[0].dstart)
        bioc_sentence_text = ET.SubElement(bioc_sentence, "text")
        bioc_sentence_text.text = self.text

        if source in self.entities.elist:
            for entity in self.entities.elist[source]:
                bioc_annotation = entity.write_bioc_annotation(bioc_sentence)
        return bioc_sentence

    def get_dic(self, source):
        dic = {}
        dic["offset"] = str(self.tokens[0].dstart)
        dic["text"] = self.text
        dic["entities"] = []
        if source in self.entities.elist:
            for entity in self.entities.elist[source]:
                dic["entities"].append(entity.get_dic())
            dic["entities"] = sorted(dic["entities"], key=lambda k: k['offset'])
        return dic

    def find_tokens_between(self, start, end, relativeto="doc"):
        '''Return list of tokens between offsets. Use relativeto to consider doc indexes or
           sentence indexes.'''
        foundtokens = []
        for t in self.tokens:
            if relativeto.startswith("doc") and t.dstart >= start and t.dend <= end:
                foundtokens.append(t)
            elif relativeto.startswith("sent") and t.start >= start and t.end <= end:
                foundtokens.append(t)
        return foundtokens
        

class Token(object):
    '''Token that is part of a sentence'''
    def __init__(self, text, **kwargs):
        self.text = text
        self.sid = kwargs.get("sid")
        self.features = {}
        self.tags = {}
        self.tid = kwargs.get("tid")
