from __future__ import unicode_literals
import os
import logging
import sys
from classification.rext.kernelmodels import ReModel
from subprocess import Popen, PIPE
import platform
import itertools
import codecs
from classification.results import ResultsRE


class JSREKernel(ReModel):

    def __init__(self, corpus, relationtype, modelname="slk_classifier.model"):
        super(JSREKernel, self).__init__()
        self.modelname = modelname
        self.test_jsre = []
        self.pairs = {}
        self.generatejSREdata(corpus, modelname, pairtypes=relationtype)

    def load_classifier(self, inputfile="slk_classifier.model.txt", outputfile="jsre_results.txt"):
        if os.path.isfile(self.temp_dir + outputfile):
            os.remove(self.temp_dir + outputfile)
        if not os.path.isfile(self.basedir + self.modelname):
            print "model", self.basedir + self.modelname, "not found"
            sys.exit()
        if platform.system() == "Windows":
            sep = ";"
        else:
            sep = ":"
        #logging.debug("testing %s with %s to %s", temp_dir + inputfile,
        #              basedir + model, temp_dir + outputfile)
        libs = ["libsvm-2.8.jar", "log4j-1.2.8.jar", "commons-digester.jar", "commons-beanutils.jar", "commons-logging.jar", "commons-collections.jar"]
        classpath = 'bin/jsre/jsre-1.1/bin'+ sep + sep.join(["bin/jsre/jsre-1.1/lib/" + l for l in libs])
        self.test_jsre = ['java', '-mx4g', '-classpath', classpath, "org.itc.irst.tcc.sre.Predict",
                          self.temp_dir + inputfile, self.basedir + self.modelname, self.temp_dir + outputfile]
        #print ' '.join(jsrecommand)

    def train(self):
        if os.path.isfile(self.basedir + self.modelname):
            print "removed old model"
            os.remove(self.basedir + self.modelname)
        if not os.path.isfile(self.temp_dir + self.modelname  + ".txt"):
            print "could not find training file " + self.basedir + self.modelname + ".txt"
            sys.exit()
        if platform.system() == "Windows":
            sep = ";"
        else:
            sep = ":"
        libs = ["libsvm-2.8.jar", "log4j-1.2.8.jar", "commons-digester.jar", "commons-beanutils.jar",
                "commons-logging.jar", "commons-collections.jar"]
        classpath = 'bin/jsre/jsre-1.1/bin/' + sep + sep.join(["bin/jsre/jsre-1.1/lib/" + l for l in libs])
        jsrecall = ['java', '-mx3g', '-classpath', classpath, "org.itc.irst.tcc.sre.Train",
                          "-k",  "SL", "-n", "4", "-w", "3", "-m", "3072", #  "-c", str(1),
                          self.temp_dir + self.modelname + ".txt", self.basedir + self.modelname]
        print " ".join(jsrecall)
        jsrecall = Popen(jsrecall, stdout=PIPE, stderr=PIPE)
        res  = jsrecall.communicate()
        if not os.path.isfile(self.basedir + self.modelname):
            print "error with jsre! model file was no created"
            print res[1]
            sys.exit()
        else:
            statinfo = os.stat(self.basedir + self.modelname)
            if statinfo.st_size == 0:
                print "error with jsre! model has 0 bytes"
                print res[0]
                print res[1]
                sys.exit()
        #logging.debug(res)


    def test(self, outputfile="jsre_results.txt"):
        print " ".join(self.test_jsre)
        jsrecall = Popen(self.test_jsre, stdout=PIPE, stderr=PIPE)
        res = jsrecall.communicate()
        #logging.debug(res[0].strip().split('\n')[-2:])
        #os.system(' '.join(jsrecommand))
        if not os.path.isfile(self.temp_dir + outputfile):
            print "something went wrong with JSRE!"
            print res
            sys.exit()
        logging.debug("done.")

    def get_sentence_instance(self, sentence, e1id, e2id, pair):
        tokens = [t for t in sentence.tokens]
        tokens_text = [t.text for t in tokens]
        pos = [t.pos for t in tokens]
        lemmas = [t.lemma for t in tokens]
        ner = [t.tag for t in tokens]
        #logging.debug("{} {} {} {}".format(len(tokens1), len(pos), len(lemmas), len(ner)))
        return self.blind_all_entities(tokens_text, sentence.entities.elist["goldstandard"],
                                       [e1id, e2id], pos, lemmas, ner)

    def generatejSREdata(self, corpus, savefile, train=False, pairtypes=("mirna", "protein")):
        if os.path.isfile(self.temp_dir + savefile + ".txt"):
            print "removed old data"
            os.remove(self.temp_dir + savefile + ".txt")
        examplelines = []
        # get all entities of this document
        # doc_entities = []
        pcount = 0
        truepcount = 0
        for sentence in corpus.get_sentences("goldstandard"):
            examplelines = []
            sentence_entities = [entity for entity in sentence.entities.elist["goldstandard"]]
            # logging.debug("sentence {} has {} entities ({})".format(sentence.sid, len(sentence_entities), len(sentence.entities.elist["goldstandard"])))
            for pair in itertools.combinations(sentence_entities, 2):
                if pair[0].type == pairtypes[0] and pair[1].type == pairtypes[1] or pair[1].type == pairtypes[0] and pair[0].type == pairtypes[1]:
                    # logging.debug(pair)
                    if pair[0].type == pairtypes[0]:
                        e1id = pair[0].eid
                        e2id = pair[1].eid
                    else:
                        e1id = pair[1].eid
                        e2id = pair[0].eid
                        pair = (pair[1], pair[0])
                    pid = sentence.did + ".p" + str(pcount)
                    # self.pairs[pid] = (e1id, e2id)
                    self.pairs[pid] = pair
                    # sentence1 = corpus.documents[did].get_sentence(pair[0].sid)
                    #sentence1 = sentence
                    # logging.info("{}  {}-{} => {}-{}".format(sentence.sid, e1id, pair[0].text, e2id, pair[1].text))
                    tokens_text, pos, lemmas, ner = self.get_sentence_instance(sentence, e1id, e2id, pair)

                    # logging.debug("{} {} {} {}".format(len(pair_text), len(pos), len(lemmas), len(ner)))
                    #logging.debug("generating jsre lines...")
                    #for i in range(len(pairinstances)):
                        #body = generatejSRE_line(pairinstances[i], pos, stems, ner)
                    if pair[0].sid != pair[1].sid:
                        sentence2 = corpus.documents[sentence.did].get_sentence(pair[1].sid)
                        tokens_text2, pos2, lemmas2, ner2 = self.get_sentence_instance(sentence2, e1id, e2id, pair)
                        tokens_text += tokens_text2
                        pos += pos2
                        ner += ner2
                        lemmas += lemmas2

                    trueddi = 0
                    if e2id in pair[0].targets:
                        trueddi = 1
                        truepcount += 1
                    body = self.generatejSRE_line(tokens_text, pos, lemmas, ner)
                    examplelines.append(str(trueddi) + '\t' + pid + '.i' + '0\t' + body + '\n')
                    pcount += 1
            logging.debug("writing {} lines to file...".format(len(examplelines)))
            with codecs.open(self.temp_dir + savefile + ".txt", 'a', "utf-8") as trainfile:
                for l in examplelines:
                    #print l
                    trainfile.write(l)
                # logging.info("wrote " + temp_dir + savefile)
        logging.info("True/total relations:{}/{} ({})".format(truepcount, pcount, str(1.0*truepcount/pcount)))

    def generatejSRE_line(self, pairtext, pos, lemmas, ner):
        candidates = [False,False]
        body = ''
        elements = []
        for it in range(len(pairtext)):
            #for it in range(len(pairtext)):
            if pairtext[it] == "#candidatea#":
                #print pairtext[i],
                tokentype = 'ENTITY'
                #tokentype = etypes[0]
                tokenlabel = 'A'
                candidates[0] = True
                #tokentext = "#candidate#"
                #tokentext = entitytext[0]
                tokentext = pairtext[it].lstrip()
                lemma = tokentext
            elif pairtext[it] == "#candidateb#":
                #print pairtext[i]
                tokentype = 'ENTITY'
                #tokentype = etypes[0]
                tokenlabel = 'T'
                #tokentext = "#candidate#"
                tokentext = pairtext[it].lstrip()
                #tokentext = entitytext[1]
                lemma = tokentext
                candidates[1] = True
            elif pairtext[it] == "#entity#":
                tokentype = 'DRUG'
                tokenlabel = 'O'
                tokentext = pairtext[it].lstrip()
                lemma = tokentext
            else:
                # logging.debug("{}".format(pairtext[it].lstrip()))
                tokentype = ner[it]
                tokenlabel = 'O'
                tokentext = pairtext[it].lstrip()
                lemma = lemmas[it]
                if tokentext == '-RRB-':
                    tokentext = ')'
                    lemma = ')'
                elif tokentext == '-LRB-':
                    tokentext = '('
                    lemma = '('
            #if ' ' in pairtext[it][0].lstrip() or '\n' in pairtext[it][0].lstrip():
            #    print "token with spaces!"
            #    print pairs[pair][ddi.PAIR_TOKENS][it][0].lstrip()
            #    sys.exit()

            elements.append("&&".join([str(it), tokentext,
                              lemma,
                              pos[it],
                              tokentype, tokenlabel]))

        #logging.debug("%s\t%s\t%s", str(trueddi), pair, body)
        if not candidates[0]:
            logging.debug("missing first candidate on pair ")
            elements = ["0&&#candidate#&&#candidate#&&-None-&&ENTITY&&T"] + [str(n+1) + e[1:] for n, e in enumerate(elements)]
            # print elements
        if not candidates[1]:
            logging.debug("missing second candidate on pair")
            elements.append(str(it+1) + "&&#candidate#&&#candidate#&&-None-&&ENTITY&&T")
            # print elements
        body = " ".join(elements)
        return body

    def get_predictions(self, corpus, examplesfile="slk_classifier.model.txt", resultfile="jsre_results.txt"):
        #pred_y = []
        with open(self.temp_dir + resultfile, 'r') as resfile:
            pred = resfile.readlines()

        with codecs.open(self.temp_dir + examplesfile, 'r', 'utf-8') as trainfile:
            original = trainfile.readlines()

        if len(pred) != len(original):
            print "different number of predictions!"
            sys.exit()
        results = ResultsRE(resultfile)
        temppreds = {}
        for i in range(len(pred)):
            original_tsv = original[i].split('\t')
            # logging.debug(original_tsv)
            pid = '.'.join(original_tsv[1].split('.')[:-1])
            #if pid not in pairs:
            #    print "pair not in pairs!"
            #    print pid
            #    print pairs
            #    sys.exit()
            #confirm that everything makes sense
            # true = float(original_tsv[0])
            # if true == 0:
            #    true = -1

            p = float(pred[i].strip())
            if p == 0:
                p = -1
            if p == 2:
                print "p=2!"
                p = 1
            if p == 1:
                did = '.'.join(pid.split(".")[:-1])
                pair = corpus.documents[did].add_relation(self.pairs[pid][0], self.pairs[pid][1], "pair", relation=True)
                #pair = self.get_pair(pid, corpus)
                results.pairs[pid] = pair

                # logging.debug("{} - {} SLK: {}".format(pair.entities[0], pair.entities[1], p))
                #if pair not in temppreds:
                #    temppreds[pair] = []
                #temppreds[pair].append(p)
                results.pairs[pid].recognized_by["jsre"] = p
        '''for pair in temppreds:
            if relations.SLK_PRED not in pairs[pair]:
                pairs[pair][relations.SLK_PRED] = {}
            p = mode(temppreds[pair])[0][0]
            if len(set(temppreds[pair])) > 1:
                print temppreds[pair], p
            pairs[pair][relations.SLK_PRED][dditype] = p
            #if pairs[pair][ddi.SLK_PRED][dditype] and not pairs[pair][ddi.SLK_PRED]["all"]:
            #    logging.info("type classifier %s found a new true pair: %s", dditype, pair)

        for pair in pairs:
            if relations.SLK_PRED not in pairs[pair]:
                pairs[pair][relations.SLK_PRED] = {}
            if dditype not in pairs[pair][relations.SLK_PRED]:
                 pairs[pair][relations.SLK_PRED][dditype] = -1'''
        results.corpus = corpus
        return results
