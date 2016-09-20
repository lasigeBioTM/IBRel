import argparse
import logging
import time
import cPickle as pickle
from classification.rext.multiinstance import MILClassifier
from config.corpus_paths import paths
from evaluate import get_gold_ann_set, get_list_results, get_relations_results
from text.corpus import Corpus

def main():
    start_time = time.time()
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("--train", nargs="+",
                        help="Gold standards to be used for training")
    parser.add_argument("--test", nargs="+",
                        help="Gold standards to be used for testing")
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

    relations = set()
    with open("corpora/transmir/transmir_relations.txt") as rfile:
        for l in rfile:
            relations.add(tuple(l.strip().split('\t')))
    with open("temp/mil.train", 'w') as f:
        f.write("")
    # train_corpus = Corpus("corpus/" + "&".join(options.goldstd[0]))
    total_entities = 0
    for goldstd in options.train:
        corpus_path = paths[goldstd]["corpus"]
        logging.info("loading corpus %s" % corpus_path)
        train_corpus = pickle.load(open(corpus_path, 'rb'))
        for sentence in train_corpus.get_sentences(options.models[0]):
            for e in sentence.entities.elist[options.models[0]]:
                if e.normalized_score > 0:
                    total_entities += 1
        # with open("mirna_ds-pmids.txt", 'w') as pmidfile:
        #     for did in train_corpus.documents:
        #         pmidfile.write(did + "\n")
        train_model = MILClassifier(train_corpus, options.ptype, relations, ner=options.models[0])
        train_model.write_to_file("temp/mil.train")
        train_model = None
        train_corpus = None
    print "total entities:", total_entities
    train_model = MILClassifier(None, options.ptype, relations, ner=options.models[0], generate=False)
    train_model.load_from_file("temp/mil.train")
    train_model.train()


    # test_corpus = Corpus("corpus/" + "&".join(options.goldstd[1]))
    test_sets = []
    for g in options.test:
        corpus_path = paths[g]["corpus"]
        logging.info("loading corpus %s" % corpus_path)
        test_corpus = pickle.load(open(corpus_path, 'rb'))
        test_sets.append(test_corpus)


    for i, test_corpus in enumerate(test_sets):
        logging.info("evaluation {}".format(options.test[i]))
        test_model = MILClassifier(test_corpus, options.ptype, relations, test=True, ner=options.models[i+1])
        # test_model.load_classifier()
        test_model.vectorizer = train_model.vectorizer
        test_model.classifier = train_model.classifier

        test_model.test()
        results = test_model.get_predictions(test_corpus)
        results.path = options.results + "-" + options.test[i]
        results.save(options.results + "-" + options.test[i] + ".pickle")
        results.load_corpus(options.test[i])
        logging.info("loading gold standard %s" % paths[options.test[i]]["annotations"])
        goldset = get_gold_ann_set(paths[options.test[i]]["format"], paths[options.test[i]]["annotations"],
                                   options.etype, options.ptype, paths[options.test[i]]["text"])
        if options.test[i] in ("transmir_annotated", "miRTex_test"):
            get_list_results(results, options.kernel, goldset[1], {}, options.rules, mode="re")
        else:
            get_relations_results(results, options.kernel, goldset[1], {}, options.rules)

    total_time = time.time() - start_time
    print "Total time: %ss" % total_time


if __name__ == "__main__":
    main()



