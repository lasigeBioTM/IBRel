#!/usr/bin/env python
from __future__ import division
import argparse
import cPickle as pickle
import codecs
import collections
import logging
import os
import random
import sys
import time

from sklearn import svm, tree
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import MultinomialNB, GaussianNB
from sklearn.pipeline import Pipeline

from config.corpus_paths import paths
from config import config
from reader.Transmir_corpus import get_transmir_gold_ann_set
from reader.bc2gm_corpus import get_b2gm_gold_ann_set
from reader.chemdner_corpus import get_chemdner_gold_ann_set, run_chemdner_evaluation, write_chemdner_files
from reader.genia_corpus import get_genia_gold_ann_set
from reader.jnlpba_corpus import get_jnlpba_gold_ann_set
from reader.mirna_corpus import get_ddi_mirna_gold_ann_set
from reader.mirtext_corpus import get_mirtex_gold_ann_set
from reader.seedev_corpus import get_seedev_gold_ann_set
from reader.tempEval_corpus import get_thymedata_gold_ann_set

if config.use_chebi:
    from postprocessing import chebi_resolution
    from postprocessing.ssm import get_ssm
from postprocessing.ensemble_ner import EnsembleNER
from classification.results import ResultsNER

def get_gold_ann_set(corpus_type, gold_path, entity_type, pair_type, text_path):
    if corpus_type == "chemdner":
        goldset = get_chemdner_gold_ann_set(gold_path, entity_type, text_path, corpus_type)
    elif corpus_type == "tempeval":
        goldset = get_thymedata_gold_ann_set(gold_path, entity_type, text_path, corpus_type)
    elif corpus_type == "pubmed":
        goldset = get_unique_gold_ann_set(gold_path)
    elif corpus_type == "genia":
        goldset = get_genia_gold_ann_set(gold_path, entity_type)
    elif corpus_type == "ddi-mirna":
        goldset = get_ddi_mirna_gold_ann_set(gold_path, entity_type, pair_type)
    elif corpus_type == "mirtex":
        goldset = get_mirtex_gold_ann_set(gold_path, entity_type, pair_type)
    elif corpus_type == "seedev":
        goldset = get_seedev_gold_ann_set(gold_path, entity_type, pair_type)
    elif corpus_type == "jnlpba":
        goldset = get_jnlpba_gold_ann_set(gold_path, entity_type)
    elif corpus_type == "bc2":
        goldset = get_b2gm_gold_ann_set(gold_path, text_path)
    elif corpus_type == "transmir":
        goldset = get_transmir_gold_ann_set(gold_path, entity_type)
    return goldset


def get_unique_gold_ann_set(goldann):
    """
    Load a gold standard consisting of a list of unique entities
    :param goldann: path to annotation
    :return: Set of gold standard annotations
    """
    with codecs.open(goldann, 'r', 'utf-8') as goldfile:
        gold = [line.strip() for line in goldfile if line.strip()]
    return gold, None


