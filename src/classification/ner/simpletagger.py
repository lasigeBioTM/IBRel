import logging
import unicodedata
from classification.model import Model
from postprocessing.chebi_resolution import element_base
from postprocessing.chebi_resolution import amino_acids

feature_extractors = {# "text": lambda x, i: x.tokens[i].text,
                      "prefix3": lambda x, i: x.tokens[i].text[:3],
                      "suffix3": lambda x, i: x.tokens[i].text[-3:],
                      "prefix2": lambda x, i: x.tokens[i].text[:2],
                      "suffix2": lambda x, i: x.tokens[i].text[-2:],
                      "hasnumber": lambda x, i: str(any(c.isdigit() for c in x.tokens[i].text)),
                      "case": lambda x, i: word_case(x.tokens[i].text),
                      # "stem": lambda x, i: x.tokens[i].stem,
                      "postag": lambda x, i: x.tokens[i].pos,
                      "wordclass": lambda x, i: wordclass(x.tokens[i].text),
                      "simplewordclass": lambda x, i: simplewordclass(x.tokens[i].text),
                      "greek": lambda x, i: str(has_greek_symbol(x.tokens[i].text)),
                      "aminoacid": lambda x, i: str(any(w in amino_acids for w in x.tokens[i].text.split('-'))),
                      "periodictable": lambda x, i: str(x.tokens[i].text in element_base.keys() or x.tokens[i].text.title() in zip(*element_base.values())[0]), # this should probably be its own function ffs
                      }


def word_case(word):
    if word.islower():
        case = 'LOWERCASE'
    elif word.isupper():
        case = 'UPPERCASE'
    elif word.istitle():
        case = 'TITLECASE'
    else:
        case = 'MIXEDCASE'
    return case


def has_greek_symbol(word):
    for c in word:
        #print c
        try:
            if 'GREEK' in unicodedata.name(c):
                hasgreek = 'HASGREEK'
                return True
        except ValueError:
            return False
    return False


def get_prefix_suffix(word, n):
    #print len(word.decode('utf-8'))
    #if len(word.decode('utf-8')) <= n:
    if len(word) <= n:
        #print "111111"
        #word2 = word.encode('utf-8')
        return word, word
    else:
        #print "22222"
        #return word.decode('utf-8')[:n].encode('utf-8'), word.decode('utf-8')[-n:].encode('utf-8')
        return word[:n], word[-n:]


def wordclass(word):
    wclass = ''
    for c in word:
        if c.isdigit():
            wclass += '0'
        elif c.islower():
            wclass += 'a'
        elif c.isupper():
            wclass += 'A'
        else:
            wclass += 'x'
    return wclass


def simplewordclass(word):
    wclass = '.'
    for c in word:
        if c.isdigit() and wclass[-1] != '0':
            wclass += '0'
        elif c.islower() and wclass[-1] != 'a':
            wclass += 'a'
        elif c.isupper() and wclass[-1] != 'A':
            wclass += 'A'
        elif not c.isdigit() and not c.islower() and not c.isupper() and wclass[-1] != 'x':
            wclass += 'x'
    return wclass[1:]


