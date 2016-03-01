import logging
import re
from config import config
from text.entity import Entity

__author__ = 'Andre'
prot_words = set()
prot_stopwords = set(["chromosome", "factor", "conserved", "gene", "anti", "mir", "regulatory", "terminal", "element",
                      "activator", "cell", "box", "transcriptional", "transcription", "growth", "talk", "epithelial",
                      "alpha", "microrna", "chip", "chipseq", "interferons", "tweak", "allele"])
# words that may seem like they are not part of named chemical entities but they are

# words that are never part of chemical entities
with open(config.stoplist, 'r') as stopfile:
    for l in stopfile:
        w = l.strip().lower()
        if w not in prot_words and len(w) > 1:
            prot_stopwords.add(w)


class ProteinEntity(Entity):
    def __init__(self, tokens, sid, *args, **kwargs):
        # Entity.__init__(self, kwargs)
        super(ProteinEntity, self).__init__(tokens, *args, **kwargs)
        self.type = "protein"
        self.subtype = kwargs.get("subtype")
        self.sid = sid

    tf_regex = re.compile(r"\A[A-Z]+\d*\w*\d*\Z")

    def get_dic(self):
        dic = super(ProteinEntity, self).get_dic()
        dic["subtype"] = self.subtype
        dic["ssm_score"] = self.ssm_score
        dic["ssm_entity"] = self.ssm_go_ID
        return dic

    def validate(self, ths, rules, *args, **kwargs):
        """
        Use rules to validate if the entity was correctly identified
        :param rules:
        :return: True if entity does not fall into any of the rules, False if it does
        """
        if "stopwords" in rules:
            words = self.text.split(" ")
            words += self.text.split("-")
            stop = False
            for s in prot_stopwords:
                if any([s == w.lower() for w in words]):
                    logging.debug("ignored stopword %s" % self.text)
                    stop = True
            if stop:
                return False
        if "alpha" in rules and not self.text[0].isalpha():
            logging.debug("not alpha %s" % self.text)
            return False
        if "nwords" in rules:
            words = self.text.split(" ")
            if len(words) > 1:
                return False
        if "codeonly" in rules:
            if self.tf_regex.match(self.text) is None:
                return False
        if "fixdash" in rules:
            self.text = self.text.replace("-", "")
        return True