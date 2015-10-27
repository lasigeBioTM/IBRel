import logging
from text.entity import Entity
from config import config

__author__ = 'Andre'

mirna_stopwords = set(["mediated", "expressing", "deficient", "transfected", "dependent", "family"])
# words that are never part of chemical entities
with open(config.stoplist, 'r') as stopfile:
    for l in stopfile:
        w = l.strip().lower()
        if w not in mirna_stopwords and len(w) > 1:
            mirna_stopwords.add(w)


class MirnaEntity(Entity):
    def __init__(self, tokens, *args, **kwargs):
        # Entity.__init__(self, kwargs)
        super(MirnaEntity, self).__init__(tokens, **kwargs)
        self.type = "mirna"
        self.subtype = kwargs.get("subtype")
        self.mirna_acc = None
        self.mirna_name = 0
        self.sid = kwargs.get("sid")

    def validate(self, ths, rules):
        """
        Use rules to validate if the entity was correctly identified
        :param rules:
        :return: True if entity does not fall into any of the rules, False if it does
        """
        # logging.debug("using these rules: {}".format(rules))
        if "stopwords" in rules:
            words = self.text.split(" ")
            stop = False
            for s in mirna_stopwords:
                if any([s == w.lower() for w in words]):
                    logging.debug("ignored stopword %s" % self.text)
                    stop = True
            if stop:
                return False
        return True