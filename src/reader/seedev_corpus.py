import argparse
import codecs
import logging
import pickle
import xml.etree.ElementTree as ET
import os
import sys
import pprint
import itertools
from nltk.corpus import stopwords
import nltk
import numpy as np
import progressbar as pb
import time

from pycorenlp import StanfordCoreNLP
from sklearn import metrics, svm, feature_selection
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from config.seedev_types import ds_pair_types, all_entity_groups, all_entity_types, pair_types
from config import config
from text.corpus import Corpus
from text.document import Document
from text.sentence import Sentence

pp = pprint.PrettyPrinter(indent=4)
text_clf = Pipeline([('vect', CountVectorizer(analyzer='char_wb', ngram_range=(7,20), min_df=0.2, max_df=0.5)),
                             #('vect', CountVectorizer(analyzer='word', ngram_range=(1,5), stop_words="english", min_df=0.1)),
                             #     ('tfidf', TfidfTransformer(use_idf=True, norm="l2")),
                                  #('tfidf', TfidfVectorizer(analyzer='char_wb', ngram_range=(6,20))),
                                  #('clf', SGDClassifier(loss='hinge', penalty='l1', alpha=0.01, n_iter=5, random_state=42)),
                                  #('clf', SGDClassifier())
                                  #('clf', svm.SVC(kernel='rbf', C=10, verbose=True, tol=1e-5))
                                  #('clf', RandomForestClassifier(n_estimators=10))
                                    #('feature_selection', feature_selection.SelectFromModel(LinearSVC(penalty="l1"))),
                                  ('clf', MultinomialNB(alpha=0.1, fit_prior=False))
                                  #('clf', DummyClassifier(strategy="constant", constant=True))
                                 ])
