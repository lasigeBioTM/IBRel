from __future__ import unicode_literals
import os
import logging
import cPickle as pickle
import random
import sys
from collections import Counter

import gc

import math
import misvm
from nltk import Tree
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
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
    def __init__(self, corpus, pairtype, relations, modelname="mil_classifier.model", test=False, ner="goldstandard",
                 generate=True):
        super(MILClassifier, self).__init__()
        self.modelname = modelname
        self.pairtype = pairtype
        self.pairs = {}  # (e1.normalized, e2.normalized) => (e1, e2)
        self.instances = {}  # bags of instances (e1.normalized, e2.normalized) -> all instances with these two entities
        self.labels = {} # (e1.normalized, e2.normalized) => label (-1/1)
        self.bag_labels = []  # ordered list of labels for each bag
        self.bag_pairs = []  # ordered list of pair labels (e1.normalized, e2.normalized)
        self.data = []  # ordered list of bags, each is a list of feature vectors
        self.predicted = []  # ordered list of predictions for each bag
        self.resultsfile = None
        self.examplesfile = None
        self.ner_model = ner
        self.vectorizer = CountVectorizer(min_df=0.2, ngram_range=(1, 1), token_pattern=r'\b\w+\-\w+\b')
        self.corpus = corpus

        #self.vectorizer = TfidfVectorizer(min_df=0.2, ngram_range=(1, 1), token_pattern=r'\b\w+\-\w+\b', max_features=)
        #self.classifier = misvm.MISVM(kernel='linear', C=1.0, max_iters=20)
        self.classifier = misvm.sMIL(kernel='linear', C=1)
        #self.classifier = misvm.MissSVM(kernel='linear', C=100) #, max_iters=20)
        #if generate:
        #    self.generateMILdata(test=test, pairtype=pairtype, relations=relations)

    def generateMILdata(self, test):
        """
        Generate data for self.instances, self.labels, self.pairs dictionaries bag->data
        :param corpus: Corpus object
        :param test: True if test mode, false if training
        :param pairtype: relation type string
        :param relations: list of relations
        :return:
        """
        # pairtypes = (config.relation_types[pairtype]["source_types"], config.relation_types[pairtype]["target_types"])
        # pairtypes = (config.event_types[pairtype]["source_types"], config.event_types[pairtype]["target_types"])
        pcount = 0
        truepcount = 0
        strue = 0
        sfalse = 0
        skipped = 0
        #for sentence in corpus.get_sentences(self.ner_model):
        for sentence in self.corpus.get_sentences(self.ner_model):
            # for did in corpus.documents:
            #did = sentence.did
            # doc_entities = corpus.documents[did].get_entities("goldstandard")
            sids = []
            # print len(corpus.type_sentences[pairtype])
            # sentence_models = set([m for m in sentence.entities.elist])
            # print self.ner_model, sentence_models
            self.generate_sentence_data(sentence, test=test)
        logging.info("True/total relations:{}/{} ({})".format(truepcount, pcount,
                                                              str(1.0 * truepcount / (pcount + 1))))
        # print "total bags:", len(self.instances)

    def write_to_file(self, filepath):
        with codecs.open(filepath, 'a', 'utf-8') as f:
            for bag in self.instances:
                f.write('#'.join(bag) + "\t")
                for i in self.instances[bag]:
                    f.write(i + "\t")
                f.write(str(self.labels[bag]) + "\n")

    def load_from_file(self, filepath):
        with codecs.open(filepath, 'r', 'utf-8') as f:
            for l in f:
                values = l.split("\t")
                bag = tuple(values[0].split("#"))
                self.instances[bag] = []
                for i in values[1:-1]:
                    self.instances[bag].append(i)
                self.labels[bag] = int(values[-1])

    def load_kb(self, kb_path):
        self.relations = set()
        with open(kb_path) as rfile:
            for l in rfile:
                self.relations.add(tuple(l.strip().split('\t')))

    def load_classifier(self):
        #self.classifier = joblib.load("{}/{}/{}.pkl".format(self.basedir, self.modelname, self.modelname))
        #self.vectorizer = joblib.load("{}/{}/{}_bow.pkl".format(self.basedir, self.modelname, self.modelname))
        with open("{}/{}/{}.pkl".format(self.basedir, self.modelname, self.modelname), 'r') as modelfile:
            self.classifier = pickle.loads(modelfile.read())
        with open("{}/{}/{}_bow.pkl".format(self.basedir, self.modelname, self.modelname), 'r') as modelfile:
            self.vectorizer = pickle.loads(modelfile.read())

    def generate_vectorizer(self):
        logging.info("Building vocabulary...")
        all_text = []
        # print self.vectorizer
        for pair in self.instances:
            for i in self.instances[pair]:
                all_text.append(i)
        # print all_text[:5]
        x = self.vectorizer.fit_transform(all_text)
        # print x, self.vectorizer
        #vocab = self.vectorizer.get_feature_names()
        #print vocab

    def vectorize_text(self):
        for pair in self.instances:
            bag = []
            # print self.instances[pair]

            for i in self.instances[pair]:

                x = self.vectorizer.transform([i]).toarray()
                #print len(x[0]),
                bag.append(x[0])
            # print len(bag[0]), len(bag)
            self.data.append(bag)
            # print bag
            self.bag_labels.append(self.labels[pair])
            self.bag_pairs.append(pair)


    def train(self):
        self.generate_vectorizer()
        # self.vectorizer = pickle.load("{}/{}/{}_bow.pkl".format(self.basedir, self.modelname, self.modelname))
        self.vectorize_text()
        # print self.vectorizer
        # sys.exit()
        logging.info("Training with {} bags".format(str(len(self.labels))))
        # for i, d in enumerate(self.data):
        #     if self.bag_labels[i] == 1:
        #         print self.bag_pairs[i], len(d), self.bag_labels[i]
        #         for pair in self.pairs[self.bag_pairs[i]]:
        #             print self.corpus.get_sentence(pair[0].sid).text
        #         print

        gc.collect()
        self.classifier.fit(self.data, self.bag_labels)
        gc.collect()
        if not os.path.exists(self.basedir + self.modelname):
            os.makedirs(self.basedir + self.modelname)
        logging.info("Training complete, saving to {}/{}/{}.pkl".format(self.basedir, self.modelname, self.modelname))
        #joblib.dump(self.classifier, "{}/{}/{}.pkl".format(self.basedir, self.modelname, self.modelname))
        #joblib.dump(self.vectorizer, "{}/{}/{}_bow.pkl".format(self.basedir, self.modelname, self.modelname))
        s = pickle.dumps(self.classifier)
        with open("{}/{}/{}.pkl".format(self.basedir, self.modelname, self.modelname), 'w') as modelfile:
            modelfile.write(s)
        s = pickle.dumps(self.vectorizer)
        with open("{}/{}/{}_bow.pkl".format(self.basedir, self.modelname, self.modelname), 'w') as modelfile:
            modelfile.write(s)

    def test(self):
        self.vectorize_text()
        # print self.data
        self.predicted = self.classifier.predict(self.data)
        #self.predicted = [1]*len(self.data)
        print Counter([round(x, 1) for x in self.predicted])

    def annotate_sentences(self, sentences):
        """
        Generate self.data for a list of sentences and then self.test and return list of results for each sentence
        :param sentences: list of sentence objects
        :return:
        """
        for sentence in sentences:
            self.generate_sentence_data(sentence)
            # print "len pairs", self.pairs
        self.test()

    def generate_sentence_data(self, sentence, test=True):
        pairtypes = (config.relation_types[self.pairtype]["source_types"], config.relation_types[self.pairtype]["target_types"])
        sentence_entities = []
        if self.ner_model == "all":
            offsets = set()
            for elist in sentence.entities.elist:
                for entity in sentence.entities.elist[elist]:
                    offset = (entity.dstart, entity.dend)
                    if offset not in offsets:
                        sentence_entities.append(entity)
                        offsets.add(offset)
        else:
            sentence_entities = [entity for entity in sentence.entities.elist[self.ner_model]]
        # print self.ner_model, sentence_entities
        for pair in itertools.permutations(sentence_entities, 2):

            if pair[0].type in pairtypes[0] and pair[1].type in pairtypes[1]: # and pair[0].normalized_score > 0 and pair[1].normalized_score > 0:
                #if test:
                #    bag = (sentence.did, pair[0].normalized, pair[1].normalized)
                #else:
                #    bag = (pair[0].normalized, pair[1].normalized)
                bag = (pair[0].normalized, pair[1].normalized)
                # print bag
                if bag not in self.instances:
                    # print "creating bag", bag
                    self.instances[bag] = []
                    self.labels[bag] = -1  # assume no relation until it's confirmed
                    self.pairs[bag] = []
                # print "adding pair", pair
                self.pairs[bag].append(pair)
                # if bag[1:] in relations:
                # print pair[0].normalized, pair[1].normalized
                if (pair[0].normalized, pair[1].normalized) in self.relations:
                    self.labels[bag] = 1
                    trueddi = 1
                    #truepcount += 1
                    #strue += 1
                #else:
                #    sfalse += 1
                #pcount += 1
                pair_features = self.get_pair_features(sentence, pair)
                if sentence.text.startswith("These abnormalities reflect"):
                    print bag, pair_features.encode("utf8")
                self.instances[bag].append(pair_features)

    def process_sentence(self, sentence):
        """
        return list of relations using sMIL results
        :param sentence:
        :return:
        """
        processed_pairs = []
        for i, pred in enumerate(self.predicted):
            if pred >= 0:
                score = 1.0 / (1.0 + math.exp(-pred))
                bag = self.bag_pairs[i]
                pairs = self.pairs[bag]
                for pair in pairs:
                    # print pair, sentence
                    if pair[0].sid == sentence.sid:
                        pair = sentence.add_relation(pair[0], pair[1], self.pairtype, relation=True)
                        processed_pairs.append(pair)
        return processed_pairs



    def get_predictions(self, corpus):
        results = ResultsRE(self.resultsfile)
        for i, pred in enumerate(self.predicted):
            if pred >= 0:
                score = 1.0 / (1.0 + math.exp(-pred))
                bag = self.bag_pairs[i]
                pairs = self.pairs[bag]
                for pair in pairs:
                    #did = bag[0]
                    did = pair[0].did
                    if did not in results.document_pairs:
                        results.document_pairs[did] = Pairs()
                    new_pair = corpus.documents[did].add_relation(pair[0], pair[1], self.pairtype,
                                                              relation=True)
                    results.document_pairs[did].add_pair(new_pair, "mil")
                    pid = did + ".p" + str(len(results.pairs))
                    results.pairs[pid] = new_pair
                    results.pairs[pid].recognized_by["mil"] = score
        results.corpus = corpus
        return results


    def get_pair_features(self, sentence, pair):
        start1, end1, start2, end2 = pair[0].tokens[0].order, pair[0].tokens[-1].order,\
                                     pair[1].tokens[0].order, pair[1].tokens[-1].order
        sentence_entities_tokens = []
        for ner_model in sentence.entities.elist:
            if ner_model == self.ner_model or self.ner_model == "all":
                for e in sentence.entities.elist[ner_model]:
                    for t in e.tokens:
                        sentence_entities_tokens.append(t.order)
        token_order1 = [t.order for t in pair[0].tokens]
        token_order2 = [t.order for t in pair[1].tokens]
        order = "normal-order"
        entitytext = [pair[0].text, pair[1].text]
        if start1 > start2:
            order = "reverse-order"
            #start, end = pair[1].tokens[-1].order, pair[0].tokens[0].order
            start1, end2, start2, end2 = start2, end2, start1, end1
            entitytext = [pair[1].text, pair[0].text]
        before_features = []
        middle_features = []
        end_features = []
        feature_window = 5
        for i, t in enumerate(sentence.tokens[max(start1-feature_window, 0):start1]):
            if t.order in sentence_entities_tokens:
                before_features.append(str(i) + "-before-entity")
            else:
                before_features.append(str(i) + "-before-" + t.lemma + "-" + t.pos + "-" + t.tag)
                #before_features.append("before-" + t.pos)

        for i, t in enumerate(sentence.tokens[end1:max(end1+feature_window, start2)]):
            if t.order in sentence_entities_tokens:
                middle_features.append(str(i) + "-middle-entity")
            else:
                middle_features.append(str(i) + "-middle-" + t.lemma  + "-" + t.pos + "-" + t.tag)
                #middle_features.append("middle-" + t.pos)

        for i, t in enumerate(sentence.tokens[end2:end2+feature_window]):
            if t.order in sentence_entities_tokens:
                end_features.append(str(i) + "-end-entity")
            else:
                end_features.append(str(i) + "-end-" + t.lemma  + "-" + t.pos + "-" + t.tag)
                #end_features.append("end-" + t.pos)
        features = before_features + middle_features + end_features + [order]
        # try:
        #     tree = Tree.fromstring(sentence.parsetree)
        #
        #
        #     # if "candidate1" in sentence.parsetree:
        #     #    logging.info(sentence1.parsetree)
        #     tree = self.mask_entity(sentence, tree, pair[0], "candidate1")
        #     tree = self.mask_entity(sentence, tree, pair[1], "candidate2")
        #     # if tree[0] != '(':
        #     #     tree = '(S (' + tree + ' NN))'
        #     # this depends on the version of nlkt
        #
        #     tree, found = self.get_path(tree)
        #     tree = tree.replace(" ", "")
        #     print tree
        # except ValueError:
        #     tree = ""
        # features.append(tree)
        return " ".join(features)

    def get_path(self, tree, found=0):
        final_tree = ""
        if tree == "candidate1" or tree == "candidate2":
            found += 1
        try:
            tree.label()
        except AttributeError:
            # print "tree:", tree[:5]

            #    print "no label:", dir(tree), tree
            return final_tree + tree + " ", found
        else:
            # Now we know that t.node is defined

            final_tree += '(' + tree.label() + " "
            for child in tree:
                if found < 2:
                    # print "next level:", tree.label()
                    partial_tree, found = self.get_path(child, found)
                    final_tree += partial_tree
                else:
                    break
            final_tree += ')'
        return final_tree, found

    def mask_entity(self, sentence, tree, entity, label):
        """
        Mask the entity names with a label
        :param sentence: sentence object
        :param tree: tree containing the entity
        :param entity: entity object
        :param label: string to replace the original text
        :return: masked tree
        """
        last_text = ""
        match_text = entity.tokens[0].text
        found = False
        entity_token_index = entity.tokens[0].order
        leaves_pos = tree.treepositions('leaves')
        # logging.info("replace {} with {}".format(match_text, label))
        if entity_token_index == 0:  # if the entity is the first in the sentence, it's easy
            tree[leaves_pos[0]] = label
            return tree
        if entity_token_index > 0:  # otherwise we have to search because the tokenization may be different
            ref_token = sentence.tokens[entity_token_index - 1].text
            # logging.info("replace {}|({}) with {}".format(ref_token, match_text, label))
            # ref_token is used to prevent from matching with the same text but corresponding to a different entity
            # in this case, it is the previous token
            for pos in leaves_pos:
                # exact match case
                if tree[pos] == match_text and (last_text in ref_token or ref_token in last_text):
                    tree[pos] = label
                    return tree
                # partial match - cover tokenization issues
                elif (tree[pos] in match_text or match_text in tree[pos]) and (
                            ref_token in tree[pos] or ref_token in last_text or last_text in ref_token):
                    tree[pos] = label
                    return tree
                last_text = tree[pos]
        # if it was no found, use the next token as reference
        if entity_token_index < sentence.tokens[-1].order and not found:
            for ipos, pos in enumerate(leaves_pos[:-1]):
                ref_token = sentence.tokens[entity_token_index + 1].text
                # logging.info("replace ({})|{} with {}".format(match_text, ref_token, label))
                next_pos = leaves_pos[ipos + 1]
                next_text = tree[next_pos]
                if tree[pos] == match_text and (next_text in ref_token or ref_token in next_text):
                    tree[pos] = label
                    return tree
                elif (tree[pos] in match_text or match_text in tree[pos]) and (
                            ref_token in tree[pos] or ref_token in next_text or next_text in ref_token):
                    tree[pos] = label
                    return tree

        logging.debug("entity not found: |{}|{}|{}|{} in |{}|".format(entity_token_index, ref_token, match_text, label,
                                                                      str(tree)))
        return tree
