import codecs
import logging
import unicodedata
from classification.model import Model
from text.chemical_entity import element_base, ChemdnerAnnotation
from text.chemical_entity import amino_acids
from text.mirna_entity import MirnaEntity
from text.protein_entity import ProteinEntity

feature_extractors = {# "text": lambda x, i: x.tokens[i].text,
                      "prefix3": lambda x, i: x.tokens[i].text[:3],
                      "prevprefix3": lambda x, i: prev_prefix(x, i, 3),
                      "nextprefix3": lambda x, i: next_prefix(x, i, 3),
                      "suffix3": lambda x, i: x.tokens[i].text[-3:],
                      "prevsuffix3": lambda x, i: prev_suffix(x, i, 3),
                      "nextsuffix3": lambda x, i: next_suffix(x, i, 3),
                      "prefix2": lambda x, i: x.tokens[i].text[:2],
                      "suffix2": lambda x, i: x.tokens[i].text[-2:],
                      "prefix4": lambda x, i: x.tokens[i].text[:4],
                      "suffix4": lambda x, i: x.tokens[i].text[-4:],
                      "hasnumber": lambda x, i: str(any(c.isdigit() for c in x.tokens[i].text)),
                      "case": lambda x, i: word_case(x.tokens[i].text),
                      "prevcase": lambda x, i: prev_case(x, i),
                      "nextcase": lambda x, i: next_case(x, i),
                      "lemma": lambda x, i: x.tokens[i].lemma,
                      "prevlemma": lambda x, i: prev_lemma(x,i),
                      "nextlemma": lambda x, i: next_lemma(x,i),
                      "postag": lambda x, i: x.tokens[i].pos,
                      "prevpostag": lambda x, i: prev_pos(x,i),
                      "nextpostag": lambda x, i: next_pos(x,i),
                      "wordclass": lambda x, i: wordclass(x.tokens[i].text),
                      "prevwordclass": lambda x, i: prev_wordclass(x, i),
                      "nextwordclass": lambda x, i: next_wordclass(x, i),
                      "simplewordclass": lambda x, i: simplewordclass(x.tokens[i].text),
                      # "greek": lambda x, i: str(has_greek_symbol(x.tokens[i].text)),
                      # "aminoacid": lambda x, i: str(any(w in amino_acids for w in x.tokens[i].text.split('-'))),
                      # "periodictable": lambda x, i: str(x.tokens[i].text in element_base.keys() or x.tokens[i].text.title() in zip(*element_base.values())[0]), # this should probably be its own function ffs
                      }

def word_in_dictionary(word, dictionary):
    pass

def prev_wordclass(sentence, i):
    if i == 0:
        return "BOS"
    else:
        return wordclass(sentence.tokens[i-1].text)

def next_wordclass(sentence, i):
    if i == len(sentence.tokens) - 1:
        return "EOS"
    else:
        return wordclass(sentence.tokens[i+1].text)

def prev_suffix(sentence, i, size):
    if i == 0:
        return "BOS"
    else:
        return sentence.tokens[i-1].text[-size:]

def next_suffix(sentence, i, size):
    if i == len(sentence.tokens) - 1:
        return "EOS"
    else:
        return sentence.tokens[i+1].text[-size:]

def prev_prefix(sentence, i, size):
    if i == 0:
        return "BOS"
    else:
        return sentence.tokens[i-1].text[:size]

def next_prefix(sentence, i, size):
    if i == len(sentence.tokens) - 1:
        return "EOS"
    else:
        return sentence.tokens[i+1].text[:size]

def prev_case(sentence, i):
    if i == 0:
        return "BOS"
    else:
        return word_case(sentence.tokens[i-1].text)

def next_case(sentence, i):
    if i == len(sentence.tokens) - 1:
        return "EOS"
    else:
        return word_case(sentence.tokens[i+1].text)

def prev_lemma(sentence, i):
    if i == 0:
        return "BOS"
    else:
        return sentence.tokens[i-1].lemma

def next_lemma(sentence, i):
    if i == len(sentence.tokens) - 1:
        return "EOS"
    else:
        return sentence.tokens[i+1].lemma

def prev_pos(sentence, i):
    if i == 0:
        return "BOS"
    else:
        return sentence.tokens[i-1].pos

def next_pos(sentence, i):
    if i == len(sentence.tokens) - 1:
        return "EOS"
    else:
        return sentence.tokens[i+1].pos

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
                            if subtype == "all":
                                tokenlabel = sentence.tokens[i].tags.get("goldstandard", "other")
                            else:
                                tokenlabel = sentence.tokens[i].tags.get("goldstandard_" + subtype, "other")
                        else:
                            tokenfeatures, tokenlabel = self.generate_features(sentence, i, flist, subtype)
                            savecorpus = True
                            sentence.tokens[i].features[fname] = tokenfeatures[:]
                        # if tokenlabel != "other":
                        #      logging.debug("%s %s" % (tokenfeatures, tokenlabel))
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
        logging.info("used %s sentences for model %s" % (nsentences, subtype))

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

    def generate_features(self, sentence, i, flist, subtype):
        """
            Features is dictionary mapping of featurename:value.
            Label is the correct label of the token. It is always other if
            the text is not annotated.
        """
        if subtype == "all":
            label = sentence.tokens[i].tags.get("goldstandard", "other")
        else:
            label = sentence.tokens[i].tags.get("goldstandard_" + subtype, "other")
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

    def save_corpus_to_sbilou(self, entity_type="CHEMICAL"):
        """
        Saves the data that was loaded into simple tagger format to a file compatible with Stanford NER
        :param entity_type:
        :return:
        """
        logging.info("saving loaded corpus to Stanford NER format...")
        lines = []
        for isent, sentence in enumerate(self.sids):
            for it, l in enumerate(self.labels[isent]):
                if l == "other":
                    label = "O"
                elif l == "start":
                    label = "B-{}".format(entity_type)
                elif l == "end":
                    label = "E-{}".format(entity_type)
                elif l == "middle":
                    label = "I-{}".format(entity_type)
                elif l == "single":
                    label = "S-{}".format(entity_type)
                #label += "_" + entity_type
                try:
                    lines.append("{0}\t{1}\n".format(self.tokens[isent][it].text, label))
                except UnicodeEncodeError: #fml
                    lines.append(u"{0}\t{1}\n".format(self.tokens[isent][it].text, label))
            lines.append("\n")
        with codecs.open("{}.bilou".format(self.path), "w", "utf-8") as output:
            output.write("".join(lines))
        logging.info("done")


    def create_entity(self, tokens, sid, did, text, score):
        """
        Create a new entity based on the type of model
        :param tokens: list of Tokens
        :param sid: ID of the sentence
        :param did: ID of the document
        :param text: string
        :param score:
        :return: entity
        """
        if "chem" in self.path:
            e = ChemdnerAnnotation(tokens=tokens, sid=sid, did=did, text=text, score=score)
        elif "prot" in self.path:
            e = ProteinEntity(tokens=tokens, sid=sid, did=did, text=text, score=score)
        elif "mirna" in self.path:
            e = MirnaEntity(tokens=tokens, sid=sid, did=did, text=text, score=score)
        return e


class BiasModel(SimpleTaggerModel):
    """Model which cheats by using the gold standard tags"""

    def test(self):
        self.predicted = self.labels
