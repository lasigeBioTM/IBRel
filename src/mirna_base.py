import argparse
import logging
from rdflib import URIRef, BNode, Literal, ConjunctiveGraph, Namespace
from rdflib.namespace import RDF, RDFS
from rdflib.plugins.sparql import prepareQuery
import time
import pprint
from fuzzywuzzy import process


def parse_mirbase(mirbase):
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

def create_graph(data, g):
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
        g.add((mirna_instance, RDF.type, mirna_class))
        label = Literal(mirna)
        g.add((mirna_instance, RDFS.label, label))
    return g


def map_label(label, g):
    choices = [str(l) for l in g.objects(predicate=RDFS.label)]
    result = process.extractOne(label, choices)
    print result
    return result

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
    path = "triples/mirbase.rdf"
    g = ConjunctiveGraph()
    g.open(path, create=False)

    if options.action == "create":
        g.open(path, create=True)
        with open("data/miRNA.dat") as datfile:
            mirbase = datfile.read().strip()
        mirbase_parsed = parse_mirbase(mirbase)
        graph = create_graph(mirbase_parsed, g)
        graph.serialize(path, format='pretty-xml')
        print 'Triples in graph after add: ', len(graph)
        graph.close()
    else:
        #g.open(path, create=False)
        g.load(path)
        print "Opened graph with {} triples".format(len(g))
        if options.action == "map":
            map_label(options.label, g)
        elif options.action == "geturi":
            q = prepareQuery('SELECT ?s WHERE { ?s rdfs:label ?label .}', initNs={"rdfs": RDFS })
            l = Literal(options.label)
            for row in g.query(q, initBindings={'label': l}):
                print row
        else:
            m = URIRef("http://www.mirbase.org/cgi-bin/mirna_entry.pl?acc=MI0017413")
            #for s, p, o in g:
            #    print s, p, o
            mirna_class = URIRef("http://purl.obolibrary.org/obo/SO_0000276")
            for row in g.query('select ?s where { ?s rdf:type [] .}'):
                print row.s

if __name__ == "__main__":
    main()
