import logging
import pickle

from text.chemical_entity import ChemdnerAnnotation
from config import config
from copy import deepcopy
#from model import SINGLE_TAG, START_TAG, MIDDLE_TAG, END_TAG, OTHER_TAG
SINGLE_TAG = "single"
START_TAG = "start"
END_TAG = "end"
MIDDLE_TAG = "middle"
OTHER_TAG = "other"

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

    def get_ner_results(self, corpus, model):
        """
            Read the results obtained with the model, add the entities to the entities set, and also
                to each sentence of the corpus object.
        """
        logging.debug("%s sentences", (len(model.predicted)))
        sentence_entities = {} # sid -> Entities
        for si in range(len(model.predicted)):
            did = '.'.join(model.sids[si].split(".")[:-1])
            this_sentence = corpus.documents[did].get_sentence(model.sids[si])
            #logging.debug("getting results for %s", model.sids[si])
            new_entity = None
            for ti in range(len(model.predicted[si])):
                #if model.predicted[si][ti] != OTHER_TAG:
                    #logging.debug("%s %s %s", model.predicted[si][ti], model.labels[si][ti],
                    #              model.tokens[si][ti].text)
                if model.predicted[si][ti] == SINGLE_TAG:
                    # logging.debug("found a single: %s", model.tokens[si][ti].text)
                    single_entity = ChemdnerAnnotation(tokens=[model.tokens[si][ti]],
                                                      sid=model.sids[si], did=did,
                                                      text=model.tokens[si][ti].text,
                                                      score=model.scores[si][ti])
                    #logging.info("%s single: %s" % (single_entity.sid, str(single_entity)))
                    eid = this_sentence.tag_entity(start=model.tokens[si][ti].start,
                                            end=model.tokens[si][ti].end, subtype="chem",
                                            entity=single_entity, source=model.path)
                    single_entity.eid = eid
                    self.entities[eid] = single_entity # deepcopy
                    sentence_entities[this_sentence.sid] = this_sentence.entities
                elif model.predicted[si][ti] == START_TAG:
                    # logging.debug("found a start: %s", model.tokens[si][ti].text)
                    new_entity = ChemdnerAnnotation(tokens=[model.tokens[si][ti]],
                                                   sid=model.sids[si], did=did,
                                                   text=model.tokens[si][ti].text,
                                                   score=model.scores[si][ti])
                elif model.predicted[si][ti] == MIDDLE_TAG:
                    # TODO: fix mistakes
                    if not new_entity:
                        new_entity = ChemdnerAnnotation(tokens=[model.tokens[si][ti]],
                                                   sid=model.sids[si], did=did,
                                                   text=model.tokens[si][ti].text,
                                                   score=model.scores[si][ti])
                        #logging.debug("started from a middle: {0}".format(new_entity))
                    else:
                        new_entity.tokens.append(model.tokens[si][ti])
                        new_entity.score += model.scores[si][ti]
                    # else:
                    #    logging.debug("found a middle without start!: %s", model.tokens[i].text)
                elif model.predicted[si][ti] == END_TAG:
                    if not new_entity:
                        new_entity = ChemdnerAnnotation(tokens=[model.tokens[si][ti]],
                                                   sid=model.sids[si], did=did,
                                                   text=model.tokens[si][ti].text,
                                                   score=model.scores[si][ti])
                        #logging.debug("started from a end: {0}".format(new_entity))
                    else:
                        new_entity.tokens.append(model.tokens[si][ti])
                        new_entity.text= this_sentence.text[new_entity.tokens[0].start:new_entity.tokens[-1].end]
                        new_entity.end = new_entity.start + len(new_entity.text)
                        new_entity.dend = new_entity.dstart + len(new_entity.text)
                        new_entity.score += model.scores[si][ti]
                        new_entity.score = new_entity.score/len(new_entity.tokens)
                    #logging.info("%s end: %s" % (new_entity.sid, str(new_entity)))
                    #logging.debug("found the end: %s", ''.join([t.text for t in new_entity.tokens]))
                    eid = this_sentence.tag_entity(start=new_entity.tokens[0].start,
                        end=new_entity.tokens[-1].end, subtype="chem",
                        entity=new_entity, source=model.path)
                    new_entity.eid = eid
                    self.entities[eid] = new_entity # deepcopy
                    sentence_entities[this_sentence.sid] = this_sentence.entities
                    new_entity = None
                    logging.debug(str(self.entities[eid]))
                    # else:
                    #    logging.debug("found the end without start!: %s", model.tokens[i].text)
        self.corpus = corpus
        return sentence_entities

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