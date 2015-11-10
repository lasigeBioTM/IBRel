import logging

from config import config
from text.entity import Entity

__author__ = 'Andre'
prot_words = set()
prot_stopwords = set(["chromosome", "factor", "conserved"])
# words that may seem like they are not part of named chemical entities but they are

# words that are never part of chemical entities
with open(config.stoplist, 'r') as stopfile:
    for l in stopfile:
        w = l.strip().lower()
        if w not in prot_words and len(w) > 1:
            prot_stopwords.add(w)


class ProteinEntity(Entity):
    def __init__(self, tokens, *args, **kwargs):
        # Entity.__init__(self, kwargs)
        super(ProteinEntity, self).__init__(tokens, *args, **kwargs)
        self.type = "protein"
        self.subtype = kwargs.get("subtype")
        # print self.sid


    def get_dic(self):
        dic = super(ProteinEntity, self).get_dic()
        dic["subtype"] = self.subtype
        dic["ssm_score"] = self.ssm_score
        dic["ssm_entity"] = self.ssm_go_ID
        return dic

    def validate(self, ths, rules):
        """
        Use rules to validate if the entity was correctly identified
        :param rules:
        :return: True if entity does not fall into any of the rules, False if it does
        """
        if "stopwords" in rules:
            if self.text.lower().startswith("mir-") or self.text.lower().startswith("microrna"):
                logging.debug("mirna %s" % self.text)
                return False
            words = self.text.split(" ")
            words += self.text.split("-")
            stop = False
            for s in prot_stopwords:
                if any([s == w.lower() for w in words]):
                    logging.debug("ignored stopword %s" % self.text)
                    stop = True
            if stop:
                return False
        if not self.text[0].isalpha():
            logging.debug("not alpha %s" % self.text)
            return False
        return True