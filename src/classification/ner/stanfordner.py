from __future__ import division, unicode_literals
import sys
from subprocess import Popen, PIPE, call
import logging
import codecs
import ner
import re
import atexit
from socket import error as SocketError
import errno

from text.protein_entity import ProteinEntity
from text.offset import Offsets, Offset
from classification.results import ResultsNER
from classification.ner.simpletagger import SimpleTaggerModel, create_entity
from config import config

stanford_coding = {"-LRB-": "<", "\/": "/", "&apos;": "'", "analogs": "analogues", "analog": "analogue",
                   "-RRB-": ">", ":&apos;s": "'s"}
# convert < to -LRB, etc
rep = dict((re.escape(v), k) for k, v in stanford_coding.iteritems())
pattern = re.compile("|".join(rep.keys()))


def replace_abbreviations(text):
    return pattern.sub(lambda m: rep[re.escape(m.group(0))], text)


class StanfordNERModel(SimpleTaggerModel):
    RAM = config.stanford_ner_train_ram
    RAM_TEST = config.stanford_ner_test_ram
    STANFORD_BASE = config.stanford_ner_dir
    STANFORD_NER = "{}/stanford-ner.jar".format(STANFORD_BASE)
    NER_PROP = "{}/base.prop".format(STANFORD_BASE)
    logging.info(NER_PROP)
    PARAMS = ["java", RAM, "-Dfile.encoding=UTF-8", "-cp", STANFORD_NER,
              "edu.stanford.nlp.ie.crf.CRFClassifier", "-prop", NER_PROP,
              "-readerAndWriter", "edu.stanford.nlp.sequences.CoNLLDocumentReaderAndWriter"]
    logging.info(PARAMS)
    TEST_SENT = "Structure-activity relationships have been investigated for inhibition of DNA-dependent protein kinase (DNA-PK) and ATM kinase by a series of pyran-2-ones, pyran-4-ones, thiopyran-4-ones, and pyridin-4-ones."

    def __init__(self, path, etype, **kwargs):
        super(StanfordNERModel, self).__init__(path, etype, **kwargs)
        self.process = None
        self.tagger = None
        self.port = None

    def write_prop(self):
        """
        Write Stanford-NER prop file based on base.prop
        :return:
        """
        lines = codecs.open(self.NER_PROP, "r", "utf-8").readlines()
        with codecs.open(self.NER_PROP, "w", "utf-8") as props:
            for l in lines:
                if l.startswith("trainFile"):
                    props.write("trainFile = {}.bilou\n".format(self.path))
                elif l.startswith("serializeTo"):
                    props.write("serializeTo = {}.ser.gz\n".format(self.path))
                elif l.startswith("entitySubclassification"):
                    props.write('entitySubclassification = SBIEO\n')
                elif l.startswith("retainEntitySubclassification"):
                    props.write("retainEntitySubclassification = false\n")
                else:
                    props.write(l)
        logging.info("wrote prop file")

    def train(self):
        self.write_prop()
        self.save_corpus_to_sbilou()
        logging.info("Training model with StanfordNER")
        process = Popen(self.PARAMS, stdout=PIPE, stderr=PIPE)
        # process.communicate()
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                logging.info(output.strip())
        rc = process.poll()
        logging.info("model " + self.path +'.ser.gz trained')
        # Popen(["jar", "-uf", self.STANFORD_NER, "{}.ser.gz".format(self.path)]).communicate()
        logging.info("saved model file to {}".format(self.STANFORD_NER))

    def test(self, corpus):

        tagged_sentences = []
        logging.info("sending sentences to tagger {}...".format(self.path))
        for isent, sid in enumerate(self.sids):
            #out = self.tagger.tag_text(replace_abbreviations(" ".join([t.text for t in self.tokens[isent]])))
            #out = self.tagger.tag_text(self.sentences[isent])
            #text = self.sentences[isent]
            text = " ".join([t.text for t in self.tokens[isent]])
            #logging.info("tagging: {}/{} - {}={}".format(isent, len(self.sids), sid, did))
            out = self.annotate_sentence(text)
            tagged_sentences.append(out)
        results = self.process_results(tagged_sentences, corpus)
        return results

    def annotate_sentence(self, text):
        self.tagger = ner.SocketNER("localhost", self.port, output_format='inlineXML')
        try:
            out = self.tagger.tag_text(text)
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise  # Not error we are looking for
            print "socket error with sentence {}".format(text)
        except:
            print "other socket error!"
            out = self.tagger.tag_text(text)
        return out

    def kill_process(self):
        self.process.kill()

    def process_results(self, sentences, corpus):
        results = ResultsNER(self.path)
        results.corpus = corpus
        for isent, sentence_output in enumerate(sentences):
            sid = self.sids[isent]
            did = '.'.join(sid.split('.')[:-1])
            sentence = results.corpus.documents[did].get_sentence(sid)
            if sentence is None:
                print sid
                print "not found!"
                print results.corpus.documents['.'.join(sid.split('.')[:-1])]
                print [s.sid for s in results.corpus.documents['.'.join(sid.split('.')[:-1])].sentences]
                sys.exit()
            sentence_results = self.process_sentence(sentence_output, sentence)
            for eid in sentence_results:
                results.entities[eid] = sentence_results[eid]
        logging.info("found {} entities".format(len(results.entities)))
        return results

    def process_sentence(self, out, sentence):
        sentence_entities = {}
        did = sentence.did
        sid = sentence.sid
        tagged_tokens = self.split_tag_tokens(out, sentence)
        new_entity = None
        for t in tagged_tokens:
            text, tag, token = t
            if tag.startswith("S"):
                single_entity = create_entity(tokens=[token],
                                                      sid=sid, did=did,
                                                      text=text, score=1, etype=self.etype)
                eid = sentence.tag_entity(start=token.start, end=token.end, etype=self.etype,
                                            entity=single_entity, source=self.path)
                single_entity.eid = eid
                #results.entities[eid] = single_entity # deepcopy
                sentence_entities[eid] = single_entity
                #logging.info("new single entity: {}".format(single_entity))
            elif tag.startswith("B"):
                new_entity = create_entity(tokens=[token],
                                                   sid=sid, did=did,
                                                   text=text, score=1, etype=self.etype)
            elif tag.startswith("I"):
                if not new_entity:
                    logging.info("starting with inside...")
                    new_entity = create_entity(tokens=[token],
                                                   sid=sid, did=did,
                                                   text=text, score=1, etype=self.etype)
                else:
                    new_entity.tokens += [token]
            elif tag.startswith("E"):
                if not new_entity:
                    new_entity = create_entity(tokens=[token],
                                               sid=sid, did=did,
                                               text=text,
                                               score=1, etype=self.etype)
                    logging.debug("started from a end: {0}".format(new_entity))
                else:
                    new_entity.tokens += [token]
                    new_entity.text= sentence.text[new_entity.tokens[0].start:new_entity.tokens[-1].end]
                    new_entity.end = new_entity.start + len(new_entity.text)
                    new_entity.dend = new_entity.dstart + len(new_entity.text)

                #logging.info("%s end: %s" % (new_entity.sid, str(new_entity)))
                #logging.debug("found the end: %s", ''.join([t.text for t in new_entity.tokens]))
                eid = sentence.tag_entity(start=new_entity.tokens[0].start,
                                          end=new_entity.tokens[-1].end, etype=self.etype,
                                          entity=new_entity, source=self.path)
                new_entity.eid = eid
                #results.entities[eid] = new_entity # deepcopy
                sentence_entities[eid] = new_entity
                new_entity = None
                try:
                    logging.debug("completed entity:{}".format(sentence_entities[eid]))
                except UnicodeDecodeError:
                    pass
        return sentence_entities

    def split_tag_tokens(self, data, sentence):
        """
        Separate StanfordNER tagget output into list of tuples (token, tag)
        :param data: SNER output
        :param sentence: sentence object
        :return:
        """
        tagged = []
        tindex = 0
        words = data.split(" ")
        # print data, words
        for t in words:
            # account for tokens with j/ - not necessary
            if t.strip() == "":
                # print "whitespace"
                continue
            # if t.count("/") > 1:
            #     print "more than 1 /: {}".format(t)
            # print t, sentence.tokens[tindex].text
            x = t.split("/")
            # print x, tindex, len(sentence.tokens), sentence.tokens[tindex].text
            match = (x[0], x[1], sentence.tokens[tindex])
            tagged.append(match)
            tindex += 1
        return tagged


    def load_tagger(self, port=9181):
        """
        Start the server process with the classifier
        :return:
        """
        # check if it already loaded (and then kill that instance)
        kill_process(port)
        self.port = port
        ner_args = ["java", self.RAM_TEST, "-Dfile.encoding=UTF-8", "-cp", self.STANFORD_NER, "edu.stanford.nlp.ie.NERServer",
                    "-port", str(port), "-loadClassifier", self.path + ".ser.gz",
                    "-tokenizerFactory", "edu.stanford.nlp.process.WhitespaceTokenizer", "-tokenizerOptions",
                    "tokenizeNLs=true"]
        logging.info(' '.join(ner_args))
        logging.info("Starting the server for {} on {}...".format(self.path, self.port))
        self.process = Popen(ner_args, stdin = PIPE, stdout = PIPE, stderr = PIPE, shell=False)
        while True:
            out = self.process.stderr.readline()
            if out and out != "":
                logging.info(out)
            if "done" in out:
                logging.info("loaded {}".format(self.path))
                break
        #out = ner.communicate("Structure-activity relationships have been investigated for inhibition of DNA-dependent protein kinase (DNA-PK) and ATM kinase by a series of pyran-2-ones, pyran-4-ones, thiopyran-4-ones, and pyridin-4-ones.")
        #logging.info(out)
        #print 'Success!!'
        atexit.register(self.kill_process)


def kill_process(port):
    # http://stackoverflow.com/a/14907802
    popen = Popen(['netstat', '-lpn'],
                             shell=False,
                             stdout=PIPE)
    (data, err) = popen.communicate()

    pattern = "^tcp.*((?:{0})).* (?P<pid>[0-9]*)/.*$"
    pattern = pattern.format(str(port))
    prog = re.compile(pattern)
    for line in data.split('\n'):
        match = re.match(prog, line)
        if match:
            pid = match.group('pid')
            logging.info("killing process {}".format(pid))
            Popen(['kill', '-9', pid])