class SeeDevCorpus(Corpus):
    """
    Corpus for the BioNLP SeeDev task
    self.path is the base directory of the files of this corpus.
    """
    def __init__(self, corpusdir, **kwargs):
        super(SeeDevCorpus, self).__init__(corpusdir, **kwargs)
        self.subtypes = []
        self.train_sentences = [] # sentences used for training the sentence classifier
        self.type_sentences = {} # sentences classified as true for each type

    def load_corpus(self, corenlpserver, process=True):
        # self.path is the base directory of the files of this corpus
        trainfiles = [self.path + '/' + f for f in os.listdir(self.path) if f.endswith('.txt')]
        total = len(trainfiles)
        widgets = [pb.Percentage(), ' ', pb.Bar(), ' ', pb.AdaptiveETA(), ' ', pb.Timer()]
        pbar = pb.ProgressBar(widgets=widgets, maxval=total, redirect_stdout=True).start()
        time_per_abs = []
        for current, f in enumerate(trainfiles):
            #logging.debug('%s:%s/%s', f, current + 1, total)
            print '{}:{}/{}'.format(f, current + 1, total)
            did = f.split(".")[0].split("/")[-1]
            t = time.time()
            with codecs.open(f, 'r', 'utf-8') as txt:
                doctext = txt.read()
            doctext = doctext.replace("\n", " ")
            newdoc = Document(doctext, process=False, did=did)
            newdoc.sentence_tokenize("biomedical")
            if process:
                newdoc.process_document(corenlpserver, "biomedical")
            self.documents[newdoc.did] = newdoc
            abs_time = time.time() - t
            time_per_abs.append(abs_time)
            #logging.info("%s sentences, %ss processing time" % (len(newdoc.sentences), abs_time))
            pbar.update(current+1)
        pbar.finish()
        abs_avg = sum(time_per_abs)*1.0/len(time_per_abs)
        logging.info("average time per abstract: %ss" % abs_avg)

    def load_annotations(self, ann_dir, etype, pairtype="all"):
        self.clear_annotations("all")
        for rtype in all_entity_types:
            self.clear_annotations(rtype)
        annfiles = [ann_dir + '/' + f for f in os.listdir(ann_dir) if f.endswith('.a1')]
        total = len(annfiles)
        time_per_abs = []
        originalid_to_eid = {}
        for current, f in enumerate(annfiles):
            logging.debug('%s:%s/%s', f, current + 1, total)
            did = f.split(".")[0].split("/")[-1]
            with codecs.open(f, 'r', 'utf-8') as txt:
                for line in txt:
                    # print line
                    tid, ann, etext = line.strip().split("\t")
                    if ";" in ann:
                        # print "multiple offsets:", ann
                        # ann = ann.split(";")[0] # ignore the second part for now
                        ann_elements = ann.split(" ")
                        entity_type, dstart, dend = ann_elements[0], int(ann_elements[1]), int(ann_elements[-1])
                        dexclude = [e.split(";") for e in ann_elements[2:-1]]
                        dexclude = [(int(dex[0]), int(dex[1])) for dex in dexclude]
                        # print ann, dstart, dend
                    else:
                        entity_type, dstart, dend = ann.split(" ")
                        dexclude = None
                        dstart, dend = int(dstart), int(dend)
                    # load all entities
                    #if etype == "all" or (etype != "all" and etype == type_match[entity_type]):

                    sentence = self.documents[did].find_sentence_containing(dstart, dend, chemdner=False)
                    if sentence is not None:
                        # e[0] and e[1] are relative to the document, so subtract sentence offset
                        start = dstart - sentence.offset
                        end = dend - sentence.offset
                        if dexclude is not None:
                            exclude = [(dex[0] - sentence.offset, dex[1] - sentence.offset) for dex in dexclude]
                        else:
                            exclude = None
                        eid = sentence.tag_entity(start, end, entity_type, text=etext, original_id=tid, exclude=exclude)
                        if eid is None:
                            print "no eid!", sentence.sid, start, end, exclude, etext, sentence.text
                            continue
                            # sys.exit()
                        originalid_to_eid[did + "." + tid] = eid
                    else:
                        print "{}: could not find sentence for this span: {}-{}|{}".format(did, dstart, dend, etext.encode("utf-8"))
                        print
                        #sys.exit()
        self.load_relations(ann_dir, originalid_to_eid)

    def load_relations(self, ann_dir, originalid_to_eid):
        print "loading relations..."
        relations_stats = {}
        annfiles = [ann_dir + '/' + f for f in os.listdir(ann_dir) if f.endswith('.a2')]
        total = len(annfiles)
        time_per_abs = []
        default_stopwords = set(nltk.corpus.stopwords.words('english'))
        custom_stopwords = set(('-', '.', ',', '-lrb-', '-rrb-', 'et', 'al', ';', ':', '/'))

        all_stopwords = default_stopwords | custom_stopwords
        unique_relations = set()
        reltype_texts = {}
        for current, f in enumerate(annfiles):
            logging.debug('%s:%s/%s', f, current + 1, total)
            did = f.split(".")[0].split("/")[-1]
            with codecs.open(f, 'r', 'utf-8') as txt:
                for line in txt:
                    eid, ann = line.strip().split("\t")
                    rtype, sourceid, targetid = ann.split(" ")
                    if rtype not in relations_stats:
                        relations_stats[rtype] = {"count": 0}
                    relations_stats[rtype]["count"] += 1
                    sourceid = did + "." + sourceid.split(":")[-1]
                    targetid = did + "." + targetid.split(":")[-1]
                    if sourceid not in originalid_to_eid or targetid not in originalid_to_eid:
                        print "{}: entity not found: {}=>{}".format(did, sourceid, targetid)
                        # print sorted([e.split(".")[-1] for e in originalid_to_eid if e.startswith(did)])
                        print "skipped relation {}".format(rtype)
                        continue
                    sourceid, targetid = originalid_to_eid[sourceid], originalid_to_eid[targetid]
                    sid1 = '.'.join(sourceid.split(".")[:-1])
                    sid2 = '.'.join(targetid.split(".")[:-1])
                    sn1 = int(sid1.split("s")[-1])
                    sn2 = int(sid2.split("s")[-1])
                    # if abs(sn2 - sn1) > 3:
                    #     print "relation {} between entities on distant sentences: {}=>{}".format(rtype, sourceid, targetid)
                    #     continue
                    sentence1 = self.documents[did].get_sentence(sid1)
                    sentence2 = self.documents[did].get_sentence(sid2)
                    if sentence1 is None:
                        print "sentence not found:", did, sid1, sourceid, targetid, len(self.documents[did].sentences)
                        continue
                    else:
                        entity1 = sentence1.entities.get_entity(sourceid)
                        entity2 = sentence2.entities.get_entity(targetid)
                        entity1.targets.append((targetid, rtype))
                        if entity1.type + "_source" not in relations_stats[rtype]:
                            relations_stats[rtype][entity1.type + "_source"] = 0
                        relations_stats[rtype][entity1.type + "_source"] += 1
                        if entity2.type + "_target" not in relations_stats[rtype]:
                            relations_stats[rtype][entity2.type + "_target"] = 0
                        relations_stats[rtype][entity2.type + "_target"] += 1
                        entity1_text = entity1.text.encode("utf-8")
                        entity2_text = entity2.text.encode("utf-8")
                        sentence_text = []
                        entity1_orders = [t.order for t in entity1.tokens]
                        entity2_orders = [t.order for t in entity2.tokens]
                        entity_orders = entity1_orders + entity2_orders
                        entity_orders.sort()
                        # print entity_orders
                        for t in sentence1.tokens:
                            if t.order in entity1_orders and (len(sentence_text) == 0 or sentence_text[-1] != "ARG1"):
                                #sentence_text.append("ARG1-" + entity1.type)
                                continue
                            elif t.order in entity2_orders and  (len(sentence_text) == 0 or sentence_text[-1] != "ARG2"):
                                #sentence_text.append("ARG2-" + entity1.type)
                                continue
                            elif "goldstandard" in t.tags and  (len(sentence_text) == 0 or sentence_text[-1] != "ENTITY"):
                                #sentence_text.append("ENTITY")
                                continue
                            elif t.text.lower() not in all_stopwords and not t.text.istitle() and t.text.isalpha():
                                sentence_text.append(t.text)
                            if rtype not in reltype_texts:
                                reltype_texts[rtype] = []
                            reltype_texts[rtype].append(sentence_text)
                            #print " ".join(sentence_text)
                            #print
                        rel_text = "{}#{}\t{}\t{}#{}".format(entity1.type, entity1_text, rtype, entity2.type, entity2_text)
                        unique_relations.add(rel_text)
                        # if rel_text not in unique_relations:
                        #     unique_relations[rel_text] = set()
                        # print
                        # print "{}-{}={}>{}-{}".format(entity1.type, entity1_text, rtype, entity2.type, entity2_text)
                        # sentence1_text = sentence1.text.encode("utf-8")
                        # sentence1_text = sentence1_text.replace(entity1_text, "|{}|".format(entity1_text))
                        # sentence1_text = sentence1_text.replace(entity2_text, "|{}|".format(entity2_text))
                        # print sentence1_text
                        #if sid1 != sid2:
                        #    sentence2_text = sentence1.text.encode("utf-8").replace(entity2_text, "|{}|".format(entity2_text))
                        #   print sentence2_text
                        # print
                        # print "{}: {}=>{}".format(etype, entity1.text.encode("utf-8"), targetid)
        with codecs.open("seedev_relation.txt", 'w', 'utf-8') as relfile:
            for r in unique_relations:
                relfile.write(r.decode("utf-8") + '\n')
        #pp.pprint(relations_stats)
        alltokens = []
        for rtype in reltype_texts:
            alltokens += list(itertools.chain(*reltype_texts[rtype]))
        alldist = nltk.FreqDist(alltokens)
        allmc = alldist.most_common(150)
        allmc = set([x[0] for x in allmc])
        for rtype in reltype_texts:
            fdist1 = nltk.FreqDist(list(itertools.chain(*reltype_texts[rtype])))
            mc = fdist1.most_common(150)
            mc = set([x[0] for x in mc])
            int_words = mc - allmc
            with codecs.open("seedev_int_words_{}.txt".format(rtype), 'w', 'utf-8') as relfile:
                print
                print rtype
                for i in int_words:
                    relfile.write(i + '\n')
                    print i
            #print rtype, len(int_words), int_words
            #print

    def get_features(self, pairtype):
        f = []
        labels = []
        sids = []
        for sentence in self.get_sentences("goldstandard"):
            hasrel = False
            hassource = False
            hastarget = False
            sids.append(sentence.sid)
            for e in sentence.entities.elist["goldstandard"]:
                if e.type in pair_types[pairtype]["source_types"]:
                    hassource = True
                if e.type in pair_types[pairtype]["target_types"]:
                    hastarget = True
                if any([target[1] == pairtype for target in e.targets]):
                    # print pairtype, sentence.text
                    hasrel = True
                    break
            if not hassource or not hastarget:
                continue
            tokens_text = [t.text for t in sentence.tokens]
            stokens = []
            for it, t in enumerate(sentence.tokens):
                #print tokens_text[:it], tokens_text[it:]
                if "-LRB-" in tokens_text[:it] and "-RRB-" in tokens_text[it:] and "-RRB-" not in tokens_text[:it] and "-LRB-" not in tokens_text[it:]:
                    #if "(" in t.text or ")" in t.text:
                    # print "skipped between ()", t.text
                    continue
                elif t.lemma.isdigit():
                    # print "digit:", t.lemma, t.text
                    continue
                elif t.text == "-LRB-" or t.text == "-RRB-":
                    continue
                elif "goldstandard" in t.tags and (len(stokens) == 0 or stokens[-1] != t.tags["goldstandard_subtype"]):
                    stokens.append(t.tags["goldstandard_subtype"])
                #elif not t.text.isalpha():
                #    print "not alpha:", t.text
                #    continue
                else:
                    stokens.append(t.pos + "-" + t.lemma)
            f.append(" ".join(stokens))
            if hasrel:
                labels.append(True)
            else:
                labels.append(False)
        return f, labels, sids

    def train_sentence_classifier(self, pairtype):
        self.text_clf = Pipeline([('vect', CountVectorizer(analyzer='char_wb', ngram_range=(7,20), min_df=0.2, max_df=0.5)),
                             #('vect', CountVectorizer(analyzer='word', ngram_range=(1,5), stop_words="english", min_df=0.1)),
                             #     ('tfidf', TfidfTransformer(use_idf=True, norm="l2")),
                                  #('tfidf', TfidfVectorizer(analyzer='char_wb', ngram_range=(6,20))),
                                  #('clf', SGDClassifier(loss='hinge', penalty='l1', alpha=0.01, n_iter=5, random_state=42)),
                                  #('clf', SGDClassifier())
                                  #('clf', svm.SVC(kernel='rbf', C=10, verbose=True, tol=1e-5))
                                  #('clf', RandomForestClassifier(n_estimators=10))
                                    #('feature_selection', feature_selection.SelectFromModel(LinearSVC(penalty="l1"))),
                                  ('clf', MultinomialNB(alpha=0.1, fit_prior=False))
                                  #('clf', DummyClassifier(strategy="constant", constant=True))
                                 ])
        f, labels, sids = self.get_features(pairtype)
        half_point = int(len(f)*0.5)
        self.train_sentences = sids[:half_point]
        """ch2 = SelectKBest(chi2, k=20)
        X_train = text_clf.named_steps["vect"].fit_transform(f[:half_point])
        X_test = text_clf.named_steps["vect"].transform(f[half_point:])
        X_train = ch2.fit_transform(X_train, labels[:half_point])
        X_test = ch2.transform(X_test)
        feature_names = text_clf.named_steps["vect"].get_feature_names()
        feature_names = [feature_names[i] for i
                         in ch2.get_support(indices=True)]
        # print feature_names"""
        # train
        text_clf = self.text_clf.fit(f[:half_point], labels[:half_point])

        #save model
        if not os.path.exists("models/kernel_models/" + pairtype + "_sentence_classifier/"):
            os.makedirs("models/kernel_models/" + pairtype + "_sentence_classifier/")
        logging.info("Training complete, saving to {}/{}/{}.pkl".format("models/kernel_models/",
                                                                        pairtype + "_sentence_classifier/", pairtype))
        joblib.dump(text_clf, "{}/{}/{}.pkl".format("models/kernel_models/",
                                                                        pairtype + "_sentence_classifier/", pairtype))

        # evaluate
        pred = text_clf.predict(f[half_point:])
        # print len(pred), sum(pred)
        self.type_sentences[pairtype] = []
        for ip, p in enumerate(pred):
            if p:
                self.type_sentences[pairtype].append(sids[half_point + ip])

        res = metrics.confusion_matrix(labels[half_point:], pred)
        return res[1][1], res[0][1], res[1][0]

    def test_sentence_classifier(self, pairtype):
        text_clf = joblib.load("{}/{}/{}.pkl".format("models/kernel_models/",
                                                                        pairtype + "_sentence_classifier/", pairtype))
        f, labels, sids = self.get_features(pairtype)
        pred = text_clf.predict(f)
        self.type_sentences[pairtype] = []
        for ip, p in enumerate(pred):
            if p:
                self.type_sentences[pairtype].append(sids[ip])
        # print self.type_sentences.keys()
        res = metrics.confusion_matrix(labels, pred)
        return res[1][1], res[0][1], res[1][0]


    def add_more_sentences(self, corpuspath):
        """
        Load sentences with relations from another corpus
        :param corpuspath: corpus path
        :return:
        """
        nsentences = 0
        for did in self.documents:
            nsentences += len(self.documents[did].sentences)
        print "base corpus has {} sentences".format(nsentences)
        corpus2 = pickle.load(open(corpuspath, 'rb'))
        nsentences = 0
        for did in corpus2.documents:
            if did in self.documents:
                print "repeated did:", did
            else:
                self.documents[did] = corpus2.documents[did]
                nsentences += len(corpus2.documents[did].sentences)
            #for sentence in corpus2.documents[did].sentences:
                #if any([len(e.targets)> 1 for e in sentence.entities.elist["goldstandard"]]):
                #    print "found sentence with relations:", sentence.sid
                #if len(sentence.entities.elist["goldstandard"]) > 1:
                #self.documents[sentence.sid] = Document(sentence.text, sentences=[sentence])
        print "added {} sentences".format(nsentences)
        self.save("corpora/Thaliana/seedev-extended.pickle")

    def convert_entities_to_goldstandard(self, basemodel="models/seedev_train_entity"):
        for did in self.documents:
            for sentence in self.documents[did].sentences:
                sentence.entities.elist["goldstandard"] = []
                for source in sentence.entities.elist:
                    if source.startswith(basemodel):
                        # logging.info("adding to goldstandard: {}, {} entities".format(source, len(sentence.entities.elist[source])))
                        sentence.entities.elist["goldstandard"] += sentence.entities.elist[source]

    def find_ds_relations(self):
        rtypes = ds_pair_types
        #del rtypes["Has_Sequence_Identical_To"]
        #del rtypes["Is_Functionally_Equivalent_To"]
        rel_words = get_relwords(rtypes)
        rtypes_count = {}
        for did in self.documents:
            for sentence in self.documents[did].sentences:
                sentence_entities = [entity for entity in sentence.entities.elist["goldstandard"]]
                sentence_words = set([t.text for t in sentence.tokens])
                # logging.debug("sentence {} has {} entities ({})".format(sentence.sid, len(sentence_entities), len(sentence.entities.elist["goldstandard"])))
                for rtype in rtypes:
                    if rtype not in rtypes_count:
                        rtypes_count[rtype] = [0, 0]
                    if len(sentence_words & rel_words[rtype]) > -1 and len(sentence_entities) < 20:
                        pairtypes = (pair_types[rtype]["source_types"], pair_types[rtype]["target_types"])
                        for pair in itertools.permutations(sentence_entities, 2):
                            # print pair[0].type in pairtypes[0], pair[1].type in pairtypes[1]
                            if pair[0].type in pairtypes[0] and pair[1].type in pairtypes[1] and pair[0].text != pair[1].text:

                                    logging.info(u"found relation {0}: {1.text}.{1.type}=>{2.text}.{2.type} because of {3}".
                                                 format(rtype, pair[0], pair[1], str(sentence_words & rel_words[rtype])))
                                    logging.info("context: {}".format(sentence.text.encode("utf-8")))
                                    pair[0].targets.append((pair[1].eid, rtype))

                                    rtypes_count[rtype][0] += 1
                            else:
                                rtypes_count[rtype][1] += 1
        for rtype in rtypes_count:
            print rtype, (1.0*rtypes_count[rtype][0])/(rtypes_count[rtype][0]+rtypes_count[rtype][1]), rtypes_count[rtype][0], rtypes_count[rtype][1]