def compare_results(offsets, goldoffsets, corpus, getwords=True, evaltype="entity", entities=[]):
    """
    Compare system results with a gold standard, works for both NER and RE
    :param offsets: system results dictionary, offset tuples (did, start, end, text): more info
    :param goldoffsets: dictionary with the gold standard annotations (did, start, end [, text]): more info
    :param corpus: Reference corpus
    :return: Lines to write into a report files, set of TPs, FPs and FNs
    """
    #TODO: check if size of offsets and goldoffsets tuples is the same
    report = []
    #if not getwords:
    # offsets = set([x[:4] for x in offsets.keys()])
    if type(goldoffsets) is set:
        goldoffsets = {s: [] for s in goldoffsets}
    # goldoffsets = set([x[:4] for x in goldoffsets.keys()])
    # print len(goldoffsets), len(offsets)
    if len(entities) > 0:
        goldoffsets_keys = goldoffsets.keys()
        for k in goldoffsets_keys:
            if k[0] not in entities or k[1] not in entities[k[0]] or k[2] not in entities[k[0]]:
                del goldoffsets[k]
    tps = set(offsets.keys()) & set(goldoffsets.keys())
    fps = set(offsets.keys()) - set(goldoffsets.keys())
    fns = set(goldoffsets.keys()) - set(offsets.keys())
    fpreport, fpwords = get_report(fps, corpus, offsets, getwords=getwords)
    fnreport, fnwords = get_report(fns, corpus, goldoffsets, getwords=getwords)
    tpreport, tpwords = get_report(tps, corpus, offsets, getwords=getwords)
    alldocs = set(fpreport.keys())
    alldocs = alldocs.union(fnreport.keys())
    alldocs = alldocs.union(tpreport.keys())
    if getwords:
        report.append("Common FPs")
        fpcounter = collections.Counter(fpwords)
        for w in fpcounter.most_common(10):
            report.append(w[0] + ": " + str(w[1]))
        report.append(">\n")
        report.append("Common FNs")
        fncounter = collections.Counter(fnwords)
        for w in fncounter.most_common(10):
            report.append(w[0] + ": " + str(w[1]))
        report.append(">\n")

    for d in list(alldocs):
        report.append(d)
        if d in tpreport:
            for x in tpreport[d]:
                report.append("TP:%s" % x)
        if d in fpreport:
            for x in fpreport[d]:
                report.append("FP:%s" % x)
        if d in fnreport:
            for x in fnreport[d]:
                report.append("FN:%s" % x)

    return report, tps, fps, fns


def get_report(results, corpus, more_info, getwords=True):
    """
        Get more information from results.
        :return: Lines to write to a report file, word that appear in this set
    """
    # TODO: use only offset tuples (did, start, end, text)
    report = {}
    words = []
    for t in results:
        if t[0] == "":
            did = "0"
        else:
            did = t[0]
        if t[0] != "" and t[0] not in corpus.documents:
            logging.debug("this doc is not in the corpus! %s" % t[0])
            # logging.info(corpus.documents.keys())
            continue
        start, end = t[1], t[2]
        if getwords:
            # doctext = corpus.documents[x[0]].text

            # if stype == "T":
            #     tokentext = corpus.documents[x[0]].title[start:end]
            # else:
                # tokentext = doctext[start:end]
            tokentext = t[3]
            words.append(tokentext)
        if did not in report:
            report[did] = []
        if getwords:
            # line = u"{}\t{}:{}\t{}\t{}".format(did, start, end, tokentext.encode('utf-8'), "\t".join(more_info[t]))
            line = u"{}\t{}:{}\t{}".format(did, start, end, tokentext)
        else:
            line = did + '\t' + start + ":" + end
        report[did].append(line)
    for d in report:
        report[d].sort()
    return report, words


def get_list_results(results, models, goldset, ths, rules, mode="ner"):
    """
    Write results files considering only doc-level unique entities, as well as a report file with basic stats
    :param results: ResultsNER object
    :param models: Base model path
    :param goldset: Set with gold standard annotations
    :param ths: Validation thresholds
    :param rules: Validation rules
    """

    print "saving results to {}".format(results.path + "_final.tsv")
    sysresults = results.corpus.get_unique_results(models, ths, rules, mode)
    print "{} unique entries".format(len(sysresults))
    with codecs.open(results.path + "_final.tsv", 'w', 'utf-8') as outfile:
        outfile.write('\n'.join(['\t'.join(x) for x in sysresults]))
    print "getting corpus entities..."
    entities = {}
    for did in results.corpus.documents:
        entities[did] = set()
        for sentence in results.corpus.documents[did].sentences:
            for s in sentence.entities.elist:
                for e in sentence.entities.elist[s]:
                    entities[did].add(e.normalized)
    if goldset:
        #lineset = set([(l[0], l[1].lower(), l[2].lower()) for l in sysresults])
        #goldset = set([(g[0], g[1].lower(), g[2].lower()) for g in goldset])
        reportlines, tps, fps, fns = compare_results(sysresults, goldset, results.corpus, getwords=True, entities=entities)
        with codecs.open(results.path + "_report.txt", 'w', "utf-8") as reportfile:
            reportfile.write("TPs: {!s}\nFPs: {!s}\n FNs: {!s}\n".format(len(tps), len(fps), len(fns)))
            if len(tps) == 0:
                precision = 0
                recall = 0
                fmeasure = 0
            else:
                precision = len(tps)/(len(tps) + len(fps))
                recall = len(tps)/(len(tps) + len(fns))
                fmeasure = (2*precision*recall)/(precision + recall)
            reportfile.write("Precision: {!s}\nRecall: {!s}\n".format(precision, recall))
            print "precision: {}".format(precision)
            print "recall: {}".format(recall)
            print "f-measure: {}".format(fmeasure)
            for line in reportlines:
                reportfile.write(line + '\n')
    else:

        print "no gold set"


