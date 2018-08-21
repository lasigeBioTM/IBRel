import argparse
import logging
import os
import time
import cPickle as pickle
from config.corpus_paths import paths


def main():
    start_time = time.time()
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("--corpus", nargs="+",
                        help="Corpus to be converted")
    parser.add_argument("--models", dest="models", help="model destination path, without extension", nargs="+")
    parser.add_argument("--entitytype", dest="etype", help="type of entities to be considered", default="all")
    parser.add_argument("--pairtype", dest="ptype", help="type of pairs to be considered", default="all")
    parser.add_argument("--log", action="store", dest="loglevel", default="WARNING", help="Log level")
    parser.add_argument("--results", dest="results", help="Results object pickle.")
    parser.add_argument("--format", dest="format", help="Output format.", default=None)
    parser.add_argument("--path", dest="path", help="Output path.")
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


    for goldstd in options.corpus:
        corpus_path = paths[goldstd]["corpus"]
        logging.info("loading corpus %s" % corpus_path)
        corpus = pickle.load(open(corpus_path, 'rb'))
        corpus.convert_to(options.format, options.path)

    if options.results:
        logging.info("loading results %s" % options.results + ".pickle")
        if os.path.exists(options.results + ".pickle"):
            results = pickle.load(open(options.results + ".pickle", 'rb'))
            results.load_corpus(options.corpus[0])
            results.path = options.results
            results.convert_to(options.format, options.path, options.etype)
        else:
            print "results not found"
            print options.results

    total_time = time.time() - start_time
    print "Total time: %ss" % total_time


if __name__ == "__main__":
    main()