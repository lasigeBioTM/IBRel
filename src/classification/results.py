import logging
import pickle

from text.chemical_entity import ChemicalEntity
from config import config
from copy import deepcopy
#from model import SINGLE_TAG, START_TAG, MIDDLE_TAG, END_TAG, OTHER_TAG
SINGLE_TAG = "single"
START_TAG = "start"
END_TAG = "end"
MIDDLE_TAG = "middle"
OTHER_TAG = "other"

class ResultsRE(object):
    def __init__(self, name):
        self.pairs = {}
        self.name = name
        self.corpus = None
        self.document_pairs = {}

    def save(self, path):
        # no need to save the whole corpus, only the entities of each sentence are necessary
        # because the full corpus is already saved on a diferent pickle
        logging.info("Saving results to {}".format(path))
        reduced_corpus = {}
        for did in self.corpus.documents:
            self.document_pairs[did] = self.corpus.documents[did].pairs
            reduced_corpus[did] = {}
            for sentence in self.corpus.documents[did].sentences:
                reduced_corpus[did][sentence.sid] = sentence.entities
        self.corpus = reduced_corpus
        pickle.dump(self, open(path, "wb"))

    def load_corpus(self, goldstd):
        logging.info("loading corpus %s" % config.paths[goldstd]["corpus"])
        corpus = pickle.load(open(config.paths[goldstd]["corpus"]))

        for did in corpus.documents:
            for sentence in corpus.documents[did].sentences:
                sentence.entities = self.corpus[did][sentence.sid]
                #for entity in sentence.entities.elist[options.models]:
                #    print entity.chebi_score,

        self.corpus = corpus

class ResultsNER(object):
    """Store a set of entities related to a corpus or input text """
    def __init__(self, name):
        self.entities = {}
        self.name = name
        self.corpus = None

    def get_ensemble_results(self, ensemble, corpus, model):
        """
            Go through every entity in corpus and if it was predicted true by the ensemble, save to entities,
            otherwise, delete it.
        """
        for did in corpus.documents:
            for sentence in corpus.documents[did].sentences:
                new_entities = []
                for entity in sentence.entities.elist[model]:
                    sentence_type = "A"
                    if sentence.sid.endswith("s0"):
                        sentence_type = "T"
                    id = (did, "{0}:{1}:{2}".format(sentence_type, entity.dstart, entity.dend), "1")
                    if id not in ensemble.ids:
                        logging.debug("this is new! {0}".format(entity))
                        continue
                    predicted_index = ensemble.ids.index(id)
                    #logging.info(predicted_index)
                    if ensemble.predicted[predicted_index][1] > 0.5:
                        self.entities[entity.eid] = entity
                        #logging.info("good entity: {}".format(entity.text.encode("utf8")))
                        new_entities.append(entity)
                    #else:
                    #    logging.info("bad entity: {}".format(entity.text.encode("utf8")))
                sentence.entities.elist[self.name] = new_entities
        self.corpus = corpus

    def save(self, path):
        # no need to save the whole corpus, only the entities of each sentence are necessary
        # because the full corpus is already saved on a diferent pickle
        logging.info("Saving results to {}".format(path))
        reduced_corpus = {}
        for did in self.corpus.documents:
            reduced_corpus[did] = {}
            for sentence in self.corpus.documents[did].sentences:
                reduced_corpus[did][sentence.sid] = sentence.entities
        self.corpus = reduced_corpus
        pickle.dump(self, open(path, "wb"))
    
    def save_chemdner(self):
        pass

    def load_corpus(self, goldstd):
        logging.info("loading corpus %s" % config.paths[goldstd]["corpus"])
        corpus = pickle.load(open(config.paths[goldstd]["corpus"]))

        for did in corpus.documents:
            for sentence in corpus.documents[did].sentences:
                sentence.entities = self.corpus[did][sentence.sid]
                #for entity in sentence.entities.elist[options.models]:
                #    print entity.chebi_score,

        self.corpus = corpus

    def combine_results(self, basemodel, name):
        # add another set of anotations to each sentence, ending in combined
        # each entity from this dataset should have a unique ID and a recognized_by attribute
        scores = 0
        total = 0
        for did in self.corpus.documents:
            #logging.debug(did)
            for sentence in self.corpus.documents[did].sentences:
                #logging.debug(sentence.sid)
                sentence.entities.combine_entities(basemodel, name)
                for e in sentence.entities.elist[name]:
                    total += 1
                    #logging.info("{} - {}".format(e.text, e.score))
                    if len(e.recognized_by) > 1:
                        scores += sum(e.score.values())/len(e.score.values())
                    elif len == 1:
                        scores += e.score.values()[0]
                    #if e.score < 0.8:
                    #    logging.info("{0} score of {1}".format(e.text.encode("utf-8"),
                    #                                            e.score))
        if total > 0:
            logging.info("{0} entities average confidence of {1}".format(total, scores/total))


class ResultSetNER(object):
    """
    Organize and process a set a results from a TaggerCollection
    """
    def __init__(self, corpus, basepath):
        self.results = [] # list of ResultsNER
        self.corpus = corpus
        self.basepath = basepath

    def add_results(self, res):
        self.results.append(res)

    def combine_results(self):
        """
        Combine the results from multiple classifiers stored in self.results.
        Process these results, and generate a ResultsNER object
        :return: ResultsNER object of the combined results of the classifiers
        """
        final_results = ResultsNER(self.basepath)
        final_results.corpus = self.corpus
        return final_results
