import logging
import sys
import itertools
import re
from classification.re.kernelmodels import KernelModel
from classification.results import ResultsRE


class RuleClassifier(KernelModel):
    def __init__(self, corpus, rules=["same_line", "list_items", "dist", "same_text", "all"]):
        """
        Rule based classifier
        rules: List of rules to use
        """
        self.rules = rules
        self.corpus = corpus
        self.pairs = {}
        self.pids = {}
        self.words = set(["of", "the", "and", "a", "with", "to", "was", "in", "for", "on", "colon", "which", "cm", "mass", "grade", "from", "is", "that", "no"])


    def load_classifier(self):
        pass

    def test(self):
        for i, did in enumerate(self.corpus.documents):
            if "path" in did:
                continue
            doc_entities = []
            pcount = 0
            logging.info("{} {}/{}".format(did, i, len(self.corpus.documents)))
            for sentence in self.corpus.documents[did].sentences:
                if 'goldstandard' in sentence.entities.elist:
                    sentence_entities = [entity for entity in sentence.entities.elist["goldstandard"]]
                    # logging.debug("sentence {} has {} entities ({})".format(sentence.sid, len(sentence_entities), len(sentence.entities.elist["goldstandard"])))
                    doc_entities += sentence_entities
            for pair in itertools.combinations(doc_entities, 2):
                pid = did + ".p" + str(pcount)
                if pair[0].dstart < pair[1].dstart:
                    e1 = pair[0]
                    e2 = pair[1]
                else:
                    e1 = pair[1]
                    e2 = pair[0]
                self.pids[pid] = pair
                sid1 = e1.sid
                sid2 = e2.sid
                sentence1 = self.corpus.documents[did].get_sentence(e1.sid)
                sentence2 = self.corpus.documents[did].get_sentence(e2.sid)
                self.pairs[pid] = 0
                # if sid1 != sid2:
                #     self.pairs[pair.pid] = -1
                # if the two entities are mentioned in the same line, assume it's true
                # if e1.text.upper() == "HISTORY":
                    # print e1.text.upper(), sentence2.text[1], e2.text, self.corpus.documents[did].text[e1.dstart:e2.dend]
                    # print e2.text, "=>", sentence2.text
                    # print "###", self.corpus.documents[did].text[e1.dstart:e2.dend]
                between_text = self.corpus.documents[did].text[e1.dstart:e2.dend]
                if "\n" not in between_text: # same line
                    #if int(e1.eid.split("e")[-1])+1 == int(e2.eid.split("e")[-1]):
                    #    self.pairs[pid] += 1
                    if e2.dstart - e1.dend < 50:
                        self.pairs[pid] += 1
                if re.match(".*\s\d+\s.*", between_text):
                    self.pairs[pid] += 1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
                elif "[end" not in between_text:
                    if e1.text.upper() == "HISTORY" and (sentence2.text[1] == "." or sentence2.text[1] == ")"):
                        self.pairs[pid] += 1
                        # print self.corpus.documents[did].text[e1.dstart:e2.dend]
                    # elif len(sentence2.text) < 20:
                    #     self.pairs[pid] += 1
                    #elif e2.dstart - e1.dend < 10:
                    #     self.pairs[pid] += 1

                pcount += 1



    def get_predictions(self, corpus):
        results = ResultsRE("")
        for p, pid in enumerate(self.pids):
            if self.pairs[pid] < 1:
                # pair.recognized_by["rules"] = -1
                pass
            else:
                did = pid.split(".")[0]
                pair = corpus.documents[did].add_relation(self.pids[pid][0], self.pids[pid][1], "tlink", relation=True)
                #pair = self.get_pair(pid, corpus)
                results.pairs[pid] = pair
                pair.recognized_by["rules"] = 1
                logging.info("{0.eid}:{0.text} => {1.eid}:{1.text}".format(pair.entities[0],pair.entities[1]))
            #logging.info("{} - {} SST: {}".format(pair.entities[0], pair.entities[0], score))
        results.corpus = corpus
        return results



