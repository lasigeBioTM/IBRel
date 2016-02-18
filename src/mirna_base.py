import argparse
import logging
from rdflib import URIRef, BNode, Literal, ConjunctiveGraph, Namespace
from rdflib.namespace import RDF, RDFS
from rdflib.plugins.sparql import prepareQuery
import time
import pprint
from fuzzywuzzy import process
from config import config

class MirbaseDB(object):
    def __init__(self, db_path):
        self.g = ConjunctiveGraph()
        self.path = db_path
        self.choices = set()

    def create_graph(self):
        self.g.open(self.path, create=True)
        with open("data/miRNA.dat") as datfile:
            mirbase = datfile.read().strip()
        data = self.parse_mirbase(mirbase)
        #g = ConjunctiveGraph(store="SPARQLUpdateStore")
        ns = Namespace("http://www.mirbase.org/cgi-bin/mirna_entry.pl?acc=")
        # g.bind()
        mirna_class = URIRef("http://purl.obolibrary.org/obo/SO_0000276")
        for mirna in data:
            if "AC" not in  data[mirna]:
                print "NO AC", mirna, data[mirna].keys()
                continue
            acc = data[mirna]["AC"][0][:-1]
            mirna_instance = URIRef(ns + str(acc))
            self.g.add((mirna_instance, RDF.type, mirna_class))
            label = Literal(mirna)
            self.g.add((mirna_instance, RDFS.label, label))


    def parse_mirbase(self, mirbase):
        mirna_dic = {}
        mirnas = mirbase.strip().split(r"//")
        for m in mirnas:
            if len(m) > 0:
                props = m.strip().split("\nXX\n")
                mirname = props[0].split()[1]
                if not mirname.startswith("hsa"):
                    continue
                mirna_dic[mirname] = {}
                for p in props[1:]:
                    plines = p.split("\n")
                    if p.startswith("SQ"):
                        # print p
                        mirna_dic[mirname]["SQ"] = []
                        for l in plines[1:]:
                            seqs = l.split()
                            for s in seqs:
                                if s.isalpha():
                                    mirna_dic[mirname]["SQ"].append(s)
                    elif p.startswith("FH"):
                        current_location = ""
                        for l in plines[1:]:
                            values = l.split()
                            if l.startswith("FH"):
                                continue
                            if values[1] == "miRNA":
                                current_location = values[2]
                                mirna_dic[mirname][current_location] = {}
                            elif values[1] == "modified_base":
                                continue
                            elif current_location != "":
                                if "=" not in values[1]:
                                    continue
                                prop = values[1].split("=")
                                prop_name = prop[0][1:]
                                mirna_dic[mirname][current_location][prop_name] = prop[1][1:-1]
                    else:
                        for l in plines:
                            if len(l) > 0:
                                values = l.split()
                                if values[0].startswith("R"):
                                    continue
                                if values[0] not in mirna_dic[mirname]:
                                    mirna_dic[mirname][values[0]] = []
                                mirna_dic[mirname][values[0]].append(" ".join(values[1:]))
        return mirna_dic

    def map_label(self, label):
        result = process.extractOne(label, self.choices)
        # result = process.extract(label, choices, limit=3)
        if result[1] != 100:
            print label, result
            if label[-1].isdigit():
                label += "a"
            else:
                label += "-1"
            result = process.extractOne(label, self.choices)
            if result[1] != 100:
                if label[-1].isdigit():
                    label += "a"
                else:
                    label += "-1"
                    result = process.extractOne(label, self.choices)
            print "revised:", label, result
        return result


    def load_graph(self):
        self.g.load(self.path)
        print "Opened graph with {} triples".format(len(self.g))
        self.choices = [str(l) for l in self.g.objects(predicate=RDFS.label)]

    def save_graph(self):
        self.g.serialize(self.path, format='pretty-xml')
        print 'Triples in graph after add: ', len(self.g)
        self.g.close()

def main():
    start_time = time.time()
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("action", default="create",  help="Actions to be performed.")
    parser.add_argument("--log", action="store", dest="loglevel", default="WARNING", help="Log level")
    parser.add_argument("--label", action="store", dest="label")
    options = parser.parse_args()

    # set logger
    numeric_level = getattr(logging, options.loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % options.loglevel)
    while len(logging.root.handlers) > 0:
        logging.root.removeHandler(logging.root.handlers[-1])
    logging_format = '%(asctime)s %(levelname)s %(filename)s:%(lineno)s:%(funcName)s %(message)s'
    logging.basicConfig(level=numeric_level, format=logging_format)
    logging.getLogger().setLevel(numeric_level)
    total_time = time.time() - start_time
    logging.info("Total time: %ss" % total_time)
    pp = pprint.PrettyPrinter(indent=2)
    path = config.mirbase_path


    mirbase = MirbaseDB(path)
    if options.action == "create":
        mirbase.create_graph()
        mirbase.save_graph()
    else:
        mirbase.load()
        if options.action == "map":
            mirbase.map_label(options.label)
        elif options.action == "geturi":
            q = prepareQuery('SELECT ?s WHERE { ?s rdfs:label ?label .}', initNs={"rdfs": RDFS })
            l = Literal(options.label)
            for row in mirbase.g.query(q, initBindings={'label': l}):
                print row
        else:
            m = URIRef("http://www.mirbase.org/cgi-bin/mirna_entry.pl?acc=MI0017413")
            #for s, p, o in g:
            #    print s, p, o
            mirna_class = URIRef("http://purl.obolibrary.org/obo/SO_0000276")
            for row in mirbase.query('select ?s where { ?s rdf:type [] .}'):
                print row.s

if __name__ == "__main__":
    main()