class SimpleTaggerModel(Model):
    """Model trained with a tagger"""
    def __init__(self, path, **kwargs):
        super(SimpleTaggerModel, self).__init__(path, **kwargs)
        self.sids = []
        self.tagger = None
        self.trainer = None
        self.sentences = []

    def load_data(self, corpus, flist, subtype="all", mode="train"):
        """
            Load the data from the corpus to the format required by crfsuite.
            Generate the following variables:
                - self.data = list of features for each token for each sentence
                - self.labels = list of labels for each token for each sentence
                - self.sids = list of sentence IDs
                - self.tokens = list of tokens for each sentence
        """
        logging.info("Loading data for subtype %s" % subtype)
        fname = "f" + str(len(flist))
        nsentences = 0
        didx = 0
        savecorpus = False # do not save the corpus if no new features are generated
        for did in corpus.documents:
            logging.debug("processing doc %s/%s" % (didx, len(corpus.documents)))
            for si, sentence in enumerate(corpus.documents[did].sentences):
                # skip if no entities in this sentence
                if mode == "train" and "goldstandard" not in sentence.entities.elist:
                    logging.debug("Skipped sentence without entities")
                    continue
                sentencefeatures = []
                sentencelabels = []
                sentencetokens = []
                sentencesubtypes = []
                for i in range(len(sentence.tokens)):
                    if sentence.tokens[i].text:
                        tokensubtype = sentence.tokens[i].tags.get("goldstandard_subtype", "none")
                        if fname in sentence.tokens[i].features:
                            tokenfeatures = sentence.tokens[i].features[fname]
                            #logging.info("loaded features from corpus: %s" % tokenfeatures)
                            tokenlabel = sentence.tokens[i].tags.get("goldstandard", "other")
                        else:
                            tokenfeatures, tokenlabel = self.generate_features(sentence, i, flist)
                            savecorpus = True
                            sentence.tokens[i].features[fname] = tokenfeatures[:]
                        if tokenlabel != "other":
                             logging.debug("%s %s" % (tokenfeatures, tokenlabel))
                        sentencefeatures.append(tokenfeatures)
                        sentencelabels.append(tokenlabel)
                        sentencetokens.append(sentence.tokens[i])
                        sentencesubtypes.append(tokensubtype)
                #logging.info("%s" % set(sentencesubtypes))
                #if subtype == "all" or subtype in sentencesubtypes:
                #logging.debug(sentencesubtypes)
                nsentences += 1
                self.data.append(sentencefeatures)
                self.labels.append(sentencelabels)
                self.sids.append(sentence.sid)
                self.tokens.append(sentencetokens)
                self.subtypes.append(set(sentencesubtypes))
                self.sentences.append(sentence.text)
            didx += 1
        # save data back to corpus to improve performance
        #if subtype == "all" and savecorpus:
        #    corpus.save()
        logging.info("used %s for model %s" % (nsentences, subtype))

    def copy_data(self, basemodel, t="all"):
        #logging.debug(self.subtypes)
        if t != "all":
            right_sents = [i for i in range(len(self.subtypes)) if t in self.subtypes[i]]
            #logging.debug(right_sents)
            self.data = [basemodel.data[i] for i in range(len(basemodel.subtypes)) if i in right_sents]
            self.labels = [basemodel.labels[i] for i in range(len(basemodel.subtypes)) if i in right_sents]
            self.sids = [basemodel.sids[i] for i in range(len(basemodel.subtypes)) if i in right_sents]
            self.tokens =  [basemodel.tokens[i] for i in range(len(basemodel.subtypes)) if i in right_sents]
            self.sentences = [basemodel.sentences[i] for i in range(len(basemodel.subtypes)) if i in right_sents]
        else:
            self.data = basemodel.data[:]
            self.labels = basemodel.labels[:]
            self.sids = basemodel.sids
            self.tokens = basemodel.tokens[:]
            self.sentences = basemodel.sentences[:]
        logging.info("copied %s for model %s" % (len(self.data), t))

    def generate_features(self, sentence, i, flist):
        """
            Features is dictionary mapping of featurename:value.
            Label is the correct label of the token. It is always other if
            the text is not annotated.
        """
        label = sentence.tokens[i].tags.get("goldstandard", "other")
        features = []
        for f in flist:
            if f not in sentence.tokens[i].features:
                fvalue = feature_extractors[f](sentence, i)
                sentence.tokens[i].features[f] = fvalue
            else:
                fvalue = sentence.tokens[i].features[f]
            features.append(f + "=" + fvalue)
        # if label != "other":
        #     logging.debug("{} {}".format(sentence.tokens[i], label))
        #logging.debug(features)
        return features, label


class BiasModel(SimpleTaggerModel):
    """Model which cheats by using the gold standard tags"""

    def test(self):
        self.predicted = self.labels