def get_relations_results(results, model, gold_pairs, ths, rules, compare_text=True):
    system_pairs = {}
    pcount = 0
    ptrue = 0
    npairs = 0
    for did in results.document_pairs:
        # npairs += len(results.document_pairs[did].pairs)
        for p in results.document_pairs[did].pairs:
            pcount += 1
            if p.recognized_by.get(model) > 0:
                val = p.validate()
                if val:
                    ptrue += 1
                    pair = (did, (p.entities[0].dstart, p.entities[0].dend), (p.entities[1].dstart, p.entities[1].dend),
                              u"{}={}>{}".format(p.entities[0].text, p.relation, p.entities[1].text))
                    #system_pairs.append(pair)
                    between_text = results.corpus.documents[p.entities[0].did].text[p.entities[0].dend:p.entities[1].dstart]
                    system_pairs[pair] = [u"{}=>{}".format(p.entities[0].type, p.entities[1].type), between_text]
    # print random.sample(system_pairs, 5)
    # print random.sample(gold_pairs, 5)
    # print pcount, ptrue, npairs
    if not compare_text:
        gold_pairs = [(o[0], o[1], o[2], "") for o in gold_pairs]
    reportlines, tps, fps, fns = compare_results(system_pairs, gold_pairs, results.corpus, getwords=compare_text)
    with codecs.open(results.path + "_report.txt", 'w', "utf-8") as reportfile:
        print "writing report to {}_report.txt".format(results.path)
        reportfile.write("TPs: {!s}\nFPs: {!s}\nFNs: {!s}\n".format(len(tps), len(fps), len(fns)))
        reportfile.write(">\n")
        if len(tps) == 0:
            precision, recall, fmeasure = 0, 0, 0
        else:
            precision, recall = len(tps)/(len(tps) + len(fps)), len(tps)/(len(tps) + len(fns))
            fmeasure = 2*precision*recall/(precision+recall)
        reportfile.write("Precision: {!s}\nRecall: {!s}\n".format(precision, recall))
        reportfile.write(">\n")
        for line in reportlines:
            reportfile.write(line + '\n')
    print "Precision: {:.3f}".format(precision)
    print "Recall: {:.3f}".format(recall)
    print "Fmeasure: {:.3f}".format(fmeasure)
    return precision, recall

def get_results(results, models, gold_offsets, ths, rules, compare_text=True):
    """
    Write a report file with basic stats
    :param results: ResultsNER object
    :param models: Base model path
    :param goldset: Set with gold standard annotations
    :param ths: Validation thresholds
    :param rules: Validation rules
    """
    offsets = results.corpus.get_entity_offsets(models, ths, rules)
    # logging.debug(offsets)
    for o in offsets:
        if o[0] not in results.corpus.documents:
            print "DID not found! {}".format(o[0])
            sys.exit()
    if not compare_text: #e.g. gold standard does not include the original text
        offsets = [(o[0], o[1], o[2], "") for o in offsets]
    # logging.info("system entities: {}; gold entities: {}".format(offsets, gold_offsets))
    reportlines, tps, fps, fns = compare_results(offsets, gold_offsets, results.corpus, getwords=compare_text)
    with codecs.open(results.path + "_report.txt", 'w', "utf-8") as reportfile:
        print "writing report to {}_report.txt".format(results.path)
        reportfile.write("TPs: {!s}\nFPs: {!s}\nFNs: {!s}\n".format(len(tps), len(fps), len(fns)))
        reportfile.write(">\n")
        if len(tps) == 0:
            precision = 0
            recall = 0
            fmeasure = 0
        else:
            precision = len(tps)/(len(tps) + len(fps))
            recall = len(tps)/(len(tps) + len(fns))
            fmeasure = 2 * precision * recall / (precision + recall)
        reportfile.write("Precision: {!s}\nRecall: {!s}\n".format(precision, recall))
        reportfile.write(">\n")
        for line in reportlines:
            reportfile.write(line + '\n')
    print "Precision: {:.3f}".format(precision)
    print "Recall: {:.3f}".format(recall)
    print "Fmeasure: {:.3f}".format(fmeasure)
    return precision, recall


