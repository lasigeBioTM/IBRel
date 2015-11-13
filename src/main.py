#!/usr/bin/env python
from __future__ import division, unicode_literals
import random
import itertools
import os, sys
import shutil
from subprocess import Popen, PIPE
import xml.etree.ElementTree as ET
import logging
import cPickle as pickle
import argparse
import datetime
import time
import codecs
from corenlp import StanfordCoreNLP
from classification.ner.mirna_matcher import MirnaMatcher

from reader.chemdner_corpus import ChemdnerCorpus
from reader.genia_corpus import GeniaCorpus
from reader.gpro_corpus import GproCorpus
from reader.ddi_corpus import DDICorpus
from reader.chebi_corpus import ChebiCorpus
from reader.pubmed_corpus import PubmedCorpus
from text.corpus import Corpus
from classification.ner.taggercollection import TaggerCollection
from classification.ner.matcher import MatcherModel
from classification.ner.simpletagger import SimpleTaggerModel, BiasModel, feature_extractors
from classification.ner.stanfordner import StanfordNERModel
from classification.results import ResultsNER, ResultSetNER
from config import config
if config.use_chebi:
    from postprocessing.chebi_resolution import add_chebi_mappings
    from postprocessing.ssm import add_ssm_score
from evaluate import get_results, run_chemdner_evaluation, get_gold_ann_set


def run_crossvalidation_types(goldstd, corpus, model, cv):
    doclist = corpus.documents.keys()
    random.shuffle(doclist)
    size = int(len(doclist)/cv)
    sublists = chunks(doclist, size)
    p, r = [], []
    for nlist in range(cv):
        testids = sublists[nlist]
        trainids = list(itertools.chain.from_iterable(sublists[:nlist]))
        trainids += list(itertools.chain.from_iterable(sublists[nlist+1:]))
        print 'CV{} - test set: {}; train set: {}'.format(nlist, len(testids), len(trainids))
        train_corpus = Corpus(corpus.path, documents={did: corpus.documents[did] for did in trainids})
        test_corpus = Corpus(corpus.path, documents={did: corpus.documents[did] for did in testids})
        corpus.subtypes = []  # TEMPORARY!!!!
        train_corpus.subtypes = corpus.subtypes
        test_corpus.subtypes = corpus.subtypes
        basemodel = model + "_cv{}".format(nlist)
        '''logging.debug('CV{} - test set: {}; train set: {}'.format(nlist, len(test_corpus.documents), len(train_corpus.documents)))
        for d in train_corpus.documents:
            for s in train_corpus.documents[d].sentences:
                print len([t.tags.get("goldstandard") for t in s.tokens if t.tags.get("goldstandard") != "other"])
        sys.exit()'''
        # train
        logging.info('CV{} - TRAIN'.format(nlist))
        models = TaggerCollection(basepath=basemodel, corpus=train_corpus, subtypes=corpus.subtypes)
        models.train_types()

        # test
        logging.info('CV{} - TEST'.format(nlist))
        models.load_models()
        results = models.test_types(corpus)
        results.basepath = basemodel + "_results"
        final_results = results.combine_results()

        # validate
        if config.use_chebi:
            logging.info('CV{} - VALIDATE'.format(nlist))
            final_results = add_chebi_mappings(final_results, basemodel)
            final_results = add_ssm_score(final_results, basemodel)
            final_results.combine_results(basemodel, basemodel + "_combined")

        # evaluate
        logging.info('CV{} - EVALUATE'.format(nlist))
        goldset = get_gold_ann_set(config.paths[goldstd]["annotations"])
        get_results(final_results, basemodel + "_combined", goldset, {})
        evaluation = run_chemdner_evaluation(config.paths[goldstd]["cem"], basemodel + "_results.txt", "-t")
        values = evaluation.split("\n")[1].split('\t')
        p.append(float(values[13])) # index of micro precision
        r.append(float(values[14])) # index of micro recall
        logging.info("precision: {} recall:{}".format(str(values[13]), str(values[14])))
    pavg = sum(p)/cv
    ravg = sum(r)/cv
    print "precision: average={} all={}".format(pavg, '|'.join(p))
    print "recall: average={}  all={}".format(ravg, '|'.join(r))

