import os
import logging

import itertools

import numpy as np
import sys
from sklearn import svm
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn import metrics
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import f1_score, make_scorer

from classification.results import ResultsRE
from classification.rext.kernelmodels import ReModel


class ScikitRE(ReModel):
    def __init__(self, corpus, relationtype, modelname="scikit_classifier"):
        super(ScikitRE, self).__init__()
        self.modelname = modelname
        self.relationtype = relationtype
        self.corpus = corpus
        self.pairs = []
        self.features = []
        self.labels = []
        self.pred = []
        self.posfmeasure = make_scorer(f1_score, average='binary', pos_label=True)
        self.generate_data(corpus, modelname, relationtype)
        self.text_clf = Pipeline([('vect', CountVectorizer(ngram_range=(1,3), binary=False)),
                                  ('tfidf', TfidfTransformer(use_idf=True)),
                                  ('clf', SGDClassifier(loss='hinge', penalty='l1', alpha=0.0001, n_iter=5, random_state=42)),
                                  #('clf', svm.SVC(tol=0.001, kernel="linear"))
                                  #('clf', RandomForestClassifier())
                                  #('clf', MultinomialNB(alpha=0.1, fit_prior=False))
                                 ])

    def generate_data(self, corpus, modelname, pairtypes):
       # TODO: remove old model
        pcount = 0
        truepcount = 0
        ns = 0
        for sentence in corpus.get_sentences(hassource="goldstandard"):
            # logging.info("{}".format(sentence.sid))
            sentence_entities = sentence.entities.elist["goldstandard"]
            # logging.debug("sentence {} has {} entities ({})".format(sentence.sid, len(sentence_entities), len(sentence.entities.elist["goldstandard"])))
            for pair in itertools.combinations(sentence_entities, 2):
                # logging.info("{}=>{}|{}=>{}".format(pair[0].type, pair[1].type, pairtypes[0], pairtypes[1]))
                if pair[0].type == pairtypes[0] and pair[1].type == pairtypes[1] or \
                                        pair[1].type == pairtypes[0] and pair[0].type == pairtypes[1]:
                    # logging.debug(pair)
                    if pair[0].type != pairtypes[0]:
                        pair = (pair[1], pair[0])
                    pid = sentence.did + ".p" + str(pcount)
                    # self.pairs[pid] = (e1id, e2id)
                    f, label = self.generate_features(sentence, pair)
                    self.features.append(f)
                    self.labels.append(label)
                    self.pairs.append(pair)

    def generate_features(self, sentence, pair):
        if pair[1].eid in pair[0].targets:
            label = True
        else:
            label = False
        #f = sentence.text[pair[0].end:pair[1].start] + " " + ' '.join([t.pos for t in sentence.tokens])
        start, end = pair[0].tokens[-1].order, pair[1].tokens[0].order
        if start > end:
            start, end = pair[1].tokens[-1].order, pair[0].tokens[0].order
        #text = [t.lemma + "-" + t.pos for t in sentence.tokens[start:end]]
        text = [t.lemma + "-" + t.pos for t in sentence.tokens]
        f = ' '.join(text)
        return f, label

    def train(self):
        parameters = {'vect__ngram_range': [(1, 1), (1, 2), (1,3), (2,3)],
                      #'vect__binary': (True, False),

                      'clf__alpha': (1e-2, 1e-3, 1e-1, 1e-4, 1e-5),
                      'clf__loss': ('hinge', 'log'),
                      'clf__penalty': ('l2', 'l1', 'elasticnet')

                       # 'clf__nu': (0.5,0.6),
                      #'clf__kernel': ('rbf', 'linear', 'poly'),
                      # 'clf__tol': (1e-3, 1e-4, 1e-2, 1e-4)

                      #'clf__n_estimators': (10, 50, 100, 500),
                      #'clf__criterion': ('gini', 'entropy'),
                      #'clf__max_features': ("auto", "log2", 100,)

                     #'clf__alpha': (0, 1e-2, 1e-3, 1e-1, 1e-4, 1e-5),
                      #'clf__fit_prior': (False, True),
                     }
        gs_clf = GridSearchCV(self.text_clf, parameters, n_jobs=-1, scoring=self.posfmeasure)
        gs_clf = gs_clf.fit(self.features, self.labels)
        print gs_clf.best_params_
        # self.text_clf = self.text_clf.fit(self.features, self.labels)
        if not os.path.exists(self.basedir + self.modelname):
            os.makedirs(self.basedir + self.modelname)
        #joblib.dump(self.text_clf, "{}/{}/{}.pkl".format(self.basedir, self.modelname, self.modelname))
        joblib.dump(gs_clf.best_estimator_, "{}/{}/{}.pkl".format(self.basedir, self.modelname, self.modelname))
        # self.test()

    def load_classifier(self):
        self.text_clf = joblib.load("{}/{}/{}.pkl".format(self.basedir, self.modelname, self.modelname))

    def test(self):
        self.pred = self.text_clf.predict(self.features)

        # for doc, category in zip(self.features, self.pred):
        #     print '%r => %s' % (doc, category)
        print np.mean(self.pred == self.labels)
        print(metrics.classification_report(self.labels, self.pred))

    def get_predictions(self, corpus):
        results = ResultsRE(self.modelname)
        temppreds = {}
        for i in range(len(self.pred)):
            did = ".".join(self.pairs[i][0].sid.split(".")[:-1])
            pid = did + ".p" + str(i)
            if self.pred[i]:
                did = '.'.join(pid.split(".")[:-1])
                pair = corpus.documents[did].add_relation(self.pairs[i][0], self.pairs[i][1], "pair", relation=True)
                #pair = self.get_pair(pid, corpus)
                results.pairs[pid] = pair

                # logging.debug("{} - {} SLK: {}".format(pair.entities[0], pair.entities[1], p))
                #if pair not in temppreds:
                #    temppreds[pair] = []
                #temppreds[pair].append(p)
                results.pairs[pid].recognized_by["scikit"] = 1
        results.corpus = corpus
        return results