def main():
    start_time = time.time()
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("action", default="evaluate",
                      help="Actions to be performed.")
    parser.add_argument("goldstd", default="chemdner_sample",
                        help="Gold standard to be used.",
                        choices=paths.keys())
    parser.add_argument("--corpus", dest="corpus",
                      default="data/chemdner_sample_abstracts.txt.pickle",
                      help="format path")
    parser.add_argument("--results", dest="results", help="Results object pickle.", nargs='+')
    parser.add_argument("--models", dest="models", help="model destination path, without extension", default="combined")
    parser.add_argument("--ensemble", dest="ensemble", help="name/path of ensemble classifier", default="combined")
    parser.add_argument("--chebi", dest="chebi", help="Chebi mapping threshold.", default=0, type=float)
    parser.add_argument("--ssm", dest="ssm", help="SSM threshold.", default=0, type=float)
    parser.add_argument("--measure", dest="measure", help="semantic similarity measure", default="simui")
    parser.add_argument("--log", action="store", dest="loglevel", default="WARNING", help="Log level")
    parser.add_argument("--submodels", default="", nargs='+', help="sub types of classifiers"),
    parser.add_argument("--rules", default=[], nargs='+', help="aditional post processing rules")
    parser.add_argument("--features", default=["chebi", "case", "number", "greek", "dashes", "commas", "length", "chemwords", "bow"],
                        nargs='+', help="aditional features for ensemble classifier")
    parser.add_argument("--doctype", dest="doctype", help="type of document to be considered", default="all")
    parser.add_argument("--entitytype", dest="etype", help="type of entities to be considered", default="all")
    parser.add_argument("--pairtype", dest="ptype", help="type of pairs to be considered", default=None)
    parser.add_argument("--external", action="store_true", default=False, help="Run external evaluation script, depends on corpus type")
    parser.add_argument("--output", dest="output", help="Final output", default=None)
    options = parser.parse_args()

    numeric_level = getattr(logging, options.loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % options.loglevel)
    while len(logging.root.handlers) > 0:
        logging.root.removeHandler(logging.root.handlers[-1])
    logging_format = '%(asctime)s %(levelname)s %(filename)s:%(lineno)s:%(funcName)s %(message)s'
    logging.basicConfig(level=numeric_level, format=logging_format)
    logging.getLogger().setLevel(numeric_level)
    logging.info("Processing action {0} on {1}".format(options.action, options.goldstd))
    results_list = []
    for results_path in options.results:
        logging.info("loading results %s" % results_path + ".pickle")
        if os.path.exists(results_path + ".pickle"):
            results = pickle.load(open(results_path + ".pickle", 'rb'))
            results.load_corpus(options.goldstd)
            results.path = results_path
            results_list.append(results)
        else:
            print "results not found"
            print results_path
            sys.exit()

    if options.action in ("combine", "train_ensemble", "test_ensemble", "savetocorpus"):
        # merge the results of various results corresponding to different classifiers
        # the entities of each sentence are added according to the classifier of each result
        # every result should correspond to the same gold standard
        # save to the first results path
        #results.load_corpus(options.goldstd)
        #logging.info("combining results...")
        #results.combine_results(options.models, options.models + "_combined")
        #results.save(options.results + "_combined.pickle")
        base_result = results_list[0]
        for result in results_list[1:]:
            logging.info("adding {}...".format(result.path))
            base_result.add_results(result)

        if options.action == "combine":
            base_result.combine_results(options.etype, options.models)
            n_sentences, n_docs, n_entities, n_relations = 0, 0, 0, 0
            for did in base_result.corpus.documents:
                n_docs += 1
                for sentence in base_result.corpus.documents[did].sentences:
                    n_sentences += 1
                    for e in sentence.entities.elist[options.models]:
                        n_entities += 1
            logging.info("Combined {} docs, {} sentences, {} entities".format(n_docs, n_sentences, n_entities))
            base_result.save(options.models + ".pickle")
        elif options.action == "savetocorpus":
            base_result.corpus.save(options.output + ".pickle")
        elif options.action == "train_ensemble":
            pipeline = Pipeline(
                [
                    #('clf', SGDClassifier(loss='hinge', penalty='l1', alpha=0.0001, n_iter=5, random_state=42)),
                    #('clf', SGDClassifier())
                     #('clf', svm.NuSVC(nu=0.01 ))
                    # ('clf', RandomForestClassifier(class_weight={False:1, True:1}, n_jobs=-1, criterion="entropy", warm_start=True))
                    #('clf', tree.DecisionTreeClassifier(criterion="entropy")),
                     #('clf', MultinomialNB())
                    #('clf', GaussianNB())
                    ('clf', svm.SVC(kernel="rbf", degree=2, C=1))
                    #('clf', DummyClassifier(strategy="constant", constant=True))
                ])
            print pipeline
            base_result.train_ensemble(pipeline, options.models, options.etype)
        elif options.action == "test_ensemble":
            pipeline = joblib.load("{}/{}/{}.pkl".format("models/ensemble/", options.models, options.models))
            print pipeline
            base_result.test_ensemble(pipeline, options.models, options.etype)
            base_result.save("results/" + options.models + ".pickle")

    elif options.action in ("evaluate", "evaluate_list", "count_entities"):
        counts = {}
        if options.action == "count_entities":
            for did in results_list[0].corpus.documents:
                for sentence in results_list[0].corpus.documents[did].sentences:
                    print sentence.entities.elist.keys()
                    if options.models in sentence.entities.elist:
                        for e in sentence.entities.elist[options.models]:
                            if e.type not in counts:
                                counts[e.type] = 0
                            counts[e.type] += 1
            print counts
            sys.exit()
        if paths[options.goldstd].get("annotations"):
            logging.info("loading gold standard %s" % paths[options.goldstd]["annotations"])
            goldset = get_gold_ann_set(paths[options.goldstd]["format"], paths[options.goldstd]["annotations"],
                                       options.etype, options.ptype, paths[options.goldstd]["text"])
        else:
            goldset = ({}, {})
        logging.info("using thresholds: chebi > {!s} ssm > {!s}".format(options.chebi, options.ssm))
        #results.load_corpus(options.goldstd)
        #results.path = options.results
        ths = {"chebi": options.chebi}
        if options.ssm > 0:
            ths["ssm"] = options.ssm
        if options.action == "evaluate":
            for result in results_list:
                if options.ptype: # evaluate this pair type
                    get_relations_results(result, options.models, goldset[1], ths, options.rules)
                else: # evaluate an entity type
                    get_results(result, options.models, goldset[0], ths, options.rules)
            if options.external:
                write_chemdner_files(results, options.models, goldset, ths, options.rules)
                #evaluation = run_chemdner_evaluation(paths[options.goldstd]["cem"],
                #                                     options.results[0] + ".tsv")
                #print evaluation
        elif options.action == "evaluate_list": # ignore the spans, the gold standard is a list of unique entities
            for result in results_list:
                if options.ptype:
                    get_list_results(result, options.models, goldset[1], ths, options.rules, mode="re")
                else:
                    get_list_results(result, options.models, goldset[0], ths, options.rules)

    total_time = time.time() - start_time
    logging.info("Total time: %ss" % total_time)
if __name__ == "__main__":
    main()
