import itertools
import logging
import random
import time
import argparse
import pickle
from classification.ner.crfsuitener import CrfSuiteModel
from classification.ner.simpletagger import feature_extractors
from classification.ner.stanfordner import StanfordNERModel
from config import config
from evaluate import get_gold_ann_set, get_results
from postprocessing.chebi_resolution import add_chebi_mappings
from postprocessing.ssm import add_ssm_score
from text.corpus import Corpus


def run_crossvalidation(goldstd, corpus, model, cv, crf, entity_type="all"):
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
        test_entities = len(test_corpus.get_all_entities("goldstandard"))
        train_entities = len(train_corpus.get_all_entities("goldstandard"))
        logging.info("test set entities: {}; train set entities: {}".format(test_entities, train_entities))
        basemodel = model + "_cv{}".format(nlist)
        logging.debug('CV{} - test set: {}; train set: {}'.format(nlist, len(test_corpus.documents), len(train_corpus.documents)))
        '''for d in train_corpus.documents:
            for s in train_corpus.documents[d].sentences:
                print len([t.tags.get("goldstandard") for t in s.tokens if t.tags.get("goldstandard") != "other"])
        sys.exit()'''
        # train
        logging.info('CV{} - TRAIN'.format(nlist))
        # train_model = StanfordNERModel(basemodel)
        if crf == "stanford":
            train_model = StanfordNERModel(basemodel)
        elif crf == "crfsuite":
            train_model = CrfSuiteModel(basemodel)
        train_model.load_data(train_corpus, feature_extractors.keys())
        train_model.train()

        # test
        logging.info('CV{} - TEST'.format(nlist))
        # test_model = StanfordNERModel(basemodel)
        if crf == "stanford":
            test_model = StanfordNERModel(basemodel)
        elif crf == "crfsuite":
            test_model = CrfSuiteModel(basemodel)
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
    precision, recall = get_results(final_results, model, test_goldset, {}, [])
    print precision, recall


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
    parser.add_argument("--goldstd", default="", dest="goldstd", nargs="+",
                      help="Gold standard to be used. Will override corpus, annotations",
                      choices=config.paths.keys())
    parser.add_argument("--submodels", default="", nargs='+', help="sub types of classifiers"),
    parser.add_argument("--corpus", dest="corpus", nargs=2,
                      default=["chemdner", "CHEMDNER/CHEMDNER_SAMPLE_JUNE25/chemdner_sample_abstracts.txt"],
                      help="format path")
    parser.add_argument("--annotations", dest="annotations")
    parser.add_argument("--tag", dest="tag", default="0", help="Tag to identify the text.")
    parser.add_argument("--models", dest="models", help="model destination path, without extension")
    parser.add_argument("--entitytype", dest="etype", help="type of entities to be considered", default="all")
    parser.add_argument("--doctype", dest="doctype", help="type of document to be considered", default="all")
    parser.add_argument("-o", "--output", "--format", dest="output",
                        nargs=2, help="format path; output formats: xml, html, tsv, text, chemdner.")
    parser.add_argument("--crf", dest="crf", help="CRF implementation", default="stanford",
                        choices=["stanford", "crfsuite"])
    parser.add_argument("--log", action="store", dest="loglevel", default="WARNING", help="Log level")
    parser.add_argument("--kernel", action="store", dest="kernel", default="svmtk", help="Kernel for relation extraction")
    parser.add_argument("--pairtype1", action="store", dest="pairtype1")
    parser.add_argument("--pairtype2", action="store", dest="pairtype2")
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
    # pre-processing options
    if options.actions == "load_corpus":
        if len(options.goldstd) > 1:
            print "load only one corpus each time"
            sys.exit()
        options.goldstd = options.goldstd[0]
        corpus_format = config.paths[options.goldstd]["format"]
        corpus_path = config.paths[options.goldstd]["text"]
        corpus_ann = config.paths[options.goldstd]["annotations"]

        corpus = Corpus("corpus/" + "&".join(options.goldstd))
        for g in options.goldstd:
            corpus_path = config.paths[g]["corpus"]
            logging.info("loading corpus %s" % corpus_path)
            this_corpus = pickle.load(open(corpus_path, 'rb'))
            corpus.documents.update(this_corpus.documents)
        cv = 5 # fixed 5-fold CV
        run_crossvalidation(options.goldstd, corpus, options.models, cv, options.etype)

    total_time = time.time() - start_time
    logging.info("Total time: %ss" % total_time)

if __name__ == "__main__":
    main()