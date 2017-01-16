import logging
import math
import sys
import os

from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn import svm, tree
from sklearn.externals import joblib

from classification.model import Model
from classification.results import ResultsNER

class EnsembleModel(Model):
    def __init__(self, path, etype, **kwargs):
        super(EnsembleModel, self).__init__(path, etype=etype, **kwargs)
        self.basedir = "models/ensemble/"
        self.goldstd = kwargs.get("goldstd")
        self.data = {}
        self.offsets = []
        self.pipeline = Pipeline(
            [
                #('clf', SGDClassifier(loss='hinge', penalty='l1', alpha=0.0001, n_iter=5, random_state=42)),
                #('clf', SGDClassifier())
                # ('clf', svm.NuSVC(nu=0.01 ))
                ('clf', RandomForestClassifier(class_weight={False:1, True:1}, n_jobs=-1, criterion="entropy", warm_start=True))
                # ('clf', tree.DecisionTreeClassifier(criterion="entropy")),
                # ('clf', MultinomialNB())
                # ('clf', GaussianNB())
                #('clf', svm.SVC(kernel="rbf", degree=2, C=1)),
                #('clf', svm.SVC(kernel="linear", C=2))
                #('clf', DummyClassifier(strategy="constant", constant=True))
            ])

    def train(self):
        #train_data, labels, offsets = self.generate_data(self.etype)
        print "training ensemble classifier..."
        #print self.train_data, self.train_labels
        pipeline = self.pipeline.fit(self.train_data, self.train_labels)
        if not os.path.exists(self.basedir + self.path):
            os.makedirs(self.basedir + self.path)
        print "Training complete, saving to {}/{}/{}.pkl".format(self.basedir, self.path, self.path)
        joblib.dump(pipeline, "{}/{}/{}.pkl".format(self.basedir, self.path, self.path))

    def load_tagger(self):
        self.pipeline = joblib.load("{}/{}/{}.pkl".format(self.basedir, self.path, self.path))

    def test(self, corpus):
        #train_data, labels, offsets = self.generate_data(self.etype, mode="test")
        pred = self.pipeline.predict(self.train_data)
        #print pred
        #results = self.process_results(corpus)
        results = ResultsNER(self.path)
        results.corpus = corpus
        for i, p in enumerate(pred):
            if p:
                sentence = corpus.get_sentence(self.offsets[i][0])
                eid = sentence.tag_entity(self.offsets[i][1], self.offsets[i][2], self.etype, source=self.path, score=1)
                results.entities[eid] = sentence.entities.get_entity(eid, self.path)
            #else:
            #    print self.offsets[i]
        return results

    def load_data(self, corpus, flist, mode="train", doctype="all"):
        """
        Use scikit to train a pipeline to classify entities as correct or incorrect
        features consist in the classifiers that identified the entity
        :param modelname:
        :return:
        """
        features = set()
        gs_labels = set()
        # collect offsets from every model (except gold standard) and add classifier score
        all_models = set()
        # merge the results of this set with another set
        for did in corpus.documents:
            # logging.debug(did)
            for sentence in corpus.documents[did].sentences:
                #print sentence.entities.elist.keys()
                if "goldstandard_{}".format(self.etype) in sentence.entities.elist:
                    sentence_eids = [e.eid for e in sentence.entities.elist["goldstandard_{}".format(self.etype)]]
                    # print sentence_eids, [e.eid for e in sentence.entities.elist["results/{}".format(self.goldstd)]]
                else:
                    sentence_eids = []
                    # print "no gold standard", sentence.entities.elist.keys()
                if "results/{}".format(self.goldstd) not in sentence.entities.elist:
                    print sentence.sid, "not entities", "results/{}".format(self.goldstd), sentence.entities.elist.keys()
                    continue
                for e in sentence.entities.elist["results/{}".format(self.goldstd)]:
                    #print sentence_eids, e.eid
                    # logging.info("%s - %s" % (self.sid, s))
                    # use everything except what's already combined and gold standard
                    # if any([word in e.text for word in self.stopwords]):
                    #    logging.info("ignored stopword %s" % e.text)
                    #    continue
                    # eid_alt =  e.sid + ":" + str(e.dstart) + ':' + str(e.dend)
                    #if not s.startswith("goldstandard") and s.endswith(etype):
                    # next_eid = "{0}.e{1}".format(e.sid, len(combined))
                    # eid_offset = Offset(e.dstart, e.dend, text=e.text, sid=e.sid, eid=next_eid)
                    # check for perfect overlaps only
                    offset = (sentence.sid, e.start, e.end)
                    if offset not in self.offsets:
                        self.offsets.append(offset)
                        self.data[offset] = {}
                    #print e.text.encode("utf8"),
                    for f in e.scores:
                        features.add(f)
                        #print f, ":", e.scores[f],
                        self.data[offset][f] = e.scores[f]
                    #print
                    if mode == "train" and e.eid in sentence_eids:
                        #for e in sentence.entities.elist[s]:
                        #offset = (sentence.sid, e.start, e.end)
                        gs_labels.add(offset)
                        #print gs_labels
                    # else:
                    #      print mode, e.eid in sentence_eids, e.eid, sentence_eids

        self.train_data = []
        self.train_labels = []
        features = sorted(list(features))
        print "using these features...", features
        # print gs_labels
        for o in self.offsets:
            of = []
            for f in features:
                if f in self.data[o]:
                    of.append(self.data[o][f])
                else:
                    of.append(0)
            self.train_data.append(of)
            if mode == "train" and o in gs_labels:
                self.train_labels.append(True)
            else:
                # print o, gs_labels
                self.train_labels.append(False)
        print "labels", set(self.train_labels)
        # print features
        # for i, l in enumerate(train_labels[:10]):
        #     print train_data[i], l
        #return train_data, train_labels, offsets

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