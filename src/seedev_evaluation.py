import argparse
import logging
import pickle

import time

import sys
from pycorenlp import StanfordCoreNLP

from classification.rext.jsrekernel import JSREKernel
from classification.rext.multir import MultiR
from classification.rext.rules import RuleClassifier
from classification.rext.scikitre import ScikitRE
from classification.rext.stanfordre import StanfordRE
from classification.rext.svmtk import SVMTKernel
from config import config
from reader.seedev_corpus import SeeDevCorpus
from text.corpus import Corpus


def main():
    start_time = time.time()
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("actions", default="classify",  help="Actions to be performed.",
                      choices=["load_corpus", "annotate", "classify", "write_results", "write_goldstandard",
                               "train", "test", "train_multiple", "test_multiple", "train_matcher", "test_matcher",
                               "crossvalidation", "train_relations", "test_relations"])
    parser.add_argument("--goldstd", default="", dest="goldstd", nargs="+",
                      help="Gold standard to be used. Will override corpus, annotations",
                      choices=config.paths.keys())
    parser.add_argument("--submodels", default="", nargs='+', help="sub types of classifiers"),
    parser.add_argument("--models", dest="models", help="model destination path, without extension")
    parser.add_argument("--pairtype", dest="ptype", help="type of pairs to be considered", default="all")
    parser.add_argument("--doctype", dest="doctype", help="type of document to be considered", default="all")
    parser.add_argument("-o", "--output", "--format", dest="output",
                        nargs=2, help="format path; output formats: xml, html, tsv, text, chemdner.")
    parser.add_argument("--log", action="store", dest="loglevel", default="WARNING", help="Log level")
    parser.add_argument("--kernel", action="store", dest="kernel", default="svmtk", help="Kernel for relation extraction")
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
    logging.getLogger("requests.packages").setLevel(30)
    logging.info("Processing action {0} on {1}".format(options.actions, options.goldstd))

    # set configuration variables based on the goldstd option if the corpus has a gold standard,
    # or on corpus and annotation options
    # pre-processing options
    if options.actions == "load_corpus":
        if len(options.goldstd) > 1:
            print "load only one corpus each time"
            sys.exit()
        options.goldstd = options.goldstd[0]
        corpus_format = config.paths[options.goldstd]["format"]
        corpus_path = config.paths[options.goldstd]["text"]
        corpus_ann = config.paths[options.goldstd]["annotations"]

        corenlp_client = StanfordCoreNLP('http://localhost:9000')
        # corpus = load_corpus(options.goldstd, corpus_path, corpus_format, corenlp_client)
        corpus = SeeDevCorpus(corpus_path)
        corpus.load_corpus(corenlp_client)
        corpus.save(config.paths[options.goldstd]["corpus"])
        if corpus_ann: #add annotation if it is not a test set
            corpus.load_annotations(corpus_ann, "all")
            corpus.save(config.paths[options.goldstd]["corpus"])

    elif options.actions == "annotate": # rext-add annotation to corpus
        if len(options.goldstd) > 1:
            print "load only one corpus each time"
            sys.exit()
        options.goldstd = options.goldstd[0]
        corpus_path = config.paths[options.goldstd]["corpus"]
        corpus_ann = config.paths[options.goldstd]["annotations"]
        logging.info("loading corpus %s" % corpus_path)
        corpus = pickle.load(open(corpus_path, 'rb'))
        logging.debug("loading annotations...")
        corpus.clear_annotations(options.etype)
        corpus.load_annotations(corpus_ann, options.etype, options.ptype)
        # corpus.get_invalid_sentences()
        corpus.save(config.paths[options.goldstd]["corpus"])
    else:
        corpus = Corpus("corpus/" + "&".join(options.goldstd))
        for g in options.goldstd:
            corpus_path = config.paths[g]["corpus"]
            logging.info("loading corpus %s" % corpus_path)
            this_corpus = pickle.load(open(corpus_path, 'rb'))
            corpus.documents.update(this_corpus.documents)

        if options.actions == "train_relations":
            if options.kernel == "jsre":
                model = JSREKernel(corpus, options.ptype)
            elif options.kernel == "svmtk":
                model = SVMTKernel(corpus, (options.etype1, options.etype2))
            elif options.kernel == "stanfordre":
                model = StanfordRE(corpus, (options.etype1, options.etype2))
            elif options.kernel == "multir":
                model = MultiR(corpus, (options.etype1, options.etype2))
            elif options.kernel == "scikit":
                model = ScikitRE(corpus, (options.etype1, options.etype2))
            model.train()
        # testing

        elif options.actions == "test_relations":
            if options.kernel == "jsre":
                model = JSREKernel(corpus, (options.etype1, options.etype2))
            elif options.kernel == "svmtk":
                model = SVMTKernel(corpus, (options.etype1, options.etype2))
            elif options.kernel == "rules":
                model = RuleClassifier(corpus, options.ptype)
            elif options.kernel == "stanfordre":
                model = StanfordRE(corpus, options.ptype)
            elif options.kernel == "scikit":
                model = ScikitRE(corpus, (options.etype1, options.etype2))
            model.load_classifier()
            model.test()
            results = model.get_predictions(corpus)
            results.save(options.output[1] + ".pickle")

    total_time = time.time() - start_time
    logging.info("Total time: %ss" % total_time)

if __name__ == "__main__":
    main()
