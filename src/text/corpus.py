from __future__ import division, absolute_import, unicode_literals
import logging
import pickle
import sys


class Corpus(object):
    """
    Base corpus class
    """
    def __init__(self, corpusdir, **kwargs):
        self.path = corpusdir
        self.documents = kwargs.get("documents", {})
        #logging.debug("Created corpus with {} documents".format(len(self.documents)))

    def save(self, *args):
        """Save corpus object to a pickle file"""
        # TODO: compare with previous version and ask if it should rewrite
        logging.info("saving corpus...")
        if not args:
            path = "data/" + self.path.split('/')[-1] + ".pickle"
        else:
            path = args[0]
        pickle.dump(self, open(path, "wb"))
        logging.info("saved corpus to " + path)

    def get_unique_results(self, source, ths, rules):
        allentities = set()
        for d in self.documents:
            doc_entities = self.documents[d].get_unique_results(source, ths, rules)
            allentities.update(doc_entities)
        return allentities

    def write_chemdner_results(self, source, outfile, ths={"chebi":0.0}, rules=[]):
        """
        Produce results to be evaluated with the BioCreative CHEMDNER evaluation script
        :param source: Base model path
        :param outfile: Text Results path to be evaluated
        :param ths: Thresholds
        :param rules: Validation rules
        :return:
        """
        lines = []
        cpdlines = []
        max_entities = 0
        for d in self.documents:
            doclines = self.documents[d].write_chemdner_results(source, outfile, ths, rules)
            lines += doclines
            hast = 0
            hasa = 0
            for l in doclines:
                if l[1].startswith("T"):
                    hast += 1
                elif l[1].startswith("A"):
                    hasa += 1
            # print hast, hasa
            cpdlines.append((d, "T", hast))
            if hast > max_entities:
                max_entities = hast
            cpdlines.append((d, "A", hasa))
            if hasa > max_entities:
                max_entities = hasa
            # print max_entities
        return lines, cpdlines, max_entities

    def find_chemdner_result(self, res):
        """
            Find the tokens that correspond to a given annotation:
            (did, A/T:start:end)
        """
        did = res[0]
        stype, start, end = res[1].split(":")
        start = int(start)
        end = int(end)
        if stype == 'T':
            sentence = self.documents[did].sentences[0]
        else:
            sentence = self.documents[did].find_sentence_containing(start, end)
            if not sentence:
                print "could not find this sentence!", start, end
        tokens = sentence.find_tokens_between(start, end)
        if not tokens:
            print "could not find tokens!", start, end, sentence.sid, ':'.join(res)
            sys.exit()
        entity = sentence.entities.find_entity(start - sentence.offset, end - sentence.offset)
        return tokens, sentence, entity
