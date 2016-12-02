import argparse
import logging
import time
import cPickle as pickle
from collections import OrderedDict
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
    parser.add_argument("--emodels", dest="emodels", help="model destination path, without extension", nargs="+")
    parser.add_argument("--rmodels", dest="rmodels", help="model destination path, without extension")
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
        for sentence in train_corpus.get_sentences(options.emodels[0]):
            for e in sentence.entities.elist[options.emodels[0]]:
                if e.normalized_score > 0:
                    total_entities += 1
        # with open("mirna_ds-pmids.txt", 'w') as pmidfile:
        #     for did in train_corpus.documents:
        #         pmidfile.write(did + "\n")
        train_model = MILClassifier(train_corpus, options.ptype, relations, ner=options.emodels[0])
        train_model.load_kb("corpora/transmir/transmir_relations.txt")
        train_model.generateMILdata(test=False)
        train_model.write_to_file("temp/mil.train")
        train_model = None
        train_corpus = None
    print "total entities:", total_entities
    train_model = MILClassifier(None, options.ptype, relations, ner=options.emodels[0], generate=False,
                                modelname=options.rmodels)
    train_model.load_kb("corpora/transmir/transmir_relations.txt")
    train_model.load_from_file("temp/mil.train")
    #train_model.generateMILdata(test=False)
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
        test_model = MILClassifier(test_corpus, options.ptype, relations, test=True, ner=options.emodels[i+1],
                                   modelname=options.rmodels)
        test_model.load_kb("corpora/transmir/transmir_relations.txt")
        test_model.generateMILdata(test=False)
        test_model.load_classifier()
        #test_model.vectorizer = train_model.vectorizer
        #test_model.classifier = train_model.classifier

        test_model.test()
        results = test_model.get_predictions(test_corpus)
        results.path = options.results + "-" + options.test[i]
        results.save(options.results + "-" + options.test[i] + ".pickle")
        results.load_corpus(options.test[i])
        if options.test[i] != "mirna_cf_annotated":
            logging.info("loading gold standard %s" % paths[options.test[i]]["annotations"])
            goldset = get_gold_ann_set(paths[options.test[i]]["format"], paths[options.test[i]]["annotations"],
                                       options.etype, options.ptype, paths[options.test[i]]["text"])
            if options.test[i] in ("transmir_annotated", "miRTex_test"):
                get_list_results(results, options.kernel, goldset[1], {}, options.rules, mode="re")
            else:
                get_relations_results(results, options.kernel, goldset[1], {}, options.rules)
        else:
            total_entities = 0
            for sentence in test_corpus.get_sentences(options.emodels[1]):
                for e in sentence.entities.elist[options.emodels[1]]:
                    if e.normalized_score > 0:
                        total_entities += 1
            print "total entities:", total_entities
            #sysresults = results.corpus.get_unique_results(options.kernel, {}, options.rules, mode="re")
            sysresults = []
            for did in results.corpus.documents:
                for p in results.corpus.documents[did].pairs.pairs:
                    if options.kernel in p.recognized_by:
                        sentence = results.corpus.documents[did].get_sentence(p.entities[0].sid)
                        # print p.entities[0].text, p.entities[1].text
                        sysresults.append((p.entities[0].sid,
                                           p.entities[0].normalized,
                                           p.entities[1].normalized,
                                           "{}=>{}".format(p.entities[0].normalized,
                                                           p.entities[1].normalized),
                                           p.recognized_by[options.kernel],
                                           sentence.text))
            rels = {}
            for x in sysresults:
                pair = (x[1], x[2])
                if pair not in rels:
                    rels[pair] = []
                #print x[0], x[-1], x[3]
                stext = x[0] + ": " + x[-1] + " (" + x[3] + ")"
                # stext = ""
                add = True
                for i in rels[pair]:
                    if i[0].startswith(x[0]):
                        add = False
                        break
                if add:
                    rels[pair].append((stext, x[4]))
            # for t in rels.items():
            #     print t
            o = OrderedDict(sorted(rels.items(), key=lambda t: t[1][0][1], reverse=True))
            for x in o:
                print x, len(o[x])
                for s in o[x]:
                    print "\t", s[0].encode("utf-8")
                print
            for x in o:
                conf = round(o[x][0][1], 3)
                unique_dids = set([sid[0].split(".")[0] for sid in o[x]])
                # print unique_dids
                print x[0] + "\t" + x[1] + "\t" + str(len(o[x])) + "\t" + str(len(unique_dids)) + "\t" + str(conf)
            #max_width = table_instance.column_max_width(2)
            #for i, line in enumerate(table_instance.table_data):
            #    wrapped_string = '\n'.join(wrap(line[2], max_width))
            #    table_instance.table_data[i][2] = wrapped_string

    total_time = time.time() - start_time
    print "Total time: %ss" % total_time


if __name__ == "__main__":
    main()



