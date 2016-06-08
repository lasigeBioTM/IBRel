import requests
import logging
import xml.etree.ElementTree as ET
import codecs
import os
import pickle
from time import sleep
from pycorenlp import StanfordCoreNLP

import config.corpus_paths
from classification.ner.matcher import MatcherModel
from config import config
from reader import pubmed
from text.corpus import Corpus
from text.document import Document


def get_pubmed_abstracts(terms, corpus_text_path, negative_pmids):
    mesh = "+".join([t + "[mesh]" for t in terms])
    query = {"term": "{}+hasabstract[text]".format(mesh),
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
            docfile.write(doc.text.replace("\n", " ") + "\n")
            print "{}/{}".format(i, len(pmids))
            sleep(0.5)

def process_documents(corpus_path):
    corpus = Corpus(corpus_path)
    final_text = []
    corenlp_client = StanfordCoreNLP('http://localhost:9000')
    lcount = 0
    starts = set()
    with codecs.open(corpus_path, 'r', 'utf-8') as docfile:
        for l in docfile:
            print lcount
            if l[:20] in starts:
                continue
            lcount += 1
            starts.add(l[:20])

            newdoc = Document(l.strip())
            newdoc.process_document(corenlp_client)
            #for sentence in newdoc.sentences:
            #    print [t.text for t in sentence.tokens]
            newtext = ""
            corpus.documents["d" + str(lcount)] = newdoc
            """for s in newdoc.sentences:
                for t in s.tokens:
                    newtext += t.text + " "
            final_text.append(newtext)"""
            # if lcount > 10:
            #     break
            if lcount % 1000 == 0:
                corpus.save("{}_{}.pickle".format(corpus_path, str(lcount/1000)))
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


def annotate_corpus_entities(reltype, corpuspath="corpora/Thaliana/thaliana-documents_10.pickle"):
    corpus = pickle.load(open(corpuspath, 'rb'))
    for d in corpus.documents:
        for sentence in corpus.documents[d].sentences:
            sentence.sid = d + "." + sentence.sid.split(".")[-1]
    entities, relations = load_gold_relations(reltype)
    matcher = MatcherModel("goldstandard")
    matcher.names = set(entities.keys())
    corpus, entitiesfound = matcher.test(corpus)

    print "saving corpus..."
    corpus.save(corpuspath)


def annotate_corpus_relations(reltype, corpuspath="corpora/Thaliana/thaliana-documents_10.pickle"):
    corpus = pickle.load(open(corpuspath, 'rb'))
    logging.info("getting relations...")
    entities, relations = load_gold_relations(reltype)
    logging.info("finding relations...")
    # print entities.keys()[:20]
    for did in corpus.documents:
        for sentence in corpus.documents[did].sentences:
            for entity in sentence.entities.elist["goldstandard"]:
                if entity.text in entities:
                    for etype in entities[entity.text]:
                        source = etype + "#" + entity.text
                        if source in relations:
                            for target in relations[source]:
                                target_type, target_text = target[0].split("#")
                                for entity2 in sentence.entities.elist["goldstandard"]:
                                    #print entity2.text,"||", target_text, target_type
                                    if entity2.text == target_text: # and entity2.type == target_type:
                                        entity.targets.append((entity2.eid, target[1]))
                                        print "found relation:", entity.text, entity2.text
    print "saving corpus..."
    corpus.save(corpuspath)

#negative_pmids = open("negative_pmids.txt", 'r').readlines()
#get_pubmed_abstracts(["mirna"], "corpora/mirna-ds/abstracts.txt", negative_pmids)
#process_documents("corpora/mirna-ds/abstracts.txt")