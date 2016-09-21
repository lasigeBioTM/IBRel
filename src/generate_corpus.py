import requests
import logging
import xml.etree.ElementTree as ET
import codecs
import os
import sys
import pickle
from time import sleep
from pycorenlp import StanfordCoreNLP

import config.corpus_paths
from classification.ner.matcher import MatcherModel
from config import config
from postprocessing import ssm
from reader import pubmed
from text.corpus import Corpus
from text.document import Document


def get_pubmed_abstracts(terms, corpus_text_path, negative_pmids):
    # searchterms = "+".join([t + "[mesh]" for t in terms])
    searchterms = '(("cystic fibrosis"[MeSH Terms] OR ("cystic"[All Fields] AND "fibrosis"[All Fields]) OR "cystic fibrosis"[All Fields])\
                   AND ("micrornas"[MeSH Terms] OR "micrornas"[All Fields] OR "mirna"[All Fields])) AND ("2011/09/04"[PDat] : "2016/09/01"[PDat])'
    query = {"term": "{}+hasabstract[text]".format(searchterms),
             #"mindate": "2006",
             #"retstart": "7407",
             "retmax": "10000",
             "sort": "pub+date"} #max 100 000

    r = requests.get('http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi', query)
    logging.debug("Request Status: {}".format(str(r.status_code)))
    response = r.text
    root = ET.fromstring(response.encode("utf-8"))
    pmids = []
    repeats = 0
    for pmid in root.find("IdList"):
        if pmids not in negative_pmids:
            pmids.append(pmid.text)
        else:
            print "repeated pmid: {}".format(pmid)
            repeats += 1
    print "repeated: {}".format(repeats)

    with codecs.open(corpus_text_path, 'a', 'utf-8') as docfile:
        for i, pmid in enumerate(pmids):
            doc = pubmed.PubmedDocument(pmid)
            docfile.write(pmid + "\t" + doc.text.replace("\n", " ") + "\n")
            print "{}/{}".format(i, len(pmids))
            sleep(0.4)

def process_documents(corpus_path):
    corpus = Corpus(corpus_path)
    final_text = []
    corenlp_client = StanfordCoreNLP('http://localhost:9000')
    lcount = 0
    starts = set()
    with codecs.open(corpus_path, 'r', 'utf-8') as docfile:
        for l in docfile:
            print lcount
            if l[:10] in starts:
                print "repeated abstract:", l[:10]
                continue
            lcount += 1
            starts.add(l[:10])
            values = l.strip().split("\t")
            pmid = values[0]
            abs_text = " ".join(values[1:])
            newdoc = Document(abs_text, did="PMID" + pmid)
            newdoc.process_document(corenlp_client)
            #for sentence in newdoc.sentences:
            #    print [t.text for t in sentence.tokens]
            newtext = ""
            newdoc.did = "PMID" + pmid
            corpus.documents["PMID" + pmid] = newdoc
            """for s in newdoc.sentences:
                for t in s.tokens:
                    newtext += t.text + " "
            final_text.append(newtext)"""
            # if lcount > 10:
            #     break
            if lcount % 1000 == 0:
                corpus.save("{}_{}.pickle".format(corpus_path, str(lcount/1000)))
                corpus = Corpus(corpus_path)
    corpus.save("{}_{}.pickle".format(corpus_path, str(lcount / 1000)))
    #with codecs.open("corpora/Thaliana/documents-processed.txt", 'w', 'utf-8') as finalfile:
    #    for l in final_text:
    #        finalfile.write(l + "\n")


def load_gold_relations(reltype):
    with codecs.open("seedev_relation.txt", 'r', "utf-8") as f:
        gold_relations = f.readlines()
    entities = {} # text -> types
    relations = {} # type#text -> type#text
    for r in gold_relations:
        values = r.strip().split("\t")
        if values[1] == reltype or reltype == "all":
            type1, entity1 = values[0].split("#")
            type2, entity2 = values[2].split("#")
            if entity1 not in entities:
                entities[entity1] = set()
            if entity2 not in entities:
                entities[entity2] = set()
            entities[entity1].add(type1)
            entities[entity1].add(type2)
            if values[0] not in relations:
                relations[values[0]] = set()
            relations[values[0]].add((values[2], values[1]))
    return entities, relations


def annotate_corpus_relations(corpus, model, corpuspath):

    logging.info("getting relations...")
    # entities, relations = load_gold_relations(reltype)
    logging.info("finding relations...")
    # print entities.keys()[:20]
    for did in corpus.documents:
        for sentence in corpus.documents[did].sentences:
            sentences_mirnas = []
            sentence_tfs = []
            #print sentence.entities.elist
            for entity in sentence.entities.elist[model]:
                if entity.type == "mirna":
                    sentences_mirnas.append(entity)
                elif entity.type == "protein":
                    sentence_tfs.append(entity)
            for mirna in sentences_mirnas:
                for tf in sentence_tfs:
                    ss = ssm.simui_go(mirna.best_go, tf.best_go)
                    if ss > 0:
                        print ss, mirna.text, tf.text, mirna.best_go, tf.best_go

    print "saving corpus..."
    corpus.save(corpuspath)
negative_pmids = open("negative_pmids.txt", 'r').readlines()

if len(sys.argv) > 2:
    corpus_path = sys.argv[2]
else:
    corpus_path = "corpora/mirna-ds/abstracts.txt"
if sys.argv[1] == "download":
    get_pubmed_abstracts(["mirna"], corpus_path, negative_pmids)
elif sys.argv[1] == "process":
    process_documents(corpus_path)
elif sys.argv[1] == "annotate":
    results = pickle.load(open("results/mirna_ds_entities.pickle", 'rb'))
    results.load_corpus("mirna_ds")
    corpus = results.corpus
    annotate_corpus_relations(corpus, "combined", "corpora/mirna-ds/abstracts.txt_1.pickle")