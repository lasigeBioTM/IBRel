from __future__ import division, absolute_import, unicode_literals
#from nltk.stem.porter import PorterStemmer
#import jsonrpclib
#from simplejson import loads
import logging
import os
from subprocess import Popen, PIPE
import codecs
import xml.etree.ElementTree as ET
from config import geniass_path

from sentence import Sentence
from token2 import Token2

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
                newtoken = Token2(t[0], order=len(newsent.tokens))
                newtoken.lemma = t[1]["Lemma"]
                newtoken.start_offset = int(t[1]["CharacterOffsetBegin"])
                newtoken.end_offset = int(t[1]["CharacterOffsetEnd"])
                newtoken.pos = t[1]["PartOfSpeech"]
                newtoken.tag = t[1]["NamedEntityTag"]
                #newtoken.stem = porter.stem_word(newtoken.text)
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
        dic = {"abstract":{}}
        # dic["title"]["offset"] = "0"
        # dic["title"]["sentences"] = self.sentences[0].get_dic(source)

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