def run_crossvalidation(goldstd, corpus, model, cv):
    doclist = corpus.documents.keys()
    random.shuffle(doclist)
    size = int(len(doclist)/cv)
    sublists = chunks(doclist, size)
    p, r = [], []
    for nlist in range(cv):
        testids = sublists[nlist]
        trainids = list(itertools.chain.from_iterable(sublists[:nlist]))
        trainids += list(itertools.chain.from_iterable(sublists[nlist+1:]))
        print 'CV{} - test set: {}; train set: {}'.format(nlist, len(testids), len(trainids))
        logging.debug(str(trainids))
        logging.debug(str(testids))
        train_corpus = Corpus(corpus.path, documents={did: corpus.documents[did] for did in trainids})
        test_corpus = Corpus(corpus.path, documents={did: corpus.documents[did] for did in testids})
        basemodel = model + "_cv{}".format(nlist)
        logging.debug('CV{} - test set: {}; train set: {}'.format(nlist, len(test_corpus.documents), len(train_corpus.documents)))
        '''for d in train_corpus.documents:
            for s in train_corpus.documents[d].sentences:
                print len([t.tags.get("goldstandard") for t in s.tokens if t.tags.get("goldstandard") != "other"])
        sys.exit()'''
        # train
        logging.info('CV{} - TRAIN'.format(nlist))
        train_model = StanfordNERModel(basemodel)
        train_model.load_data(train_corpus, feature_extractors.keys())
        train_model.train()

        # test
        logging.info('CV{} - TEST'.format(nlist))
        test_model = StanfordNERModel(basemodel)
        test_model.load_tagger()
        test_model.load_data(test_corpus, feature_extractors.keys(), mode="test")
        final_results = test_model.test(test_corpus)
        final_results.basepath = basemodel + "_results"
        final_results.path = basemodel

        # validate
        if config.use_chebi:
            logging.info('CV{} - VALIDATE'.format(nlist))
            final_results = add_chebi_mappings(final_results, basemodel)
            final_results = add_ssm_score(final_results, basemodel)
            final_results.combine_results(basemodel, basemodel)

        # evaluate
        logging.info('CV{} - EVALUATE'.format(nlist))
        test_goldset = set()
        goldset = get_gold_ann_set(config.paths[goldstd]["format"], config.paths[goldstd]["annotations"])
        for g in goldset:
            if g[0] in testids:
                test_goldset.add(g)
        precision, recall = get_results(final_results, basemodel, test_goldset, {}, [])
        # evaluation = run_chemdner_evaluation(config.paths[goldstd]["cem"], basemodel + "_results.txt", "-t")
        # values = evaluation.split("\n")[1].split('\t')
        p.append(precision)
        r.append(recall)
        # logging.info("precision: {} recall:{}".format(str(values[13]), str(values[14])))
    pavg = sum(p)/cv
    ravg = sum(r)/cv
    print "precision: average={} all={}".format(str(pavg), '|'.join([str(pp) for pp in p]))
    print "recall: average={}  all={}".format(str(ravg), '|'.join([str(rr) for rr in r]))

def chunks(l, n):
    """ return list of n sized sublists of l
    """
    subs = []
    for i in xrange(0, len(l), n):
        subs.append(l[i:i+n])
    return subs