def get_relwords(rtypes, basedir="seedev_int_words"):
    relwords = {}
    for rtype in rtypes:
        relwords[rtype] = set()
        with open(basedir + "_{}.txt".format(rtype), 'r') as wfile:
            for l in wfile:
                relwords[rtype].add(l.strip())
    return relwords

def get_seedev_gold_ann_set(goldpath, entitytype, pairtype):
    logging.info("loading gold standard annotations... {}".format(goldpath))
    annfiles = [goldpath + '/' + f for f in os.listdir(goldpath) if f.endswith('.a1')]
    gold_offsets = set()
    tid_to_offsets = {}
    for current, f in enumerate(annfiles):
            did = f.split(".")[0].split("/")[-1]
            with codecs.open(f, 'r', "utf-8") as txt:
                for line in txt:
                    tid, ann, etext = line.strip().split("\t")
                    if ";" in ann:
                        # print "multiple offsets:", ann
                        # TODO: use the two parts
                        ann_elements = ann.split(" ")
                        entity_type, dstart, dend = ann_elements[0], int(ann_elements[1]), int(ann_elements[-1])
                    else:
                        etype, dstart, dend = ann.split(" ")
                        dstart, dend = int(dstart), int(dend)
                        if etype == entitytype or entitytype == "all":
                            gold_offsets.add((did, dstart, dend, etext))

                    tid_to_offsets[did + "." + tid] = (dstart, dend, etext)
    gold_relations = set()
    annfiles = [goldpath + '/' + f for f in os.listdir(goldpath) if f.endswith('.a2')]
    for current, f in enumerate(annfiles):
        did = f.split(".")[0].split("/")[-1]
        with open(f, 'r') as txt:
            for line in txt:
                eid, ann = line.strip().split("\t")
                ptype, sourceid, targetid = ann.split(" ")
                if ptype == pairtype or pairtype == "all":
                    sourceid = sourceid.split(":")[-1]
                    targetid = targetid.split(":")[-1]
                    source = tid_to_offsets[did + "." + sourceid]
                    target = tid_to_offsets[did + "." + targetid]
                    gold_relations.add((did, source[:2], target[:2], u"{}={}>{}".format(source[2], ptype, target[2])))
                    #gold_relations.add((did, source[:2], target[:2], u"{}=>{}".format(source[2], target[2])))
    return gold_offsets, gold_relations

