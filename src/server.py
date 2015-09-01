import argparse
import time
import json

__author__ = 'Andre'
import bottle
from corenlp import StanfordCoreNLP
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import logging
import codecs
from bottledaemon import daemon_run

from document import Document
from corpus import Corpus
from chemdner_corpus import ChemdnerCorpus
from taggercollection import TaggerCollection
from simpletagger import SimpleTaggerModel, feature_extractors
from results import ResultsNER
import chebi_resolution
from ssm import get_ssm
from ensemble_ner import EnsembleNER
import pubmed
import relations

class IICEServer(object):


    CORENLP_DIR = "bin/stanford-corenlp-full-2015-01-30/"


    def __init__(self, basemodel, ensemble_model, submodels):
        self.corenlpserver = StanfordCoreNLP(corenlp_path=self.CORENLP_DIR,
                                            properties=self.CORENLP_DIR + "default.properties")
        self.basemodel = basemodel
        self.ensemble_model = ensemble_model
        self.subtypes = submodels
        self.models = TaggerCollection(basepath=self.basemodel)
        self.models.load_models()
        self.ensemble = EnsembleNER(self.ensemble_model, None, self.basemodel + "_combined", types=self.subtypes,
                                   features=[])
        self.ensemble.load()

    #app = Bottle()
    #run(reloader=True)
    def hello(self):
        return "Hello World!"

    def process_pubmed(self, pmid):
        text = pubmed.get_pubmed_abs(pmid)


    def process_multiple(self, text="", format="bioc"):
        test_corpus = self.generate_corpus(text)
        multiple_results = self.models.test_types(test_corpus)
        final_results = multiple_results.combine_results()
        final_results = add_chebi_mappings(final_results, self.basemodel)
        final_results = add_ssm_score(final_results, self.basemodel)
        final_results.combine_results(self.basemodel, self.basemodel + "_combined")

        self.ensemble.generate_data(final_results, supervisioned=False)
        self.ensemble.test()
        ensemble_results = ResultsNER(self.basemodel + "_combined_ensemble")
        ensemble_results.get_ensemble_results(self.ensemble, final_results.corpus, self.basemodel + "_combined")
        #output = get_output(final_results, basemodel + "_combined")
        output = self.get_output(ensemble_results, self.basemodel + "_combined_ensemble", format)
        #output = self.get_output(final_results, self.basemodel + "_combined")
        #self.models.load_models()
        self.clean_up()
        return output

    def clean_up(self):

        for m in self.models.models:
            self.models.models[m].reset()
        self.models.basemodel.reset()

    def process(self, text="", modeltype="all"):
        test_corpus = self.generate_corpus(text)
        model = SimpleTaggerModel("models/chemdner_train_f13_lbfgs_" + modeltype)
        model.load_tagger()
        # load data into the model format
        model.load_data(test_corpus, feature_extractors.keys())
        # run the classifier on the data
        model.test(stats=False)
        results = ResultsNER("models/chemdner_train_f13_lbfgs_" + modeltype)
        # process the results
        results.get_ner_results(test_corpus, model)
        output = self.get_output(results, "models/chemdner_train_f13_lbfgs_" + modeltype)
        return output

    def get_relations(self):
        """
        Process the results dictionary, identify relations
        :return: results dictionary with relations
        """
        data = bottle.request.json
        for sentence in data["abstract"]["sentences"]:
            sentence_pairs = []
            for i1, e1 in enumerate(sentence["entities"]):
                for i2, e2 in enumerate(sentence["entities"][i1:])
                    sentence_pairs.append(e1, e2)

        return data

    def generate_corpus(self, text):
        """
        Create a corpus object from the input text.
        :param text:
        :return:
        """
        test_corpus = Corpus("")
        newdoc = Document(text, process=False, did="d0", title="Test document")
        newdoc.sentence_tokenize("biomedical")
        newdoc.process_document(self.corenlpserver, "biomedical")
        test_corpus.documents["d0"] = newdoc
        return test_corpus

    def get_output(self, results, model_name, format="bioc"):
        if format == "bioc":
            a = ET.Element('collection')
            bioc = results.corpus.documents["d0"].write_bioc_results(a, model_name)
            rough_string = ET.tostring(a, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            output = reparsed.toprettyxml(indent="\t")
        elif format == "chemdner":
             with codecs.open("/dev/null", 'w', 'utf-8') as outfile:
                lines = results.corpus.write_chemdner_results(model_name, outfile)
                output = ""
                for l in lines:
                    output += ' '.join(l) + " "
        else: # default should be json
            results_dic = {}
            results_dic = results.corpus.documents["d0"].get_dic(model_name)
            output = json.dumps(results_dic)
        return output

def add_chebi_mappings(results, source):
    """

    :param results: ResultsNER object
    :return:
    """
    mapped = 0
    not_mapped = 0
    total_score = 0
    for did in results.corpus.documents:
        for sentence in results.corpus.documents[did].sentences:
            for s in sentence.entities.elist:
                if s.startswith(source):
                    #if s != source:
                    #    logging.info("processing %s" % s)
                    for entity in sentence.entities.elist[s]:
                        chebi_info = chebi_resolution.find_chebi_term3(entity.text.encode("utf-8"))
                        entity.chebi_id = chebi_info[0]
                        entity.chebi_name = chebi_info[1]
                        entity.chebi_score = chebi_info[2]
                        # TODO: check for errors (FP and FN)
                        if chebi_info[2] == 0:
                            #logging.info("nothing for %s" % entity.text)
                            not_mapped += 1
                        else:
                            #logging.info("%s => %s %s" % (entity.text, chebi_info[1], chebi_info[2]))
                            mapped += 1
                            total_score += chebi_info[2]
    if mapped == 0:
        mapped = 0.000001
    logging.info("{0} mapped, {1} not mapped, average score: {2}".format(mapped, not_mapped, total_score/mapped))
    return results

def add_ssm_score(results, source):
    total = 0
    scores = 0
    for did in results.corpus.documents:
        for sentence in results.corpus.documents[did].sentences:
            for s in sentence.entities.elist:
                if s.startswith(source):
                    sentence.entities.elist[s] = get_ssm(sentence.entities.elist[s], "simui", 0)
                    total += 1
                    scores += sum([e.ssm_score for e in sentence.entities.elist[s]])
                    #for entity in results.corpus[did][sid].elist[s]:
                    #    logging.info("%s %s %s %s" % (entity.text, entity.chebi_name, entity.ssm_score,
                    #                                  entity.ssm_chebi_name))
    if total == 0:
        total = 0.00001
    logging.info("average ssm score: {0}".format(scores/total))
    return results


def main():
    starttime = time.time()
    #parser = argparse.ArgumentParser(description='')
    #parser.add_argument("action", choices=["start", "stop"])
    #parser.add_argument("--basemodel", dest="model", help="base model path")
    #parser.add_argument("-t", "--test", action="store_true",
    #                help="run a test instead of the server")
    #parser.add_argument("--log", action="store", dest="loglevel", default="WARNING", help="Log level")
    #options = parser.parse_args()
    numeric_level = getattr(logging, "DEBUG", None)
    #if not isinstance(numeric_level, int):
    #    raise ValueError('Invalid log level: %s' % options.loglevel)

    #while len(logging.root.handlers) > 0:
    #    logging.root.removeHandler(logging.root.handlers[-1])
    logging_format = '%(asctime)s %(levelname)s %(filename)s:%(lineno)s:%(funcName)s %(message)s'
    logging.basicConfig(level=numeric_level, format=logging_format)
    logging.getLogger().setLevel(numeric_level)

    base_model = "models/chemdner_train"
    ensemble_model = "models/ensemble_ner/train_on_dev"
    #submodels = [base_model + "_" + t for t in ChemdnerCorpus.chemdner_types]
    if base_model.split("/")[-1].startswith("chemdner+ddi"):
        subtypes = ["drug", "group", "brand", "drug_n"] + ["IDENTIFIER", "MULTIPLE",
                                                                 "FAMILY", "FORMULA", "SYSTEMATIC",
                                                                 "ABBREVIATION", "TRIVIAL"] + ["chemdner", "ddi"]
    elif base_model.split("/")[-1].startswith("ddi"):
        subtypes = ["drug", "group", "brand", "drug_n", "all"]
    elif base_model.split("/")[-1].startswith("chemdner"):
        subtypes = ["IDENTIFIER", "MULTIPLE", "FAMILY", "FORMULA", "SYSTEMATIC", "ABBREVIATION", "TRIVIAL", "all"]
    submodels = ['_'.join(base_model.split("_")[:]) + "_" + t for t in subtypes[:-1]] #ignore the "all"
    logging.debug("Initializing the server...")
    server = IICEServer(base_model, ensemble_model, submodels)
    logging.debug("done.")
    load_time = time.time() - starttime
    starttime = time.time()
    '''if options.test:
        text = "Primary Leydig cells obtained from bank vole testes and the established tumor Leydig cell line (MA-10) have been used to explore the effects of 4-tert-octylphenol (OP). Leydig cells were treated with two concentrations of OP (10(-4)M, 10(-8)M) alone or concomitantly with anti-estrogen ICI 182,780 (1M). In OP-treated bank vole Leydig cells, inhomogeneous staining of estrogen receptor (ER) within cell nuclei was found, whereas it was of various intensity among MA-10 Leydig cells. The expression of ER mRNA and protein decreased in both primary and immortalized Leydig cells independently of OP dose. ICI partially reversed these effects at mRNA level while at protein level abrogation was found only in vole cells. Dissimilar action of OP on cAMP and androgen production was also observed. This study provides further evidence that OP shows estrogenic properties acting on Leydig cells. However, its effect is diverse depending on the cellular origin. "
        logging.debug("test with this text: {}".format(text))
        output = server.process_multiple(text)
        print output
        process_time = time.time() - starttime
        # second document
        text = "Azole class of compounds are well known for their excellent therapeutic properties. Present paper describes about the synthesis of three series of new 1,2,4-triazole and benzoxazole derivatives containing substituted pyrazole moiety (11a-d, 12a-d and 13a-d). The newly synthesized compounds were characterized by spectral studies and also by C, H, N analyses. All the synthesized compounds were screened for their analgesic activity by the tail flick method. The antimicrobial activity of the new derivatives was also performed by Minimum Inhibitory Concentration (MIC) by the serial dilution method. The results revealed that the compound 11c having 2,5-dichlorothiophene substituent on pyrazole moiety and a triazole ring showed significant analgesic and antimicrobial activity."
        logging.debug("test with this text: {}".format(text))
        output = server.process_multiple(text)
        print output
        logging.info("loading time: {}; process time: {}".format(load_time, process_time))
    else:'''
    bottle.route("/hello")(server.hello)
    bottle.route("/iice/chemdner/<text>/all.<format>", method='POST')(server.process_multiple)
    bottle.route("/iice/chemdner/<text>/<modeltype>", method='POST')(server.process)
    bottle.route("/iice/relations", method='POST')(server.get_relations)
    #daemon_run(host='10.10.4.63', port=8080, logfile="server.log", pidfile="server.pid")
    bottle.run(host='10.10.4.63', port=8080, DEBUG=True)
if __name__ == "__main__":
    main()