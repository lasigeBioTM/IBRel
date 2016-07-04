import logging

from mirna_base import MirbaseDB, MIRBASE
from text.entity import Entity
from config import config
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
logging.info("Loading miRbase...")
mirna_graph = MirbaseDB(config.mirbase_path)
mirna_graph.load_graph()
logging.info("done.")

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
        self.normalize()

    def validate(self, ths, rules, *args, **kwargs):
        """
        Use rules to validate if the entity was correctly identified
        :param rules:
        :return: True if entity does not fall into any of the rules, False if it does
        """
        # logging.debug("using these rules: {}".format(rules))
        # logging.debug("{}=>{}:{}".format(self.text.encode("utf-8"), self.normalized, self.normalized_score))
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

        return True

    def normalize(self):
        if self.text.isalpha():
            self.normalized = "microrna"
            self.normalized_score = 100
            self.normalized_ref = "text"
            self.go_ids = []
            self.best_go = ""
        else:
            self.normalized, self.normalized_score= mirna_graph.map_label(self.text)
            self.normalized_ref = "mirbase"

            base_mirna = mirna_graph.labels[self.normalized]
            # print base_mirna
            for go in mirna_graph.g.objects(base_mirna, MIRBASE["goa"]):
                # print str(go)
                self.go_ids.append(str(go))
            if len(self.go_ids) > 0:
                self.get_best_go()
            else:
                self.best_go = ""
        logging.info("{}=>{}:{}".format(self.text.encode("utf-8"), self.normalized, self.normalized_score))

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

