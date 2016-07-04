from __future__ import unicode_literals

import codecs
import logging
import sys
import itertools
import re
from subprocess import Popen, PIPE

import config.seedev_types
from classification.rext.kernelmodels import ReModel
from classification.results import ResultsRE
from config import config
from text.pair import Pairs


class MirtexClassifier(ReModel):
    def __init__(self, corpus, ptype):
        """
        Rule based classifier
        rules: List of rules to use
        """
        self.ptype = ptype
        self.corpus = corpus
        self.pairs = {}
        self.pids = {}
        self.trigger_words = {}
        self.tregexes_agent = set()
        self.tregexes_theme = set()
        with open("corpora/miRTex/trigger_words.csv", 'r') as tfile:
            for l in tfile:
                csv = l.split(";")
                if csv[0].strip() != "":
                    tword = csv[0].strip()
                    pos = csv[1].strip()
                    if tword not in self.trigger_words:
                        self.trigger_words[tword] = set()
                    self.trigger_words[tword].add(pos)
        # print self.trigger_words
        with open("corpora/miRTex/tregexes.csv", 'r') as tfile:
            for l in tfile:
                csv = l.split(";")
                if csv[0].strip() != "":
                    if csv[0].startswith("agent"):
                        self.tregexes_agent.add(csv[1].strip())
                    elif csv[0].startswith("theme"):
                        self.tregexes_theme.add(csv[1].strip())
        # print self.tregexes_agent, self.tregexes_theme


    def load_classifier(self):
        pass


    def test(self):
        for sentence in self.corpus.get_sentences("goldstandard_mirna"):
            if "goldstandard_protein" in sentence.entities.elist:
                #print sentence.parsetree.replace("\n", "").replace("  ", "")
                # print sentence.sid, sentence.text

                sentence_mirnas = {e.text: e for e in sentence.entities.elist["goldstandard_mirna"]}
                sentence_genes = {e.text: e for e in sentence.entities.elist["goldstandard_protein"]}
                #write parse tree to file
                with open("temp/tregex_sentence.txt", 'w') as tfile:
                    tfile.write(sentence.parsetree.replace("\n", "").replace("  ", ""))
                mirna_to_triggers = {} #mirna-> target for this sentence, assuming each mirna has
                # test each regex for agent (mirna)
                for tr in self.tregexes_agent:
                    tregexcall = Popen(["./bin/stanford-tregex-2015-12-09/tregex.sh", "-h", "tr", "-h", "arg", "-t", tr,
                                        "temp/tregex_sentence.txt"],
                                       stdout=PIPE, stderr=PIPE)
                    res = tregexcall.communicate()
                    if res[0] != "":
                        # print tr, "agent:", res[0]
                        for r in res[0].split("\n"): # each match
                            if r.strip() != "":
                                words = [w.split("/")[0] for w in r.split()] #just words, without POS
                                pos = [w.split("/")[1] for w in r.split()] # just POS
                                #assumption: each mirna and trigger appear only once in the sentence
                                #TODO check if the same mirna and trigger appear multiple times in the same sentence
                                mirna_agent = set(words) & set(sentence_mirnas.keys()) # mirnas found
                                mirna_trigger = set(words) & set(self.trigger_words.keys()) # triggers found
                                if mirna_agent and mirna_trigger:
                                    for trigger in mirna_trigger:
                                        trigger_i = words.index(trigger)
                                        if pos[trigger_i] not in self.trigger_words[trigger]:
                                            print "skipped because POS did not match:", r
                                            continue
                                        if trigger not in mirna_to_triggers:
                                            mirna_to_triggers[trigger] = set()
                                        for m in mirna_agent:
                                            mirna_to_triggers[trigger].add(m)
                                else:
                                    continue
                    else:
                        continue
                if not mirna_to_triggers:
                    continue
                # print mirna_targets
                for tr in self.tregexes_theme:
                    tregexcall = Popen(["./bin/stanford-tregex-2015-12-09/tregex.sh", "-h", "tr", "-h", "arg", "-t", tr,
                                        "temp/tregex_sentence.txt"],
                                       stdout=PIPE, stderr=PIPE)
                    res = tregexcall.communicate()
                    if res[0] != "":
                        # print tr, "theme:", res[0]
                        for r in res[0].split("\n"):
                            if r.strip() != "":
                                words = [w.split("/")[0] for w in r.split()]
                                pos = [w.split("/")[1] for w in r.split()]  # just POS
                                gene_agent = set(words) & set(sentence_genes.keys())
                                gene_trigger = set(words) & set(self.trigger_words.keys())
                                if gene_agent and gene_trigger:
                                    for trigger in gene_trigger:
                                        # print "target:", target
                                        trigger_i = words.index(trigger)
                                        if pos[trigger_i] not in self.trigger_words[trigger]:
                                            print "skipped because POS did not match:", r
                                            continue
                                        if trigger in mirna_to_triggers:
                                            for gene in gene_agent:
                                                print "+".join(mirna_to_triggers[trigger]), trigger, gene
                                                for mirna in mirna_to_triggers[trigger]:
                                                    self.pids["p{}".format(len(self.pids))] = (sentence_mirnas[mirna],
                                                                                                 sentence_genes[gene])

                                    # print gene_agent, gene_target
                        #sys.exit()
            # print


    def get_predictions(self, corpus):
        results = ResultsRE("")
        # print len(self.pids)
        for p, pid in enumerate(self.pids):
            did = self.pids[pid][0].did
            if did not in results.document_pairs:
                results.document_pairs[did] = Pairs()
            pair = corpus.documents[did].add_relation(self.pids[pid][0], self.pids[pid][1], self.ptype, relation=True)
            # print pair, pair[0], pair[1]
            #pair = self.get_pair(pid, corpus)
            results.document_pairs[did].add_pair(pair, "mirtex_rules")
            results.pairs[pid] = pair
            pair.recognized_by["mirtex_rules"] = 1
            logging.info("{0.eid}:{0.text} => {1.eid}:{1.text}".format(pair.entities[0],pair.entities[1]))
        #logging.info("{} - {} SST: {}".format(pair.entities[0], pair.entities[0], score))
        results.corpus = corpus
        return results



