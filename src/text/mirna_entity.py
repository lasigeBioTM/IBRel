import logging

import re

from mirna_base import MirbaseDB, MIRBASE
from text.entity import Entity
from config import config
if config.use_go:
    from config.config import go_conn as db
__author__ = 'Andre'

mirna_stopwords = set(["mediated", "expressing", "deficient", "transfected", "dependent", "family", "specific", "null",
                       "independent", "dependant", "overexpressing", "binding", "targets", "induced"])
                       # "mirna", "mirnas", "mir", "hsa-mir"])

mirna_nextstopwords = set(["inhibitor"])
with open(config.stoplist, 'r') as stopfile:
    for l in stopfile:
        w = l.strip().lower()
        if w not in mirna_stopwords and len(w) > 1:
            mirna_stopwords.add(w)
mirna_stopwords.discard("let")
mirna_graph = MirbaseDB(config.mirbase_path)
mirna_graph.load_graph()

class MirnaEntity(Entity):
    def __init__(self, tokens, sid, *args, **kwargs):
        # Entity.__init__(self, kwargs)
        super(MirnaEntity, self).__init__(tokens, **kwargs)
        self.type = "mirna"
        self.subtype = kwargs.get("subtype")
        self.mirna_acc = None
        self.mirna_name = 0
        self.sid = sid
        self.nextword = kwargs.get("nextword")
        self.go_ids = []

    def validate(self, ths, rules, *args, **kwargs):
        self.normalize()
        """
        Use rules to validate if the entity was correctly identified
        :param rules:
        :return: True if entity does not fall into any of the rules, False if it does
        """
        # logging.debug("using these rules: {}".format(rules))
        # logging.debug("{}=>{}:{}".format(self.text.encode("utf-8"), self.normalized, self.normalized_score))
        final_entities = [self]
        words = self.text.split("-")
        '''if len(words) > 2 and len(words[-1]) > 3:
            logging.info("big ending: {}".format(self.text))
            self.text = '-'.join(words[:-1])
            words = words[:-1]
            return False'''
        if "stopwords" in rules:
            if self.text.lower() in ["mirna", "mirnas", "mir", "hsa-mir", "microrna", ]:
                logging.debug("ignored stopword %s" % self.text)
                return False
            stop = False
            for i, w in enumerate(words):
                if w.lower() in mirna_stopwords:
                    logging.debug("ignored stopword %s" % self.text)
                    self.text = '-'.join(words[:i])
                    self.dend -= len(words[i:])
                    self.end -= len(words[i:])
                    # stop = True
        if "nextstopword" in rules:
            if self.nextword in mirna_nextstopwords:
                logging.debug("ignored next stop word: {} {}".format(self.text, self.nextword))
                return False

        if "separate_mirnas" in rules:
            if "~" in self.text:  # mir cluster 23a~27a~24-2 => mir-23a, mir-27a, mir-24-2
                self.text = self.text.replace("~", ", ")
            x = self.text.split("-")
            if len(x) > 2 and x[-2].isdigit() and x[-1].isdigit() and len(x[-1]) == len(x[-2]):  # mir-221-222 => mir-221, mir-222
                self.text = x[0] + "-" + x[1] + "/" + x[2]
            elif len(x) == 4 and " " not in self.text:  # mir-15b-16-2
                # print "before lenx==3", self.text
                self.text = x[0] + "-" + x[1] + "/" + "-".join(x[2:])
                # print "after lenx==3", self.text
            elif "-" not in x[0] and "-" in self.text and x[0].lower().startswith("mir") and x[0][-1].isdigit(): #mir302-367
                    # print "mirXXX-XXX", self.text, x
                    self.text = self.text.replace("-", "/")
            if "/" in self.text:  # mir-192/215 => mir-192 + mir-215 | mir-34a/b/c => mir-34a, mir-34b, mir-34c
                newtext_separated = self.text.split("/")
                self.text = newtext_separated[0]
                self.normalize()
                logging.info("first element of sequence:" + self.text)
                for sep in newtext_separated[1:]:
                    # print "sep:", sep
                    logging.info("other element:" + sep)
                    if sep.isdigit():  # mir-192/215
                        # base = self.text.split("-")  # mir - ###
                        base = "mir"
                        entity2_text = base + "-" + sep
                        # print entity2_text
                        entity2 = MirnaEntity(self.tokens, self.sid, text=entity2_text)
                        entity2.normalize()
                        final_entities.append(entity2)
                    elif len(sep) == 1: # assuming mir-34a/b/c
                        entity2_text = self.text[:-1] + sep
                        # print entity2_text
                        entity2 = MirnaEntity(self.tokens, self.sid, text=entity2_text)
                        entity2.normalize()
                        final_entities.append(entity2)
            elif " and " in self.text or ", " in self.text:  # mir-200a, -200b, -200c, -141 and -429
                elems = re.split(' and |, ', self.text)  # mir-143 and -145 => mir-143, mir-145
                self.text = elems[0]
                self.normalize()
                # print self.text
                for sep in elems[1:]:
                    # print "and, separator:", sep
                    if sep.isalpha():  # mir-34 and c
                        entity2_text = self.text[:-1] + sep
                        entity2 = MirnaEntity(self.tokens, self.sid, text=entity2_text)
                        entity2.normalize()
                        final_entities.append(entity2)
                    else:
                        if not sep.startswith("-"):
                            sep = "-" + sep
                        if not sep.lower().startswith("mir"):
                            entity2_text = "mir" + sep
                        entity2 = MirnaEntity(self.tokens, self.sid, text=entity2_text)
                        entity2.normalize()
                        final_entities.append(entity2)
        # if self.text.startswith("MicroRNA-") or self.text.startswith("microRNA-"):
        #    self.text = "mir-" + "-".join(words[1:])
        """if len(words) > 1 and self.text[-1].isdigit() and self.text[-2].isalpha(): #let-7a1 -> let-7a-1
            self.text = self.text[:-1] + "-" + self.text[-1]
        if len(words) > 1 and words[-1].isdigit() and words[-2].isdigit(): # mir-371-373 -> mir-371
            self.text = "-".join(words[:-1])
        words = self.text.split("-")
        if len(words) > 2 and words[2].isalpha() and words[1].isdigit(): # mir-133-a-1 -> mir-133a-1
            # logging.info(words)
            self.text = words[0] + "-" + words[1] + words[2]
            if len(words) > 3:
                self.text += "-" + '-'.join(words[3:])
            logging.info('-'.join(words) + " -> " + self.text)"""
        # print [(e.text, e.normalized) for e in final_entities]
        return final_entities

    def normalize(self):
        if self.text.isalpha():
            # print "normalizing", self.text, "to microrna"
            self.normalized = "microrna"
            self.normalized_score = 100
            self.normalized_ref = "text"
            self.go_ids = []
            self.best_go = ""
        elif len(self.text) > 0:
            self.normalized, self.normalized_score= mirna_graph.map_label(self.text)
            if self.normalized_score < 99:
                self.normalized = self.text
                self.normalized_score = 0
                self.normalized_ref = "text"
            else:
                self.normalized_ref = "mirbase"
        else:
            self.normalized = self.text
            self.normalized_score = 0
            self.normalized_ref = "text"

            # base_mirna = mirna_graph.labels[self.normalized]
            # print base_mirna
            # for go in mirna_graph.g.objects(base_mirna, MIRBASE["goa"]):
            #     # print str(go)
            #     self.go_ids.append(str(go))
            # if len(self.go_ids) > 0:
            #     self.get_best_go()
            # else:
            #     self.best_go = ""
        try:
            logging.info("{}=>{}:{}".format(self.text, self.normalized, self.normalized_score))
        except:
            pass

    def get_best_go(self):
        cur = db.cursor()
        # synonym

        query = """SELECT DISTINCT t.acc, t.name, t.ic
                       FROM term t
                       WHERE t.acc IN (%s)
                       ORDER BY t.ic ASC
                       LIMIT 1;"""  # or DESC
        # print "QUERY", query


        format_strings = ','.join(['%s'] * len(self.go_ids))
        cur.execute(query % format_strings, (self.go_ids))
        res = cur.fetchone()
        if res is not None:
            # print self.text, res[1:]
            logging.info("best GO for {} ({}): {}".format(self.text, len(self.go_ids), " ".join([str(r) for r in res])))
            self.best_go = res[0]
        else:
            logging.info("NO GO")
            self.best_go = ""

