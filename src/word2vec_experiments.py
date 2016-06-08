import codecs
import os
import pickle
from time import sleep

import requests
import word2vec
import logging
import xml.etree.ElementTree as ET

from pycorenlp import StanfordCoreNLP

import config.corpus_paths
from classification.ner.matcher import MatcherModel
from config import config
from reader import pubmed
from text.corpus import Corpus
from text.document import Document
import logging
numeric_level = getattr(logging, "DEBUG", None)
logging_format = '%(asctime)s %(levelname)s %(filename)s:%(lineno)s:%(funcName)s %(message)s'
logging.basicConfig(level=numeric_level, format=logging_format)
logging.getLogger().setLevel(numeric_level)


def write_train_file(filepath="corpora/Thaliana/documents-processed.txt", corpuspath="corpora/Thaliana/thaliana-documents_11.pickle"):
    corpus = pickle.load(open(corpuspath, 'rb'))
    with codecs.open(filepath, 'w', 'utf-8') as f:
        for did in corpus.documents:
            for sentence in corpus.documents[did].sentences:
                # print sentence.sid, sentence.tokens
                f.write(" ".join([t.lemma.lower() for t in sentence.tokens if t.text.isalnum() and not t.text.isnumeric()]) + "\n")


def train_model(docfile_root="corpora/Thaliana/documents-processed"):
    print "phrases..."
    word2vec.word2phrase(docfile_root + ".txt", docfile_root + "-phrases.txt", verbose=True)
    #print "word2vec"
    #word2vec.word2vec(docfile_root + "-phrases.txt", docfile_root + ".bin", size=1000, verbose=True, min_count=1)
    print "word2cluster"
    word2vec.word2clusters(docfile_root + ".txt", docfile_root + '-clusters.txt', 10000, verbose=True, min_count=1, threads=4)
    #model = word2vec.load(docfile_root + '.bin')
    #indexes, metrics = model.cosine('AP2')
    #print model.vectors.shape
    #print model.generate_response(indexes, metrics).tolist()


def match_relations(reltype, docfile_root="corpora/Thaliana/documents-processed"):

    model = word2vec.load(docfile_root + '.bin')
    gold_relations = []
    with open("seedev_relation.txt") as f:
        gold_relations = f.readlines()
    unmatched1, unmatched2 = 0, 0
    for r in gold_relations:
        values = r.split("\t")
        if values[1] == reltype:
            entity1 = values[0].split("#")[1]
            entity2 = values[2].split("#")[1]
            #print entity1,
            if entity1 in model:
                indexes, metrics = model.cosine(entity1, n=1)
                #print model.generate_response(indexes, metrics).tolist()
            else:
                entity1 = entity1.split(" ")[0]
                if entity1 in model:
                    indexes, metrics = model.cosine(entity1, n=1)
                    #print model.generate_response(indexes, metrics).tolist()
                else:
                    unmatched1 += 1
                    #print
            #print entity2,
            if entity2 in model:
                indexes, metrics = model.cosine(entity2, n=5)
                #print model.generate_response(indexes, metrics).tolist()
            else:
                entity2 = entity2.split(" ")[0]
                if entity2 in model:
                    indexes, metrics = model.cosine(entity2, n=5)
                    #print model.generate_response(indexes, metrics).tolist()
                else:
                    unmatched2 += 1
                    #print
            #print "========================================"
    print unmatched1, unmatched2


def get_seedev_docs(f="corpora/Thaliana/documents-processed.txt"):
    goldstd = "seedev_train"
    corpus_path = config.corpus_paths.paths[goldstd]["corpus"]
    print "loading corpus %s" % corpus_path
    corpus = pickle.load(open(corpus_path, 'rb'))
    final_text = []
    for did in corpus.documents:
        for sentence in corpus.documents[did].sentences:
            newtext = ""
            for t in sentence.tokens:
                if t.text.isalnum() and not t.text.isnumeric():
                    newtext += t.lemma.lower() + " "
            final_text.append(newtext)

    with codecs.open(f, 'a' 'utf-8') as f:
        for l in final_text:
            f.write(l.encode("utf-8") + "\n")


def load_tair_relations():
    #Transcribes_Or_Translates_To
    relations = {}
    with open("corpora/Thaliana/gene_aliases_20141231.txt", 'r') as f:
        for l in f:
            values = l.strip().split("\t")
            if values[0] not in relations:
                relations[values[0]] = []
            relations[values[0]].append((values[1], "Transcribes_Or_Translates_To"))
            relations[values[0]].append((values[2][1:-1], "Transcribes_Or_Translates_To"))
    with open("corpora/Thaliana/gene_families_sep_29_09_update.txt", 'r') as f:
        for l in f:
            values = l.split("\t")
            family_name = values[0]
            if family_name not in relations:
                relations[family_name] = []
            if values[2] != "NULL": #Gene_name
                relations[family_name].append((values[2], "Is_Member_Of_Family"))
            if values[3] != "NULL": #Alternate_gene_Name
                relations[family_name].append((values[3], "Is_Member_Of_Family"))
            if values[5] != "NULL": #AT3g51860
                relations[family_name].append((values[5], "Is_Member_Of_Family"))

    with open("corpora/Thaliana/ATH_GO_GOSLIM.txt", 'r') as f:
        for l in f:
            values = l.split("\t")
            gene = values[0]
            target = values[4]
            if gene not in relations:
                relations[gene] = []
                if values[3] == "located in":
                    relations[gene].append((target, "Is_Localized_In"))
                elif values[3] == "involved in":
                    relations[gene].append((target, "Is_Involved_In_Process"))
                elif values[3] == "functions in":
                    #relations[gene].append((target, "Is_Involved_In_Process"))
                    continue
    return relations


    # eid = sentence.tag_entity(start, end, entity_type, text=etext, original_id=tid, exclude=exclude)

#get_pubmed_abstracts()
#process_documents()
#get_seedev_docs()
#train_model(docfile_root="corpora/Thaliana/seedev-processed")
#match_relations("Regulates_Process", docfile_root="corpora/Thaliana/seedev-processed")
#write_train_file()
#get_seedev_docs()
#train_model()


#annotate_corpus_entities("all")
#annotate_corpus_relations("all")
#match_relations("Regulates_Process")
#print load_tair_relations()