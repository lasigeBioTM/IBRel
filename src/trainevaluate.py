import argparse
import logging
import time
import cPickle as pickle

from classification.rext.crfre import CrfSuiteRE
from classification.rext.jsrekernel import JSREKernel
from classification.rext.multiinstance import MILClassifier
from classification.rext.multir import MultiR
from classification.rext.scikitre import ScikitRE
from classification.rext.stanfordre import StanfordRE
from classification.rext.svmtk import SVMTKernel
from config.corpus_paths import paths
from evaluate import get_gold_ann_set, get_list_results, get_relations_results
from text.corpus import Corpus


def main():
    start_time = time.time()
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("goldstd", nargs="+",
                        help="Gold standards to be used. First for training and second for evaluating")
    parser.add_argument("--tag", dest="tag", default="0", help="Tag to identify the experiment")
    parser.add_argument("--models", dest="models", help="model destination path, without extension", nargs="+")
    parser.add_argument("--entitytype", dest="etype", help="type of entities to be considered", default="all")
    parser.add_argument("--pairtype", dest="ptype", help="type of pairs to be considered", default="all")
    parser.add_argument("--crf", dest="crf", help="CRF implementation", default="stanford",
                        choices=["stanford", "crfsuite", "banner"])
    parser.add_argument("--log", action="store", dest="loglevel", default="WARNING", help="Log level")
    parser.add_argument("--rules", default=[], nargs='+', help="aditional post processing rules")
    parser.add_argument("--kernel", action="store", dest="kernel", default="svmtk", help="Kernel for relation extraction")
    parser.add_argument("--results", dest="results", help="Results object pickle.")
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
    # logging.info("Processing action {0} on {1}".format(options.actions, options.goldstd))

    # train_corpus = Corpus("corpus/" + "&".join(options.goldstd[0]))
    corpus_path = paths[options.goldstd[0]]["corpus"]
    logging.info("loading corpus %s" % corpus_path)
    train_corpus = pickle.load(open(corpus_path, 'rb'))
    with open("mirna_ds-pmids.txt", 'w') as pmidfile:
        for did in train_corpus.documents:
            pmidfile.write(did + "\n")


    # test_corpus = Corpus("corpus/" + "&".join(options.goldstd[1]))
    test_sets = []
    for g in options.goldstd[1:]:
        corpus_path = paths[g]["corpus"]
        logging.info("loading corpus %s" % corpus_path)
        test_corpus = pickle.load(open(corpus_path, 'rb'))
        test_sets.append(test_corpus)



    relations = set()
    with open("corpora/transmir/transmir_relations.txt") as rfile:
        for l in rfile:
            relations.add(tuple(l.strip().split('\t')))
    train_model = MILClassifier(train_corpus, options.ptype, relations, ner=options.models[0])
    train_model.train()

    for i, test_corpus in enumerate(test_sets):
        logging.info("evaluation {}".format(options.goldstd[i+1]))
        test_model = MILClassifier(test_corpus, options.ptype, relations, test=True, ner=options.models[i+1])
        # test_model.load_classifier()
        test_model.vectorizer = train_model.vectorizer
        test_model.classifier = train_model.classifier

        test_model.test()
        results = test_model.get_predictions(test_corpus)
        results.path = options.results + "-" + options.goldstd[i+1]
        results.save(options.results + "-" + options.goldstd[i+1] + ".pickle")
        results.load_corpus(options.goldstd[i+1])
        logging.info("loading gold standard %s" % paths[options.goldstd[1]]["annotations"])
        goldset = get_gold_ann_set(paths[options.goldstd[i+1]]["format"], paths[options.goldstd[i+1]]["annotations"],
                                   options.etype, options.ptype, paths[options.goldstd[i+1]]["text"])
        if options.goldstd[i+1] in ("transmir_annotated", "miRTex_test"):
            get_list_results(results, options.kernel, goldset[1], {}, options.rules, mode="re")
        else:
            get_relations_results(results, options.kernel, goldset[1], {}, options.rules)

    total_time = time.time() - start_time
    logging.info("Total time: %ss" % total_time)


if __name__ == "__main__":
    main()