def main():
    start_time = time.time()
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("actions", default="classify",  help="Actions to be performed.",
                      choices=["load_corpus", "annotate", "classify", "write_results", "write_goldstandard",
                               "train", "test", "train_multiple", "test_multiple", "train_matcher", "test_matcher",
                               "crossvalidation"])
    parser.add_argument("--goldstd", default="", dest="goldstd",
                      help="Gold standard to be used. Will override corpus, annotations",
                      choices=config.paths.keys())
    parser.add_argument("--submodels", default="", nargs='+', help="sub types of classifiers"),
    parser.add_argument("-i", "--input", dest="input", action="store",
                      default='''Administration of a higher dose of indinavir should be \\
considered when coadministering with megestrol acetate.''',
                      help="Text to classify.")
    parser.add_argument("--corpus", dest="corpus", nargs=2,
                      default=["chemdner", "CHEMDNER/CHEMDNER_SAMPLE_JUNE25/chemdner_sample_abstracts.txt"],
                      help="format path")
    parser.add_argument("--annotations", dest="annotations")
    parser.add_argument("--tag", dest="tag", default="0", help="Tag to identify the text.")
    parser.add_argument("--models", dest="models", help="model destination path, without extension")
    parser.add_argument("--annotated", action="store_true", default=False, dest="annotated",
                      help="True if the input has <entity> tags.")
    parser.add_argument("-o", "--output", "--format", dest="output",
                        nargs=2, help="format path; output formats: xml, html, tsv, text, chemdner.")
    parser.add_argument("--log", action="store", dest="loglevel", default="WARNING", help="Log level")
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
    logging.info("Processing action {0} on {1}".format(options.actions, options.goldstd))

    # set configuration variables based on the goldstd option if the corpus has a gold standard,
    # or on corpus and annotation options
    if options.goldstd:
        if "load_corpus" in options.actions or "process_text" in options.actions:
            corpus_format = config.paths[options.goldstd]["format"]
            corpus_path = config.paths[options.goldstd]["text"]
        else:
            corpus_format = "pickle"
            corpus_path = config.paths[options.goldstd]["corpus"]
        corpus_ann = config.paths[options.goldstd]["annotations"]
    else:
        corpus_format, corpus_path = options.corpus
        corpus_ann = options.annotations

    # pre-processing options
    if options.actions == "load_corpus":
        print("loading CoreNLP...")
        corenlpserver = StanfordCoreNLP(corenlp_path=config.corenlp_dir,
                                    properties=config.corenlp_dir + "default.properties")
        if corpus_format == "chemdner":
            corpus = ChemdnerCorpus(corpus_path)
            #corpus.save()
            if options.goldstd == "chemdner_traindev":
                # merge chemdner_train and chemdner_dev
                tpath = config.paths["chemdner_train"]["corpus"]
                tcorpus = pickle.load(open(tpath, 'rb'))
                dpath = config.paths["chemdner_dev"]["corpus"]
                dcorpus = pickle.load(open(dpath, 'rb'))
                corpus.documents.update(tcorpus.documents)
                corpus.documents.update(dcorpus.documents)
            elif options.goldstd == "cemp_test_divide":
                logging.info("loading corpus %s" % corpus_path)
                corpus.load_corpus(corenlpserver, process=False)
                docs = corpus.documents.keys()
                step = int(len(docs)/10)
                logging.info("step: {}".format(str(step)))
                for i in range(10):
                    logging.info("processing cemp_test{}: {} - {}".format(str(i), int(step*i), int(step*i+step)))
                    sub_corpus_path = config.paths["cemp_test" + str(i)]["corpus"]
                    sub_corpus = ChemdnerCorpus(sub_corpus_path)
                    sub_docs = docs[int(step*i):int(step*i+step)]
                    for di, d in enumerate(sub_docs):
                        logging.info("fold {}: processing {}/{}".format(i, di, step))
                        sub_corpus.documents[d] = corpus.documents[d]
                        del corpus.documents[d]
                        sub_corpus.documents[d].process_document(corenlpserver)
                    sub_corpus.save()

            else:
                corpus.load_corpus(corenlpserver)
        elif corpus_format == "gpro":
            corpus = GproCorpus(corpus_path)
            corpus.load_corpus(None)
        elif corpus_format == "ddi":
            corpus = DDICorpus(corpus_path)
            corpus.load_corpus(corenlpserver)
            # since the path of this corpus is a directory, add the reference to save this corpus
            corpus.path += options.goldstd + ".txt"
        elif corpus_format == "chebi":
            corpus = ChebiCorpus(corpus_path)
            corpus.load_corpus(corenlpserver)
            # since the path of this corpus is a directory, add the reference to save this corpus
            corpus.path += options.goldstd + ".txt"
        elif corpus_format == "pubmed":
            # corenlpserver = ""
            with open(corpus_path, 'r') as f:
                pmids = [line.strip() for line in f if line.strip()]
            corpus = PubmedCorpus(corpus_path, pmids)
            corpus.load_corpus(corenlpserver)
        elif corpus_format == "genia":
            corpus = GeniaCorpus(corpus_path)
            corpus.load_corpus(corenlpserver)
        corpus.save()
        if corpus_ann and "test" not in options.goldstd: #add annotation if it is not a test set
            corpus.load_annotations(corpus_ann)
            corpus.save()
    else: # options other than processing a corpus, i.e. load the corpus directly from a pickle file
        logging.info("loading corpus %s" % corpus_path)
        corpus = pickle.load(open(corpus_path, 'rb'))

    if options.actions == "annotate": # re-add annotation to corpus
        logging.debug("loading annotations...")
        corpus.load_annotations(corpus_ann)
        # for d in corpus.documents:
        #    for s in corpus.documents[d].sentences:
        #        print s.entities.elist
        corpus.save()
    elif options.actions == "write_goldstandard":
        model = BiasModel(options.output[1])
        model.load_data(corpus, [])
        model.test()
        results = ResultsNER(options.output[1])
        results.get_ner_results(corpus, model)
        results.save(options.output[1] + ".pickle")
        #logging.info("saved gold standard results to " + options.output[1] + ".txt")

    # training
    elif options.actions == "train":
        model = StanfordNERModel(options.models)
        model.load_data(corpus, feature_extractors.keys())
        model.train()
    elif options.actions == "train_matcher": # Train a simple classifier based on string matching
        model = MatcherModel(options.models)
        model.train(corpus)
    elif options.actions == "train_multiple": # Train one classifier for each type of entity in this corpus
        # logging.info(corpus.subtypes)
        models = TaggerCollection(basepath=options.models, corpus=corpus, subtypes=corpus.subtypes)
        models.train_types()

    # testing
    elif options.actions == "test":
        base_port = 9191
        if len(options.submodels) > 1:
            allresults = ResultSetNER(corpus, options.output[1])
            for i, submodel in enumerate(options.submodels):
                model = StanfordNERModel(options.models + "_" + submodel)
                model.load_tagger(base_port + i)
                # load data into the model format
                model.load_data(corpus, feature_extractors.keys(), mode="test")
                # run the classifier on the data
                results = model.test(corpus, port=base_port + i)
                allresults.add_results(results)
                model.kill_process()
            # save the results to an object that can be read again, and log files to debug
            final_results = allresults.combine_results()
        else:
            model = StanfordNERModel(options.models)
            model.load_tagger()
            model.load_data(corpus, feature_extractors.keys(), mode="test")
            final_results = model.test(corpus)
        with codecs.open(options.output[1] + ".txt", 'w', 'utf-8') as outfile:
            lines = final_results.corpus.write_chemdner_results(options.models, outfile)
        final_results.lines = lines
        final_results.save(options.output[1] + ".pickle")
    elif options.actions == "test_matcher":
        if "mirna" in options.models:
            model = MirnaMatcher(options.models)
        else:
            model = MatcherModel(options.models)
        results = ResultsNER(options.models)
        results.corpus, results.entities = model.test(corpus)
        allentities = set()
        for e in results.entities:
            allentities.add(results.entities[e].text)
        with codecs.open(options.output[1] + ".txt", 'w', 'utf-8') as outfile:
            outfile.write('\n'.join(allentities))

        results.save(options.output[1] + ".pickle")
    elif options.actions == "test_multiple":
        logging.info("testing with multiple classifiers... {}".format(' '.join(options.submodels)))
        allresults = ResultSetNER(corpus, options.output[1])
        if len(options.submodels) < 2:
            models = TaggerCollection(basepath=options.models)
            models.load_models()
            results = models.test_types(corpus)
            final_results = results.combine_results()
        else:
            base_port = 9191
            for submodel in options.submodels:
                models = TaggerCollection(basepath=options.models + "_" + submodel, baseport = base_port)
                models.load_models()
                results = models.test_types(corpus)
                logging.info("combining results...")
                submodel_results = results.combine_results()
                allresults.add_results(submodel_results)
                base_port += len(models.models)
            final_results = allresults.combine_results()
        logging.info("saving results...")
        final_results.save(options.output[1] + ".pickle")

    elif options.actions == "crossvalidation":
        cv = 5 # fixed 10-fold CV
        run_crossvalidation(options.goldstd, corpus, options.models, cv)

    total_time = time.time() - start_time
    logging.info("Total time: %ss" % total_time)

if __name__ == "__main__":
    main()
