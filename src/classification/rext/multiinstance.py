from __future__ import unicode_literals
import os
import logging
import random
import sys
import misvm
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline

from classification.rext.kernelmodels import ReModel
from subprocess import Popen, PIPE
import platform
import itertools
import codecs
from classification.results import ResultsRE
from config import config
from text.pair import Pairs

class MILClassifier(ReModel):
    def __init__(self, corpus, pairtype, relations, modelname="mil_classifier.model", train=False, ner="goldstandard"):
        super(MILClassifier, self).__init__()
        self.modelname = modelname
        self.pairs = {}
        self.instances = {}  # bags of instances (e1.normalized, e2.normalized) -> all instances with these two entities
        self.labels = {}
        self.bag_labels = []
        self.data = []
        self.predicted = {}
        self.resultsfile = None
        self.examplesfile = None
        self.ner_model = ner
        self.vectorizer = CountVectorizer(min_df=1)
        # self.classifier = misvm.MISVM(kernel='linear', C=1.0, max_iters=50)
        self.text_clf = Pipeline(
            [#('vect', CountVectorizer(analyzer='char_wb', ngram_range=(3, 20), min_df=0.0, max_df=0.7)),
             #('vect', CountVectorizer(ngram_range=(1,3), binary=False, max_features=None)),
             # ('tfidf', TfidfTransformer(use_idf=True, norm="l2")),
             # ('clf', SGDClassifier(loss='hinge', penalty='l1', alpha=0.0001, n_iter=5, random_state=42)),
             # ('clf', SGDClassifier())
             # ('clf', svm.NuSVC(nu=0.01 ))
             # ('clf', RandomForestClassifier(class_weight={False:1, True:2}, n_jobs=-1))
             ('clf', misvm.MISVM(kernel='linear', C=1.0, max_iters=50))
             # ('clf', DummyClassifier(strategy="constant", constant=True))
             ])
        self.generateMILdata(corpus, train=train, pairtype=pairtype, relations=relations)

    def generateMILdata(self, corpus, train, pairtype, relations):
        pairtypes = (config.relation_types[pairtype]["source_types"], config.relation_types[pairtype]["target_types"])
        # pairtypes = (config.event_types[pairtype]["source_types"], config.event_types[pairtype]["target_types"])
        pcount = 0
        truepcount = 0
        strue = 0
        sfalse = 0
        skipped = 0
        for sentence in corpus.get_sentences(self.ner_model):
            # for did in corpus.documents:
            did = sentence.did
            # doc_entities = corpus.documents[did].get_entities("goldstandard")
            sids = []
            # print len(corpus.type_sentences[pairtype])
            sentence_entities = [entity for entity in sentence.entities.elist[self.ner_model]]
            # print self.ner_model, sentence_entities
            for pair in itertools.permutations(sentence_entities, 2):
                if pair[0].type in pairtypes[0] and pair[1].type in pairtypes[1]:
                    if (pair[0].normalized, pair[1].normalized) not in self.instances:
                        self.instances[(pair[0].normalized, pair[1].normalized)] = []
                        self.labels[(pair[0].normalized, pair[1].normalized)] = -1  # assume no relation until it's confirmed

                    if (pair[0].normalized, pair[1].normalized) in relations:
                        self.labels[(pair[0].normalized, pair[1].normalized)] = 1
                        trueddi = 1
                        truepcount += 1
                        strue += 1
                    else:
                        sfalse += 1
                    pcount += 1
                    pair_features = self.get_pair_features(sentence, pair)
                    self.instances[(pair[0].normalized, pair[1].normalized)].append(pair_features)
        logging.info("True/total relations:{}/{} ({})".format(truepcount, pcount,
                                                              str(1.0 * truepcount / (pcount + 1))))

    def load_classifier(self):
        self.text_clf = joblib.load("{}/{}/{}.pkl".format(self.basedir, self.modelname, self.modelname))


    def train(self):
        logging.info("Building vocabulary...")
        all_text = []
        print self.vectorizer
        for pair in self.instances:
            for i in self.instances[pair]:
                all_text.append(i)
        # print all_text[:5]
        x = self.vectorizer.fit_transform(all_text)
        # print x, self.vectorizer
        vocab = self.vectorizer.get_feature_names()
        for pair in self.instances:
            bag = []
            #print self.instances[pair]
            for i in self.instances[pair]:
                # print i
                x = self.vectorizer.transform([i]).toarray()
                # print len(x[0]),
                bag.append(x[0])
            self.data.append(bag)
            # print bag
            self.bag_labels.append(self.labels[pair])
        print self.vectorizer
        # sys.exit()
        logging.info("Traning with {} pairs".format(str(len(self.labels))))
        self.text_clf = self.text_clf.fit(self.data, self.bag_labels)
        if not os.path.exists(self.basedir + self.modelname):
            os.makedirs(self.basedir + self.modelname)
        logging.info("Training complete, saving to {}/{}/{}.pkl".format(self.basedir, self.modelname, self.modelname))
        joblib.dump(self.text_clf, "{}/{}/{}.pkl".format(self.basedir, self.modelname, self.modelname))

    def test(self):
        self.predicted = self.text_clf.predict(self.features)

    def get_pair_features(self, sentence, pair):
        start1, end1, start2, end2 = pair[0].tokens[0].order, pair[0].tokens[-1].order,\
                                     pair[1].tokens[0].order, pair[1].tokens[-1].order
        token_order1 = [t.order for t in pair[0].tokens]
        token_order2 = [t.order for t in pair[1].tokens]
        order = "###normalorder###"
        entitytext = [pair[0].text, pair[1].text]
        if start1 > start2:
            order = "###reverseorder###"
            #start, end = pair[1].tokens[-1].order, pair[0].tokens[0].order
            start1, end2, start2, end2 = start2, end2, start1, end1
            entitytext = [pair[1].text, pair[0].text]
        #features = "-".join([t.text for t in sentence.tokens[start1-5:start1]]) # before 1st entity
        #features += " " + "-".join([t.text for t in sentence.tokens[end1:start2]])
        #features += " " + "-".join([t.text for t in sentence.tokens[end2:end2+5]]) # after 2nd entity
        features = " ".join([t.text for t in sentence.tokens])
        return features
