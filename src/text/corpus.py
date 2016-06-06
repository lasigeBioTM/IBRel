from __future__ import division, absolute_import
import logging
import pickle
import sys
import os

import pexpect

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '../..'))



class Corpus(object):
    """
    Base corpus class
    """
    def __init__(self, corpusdir, **kwargs):
        self.path = corpusdir
        self.documents = kwargs.get("documents", {})
        self.invalid_sections = set()
        self.invalid_sids = set()
        #logging.debug("Created corpus with {} documents".format(len(self.documents)))

    def progress(self, count, total, suffix=''):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '=' * filled_len + '-' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))

    def save(self, savedir, *args):
        """Save corpus object to a pickle file"""
        # TODO: compare with previous version and ask if it should rewrite
        logging.info("saving corpus...")
        #if not args:
        #    path = "data/" + self.path.split('/')[-1] + ".pickle"
        #else:
        #    path = args[0]
        pickle.dump(self, open(savedir, "wb"))
        logging.info("saved corpus to " + savedir)

    def get_unique_results(self, source, ths, rules, mode):
        allentitites = {}
        for did in self.documents:
            if mode == "ner":
                doc_entities = self.documents[did].get_unique_results(source, ths, rules, mode)
                for e in doc_entities:
                    allentitites[(self.did, e)] = doc_entities[e]
            elif mode == "re":
                doc_pairs = {}
                # logging.info(len(self.documents[d].pairs.pairs))
                for p in self.documents[did].pairs.pairs:
                    if source in p.recognized_by:
                        doc_pairs[(did, p.entities[0].normalized, p.entities[1].normalized)] = []
                allentitites.update(doc_pairs)
        return allentitites

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

    def get_entity_offsets(self, esource, ths, rules):
        """
        Retrieve the offsets of entities found with the models in source to evaluate
        :param esources:
        :return: List of tuple : (did, start, end, text)
        """
        offsets = {} # {did1: [(0,5), (10,14)], did2: []...}
        for did in self.documents:
            offsets[did] = self.documents[did].get_entity_offsets(esource, ths, rules)
        offsets_list = {}
        for did in offsets:
            for o in offsets[did]:
                offsets_list[(did, o[0], o[1], o[2])] = o[3]
        return offsets_list


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

    def get_all_entities(self, source):
        entities = []
        for d in self.documents:
            for s in self.documents[d].sentences:
                for e in s.entities.elist[source]:
                    entities.append(e)
        return entities

    def clear_annotations(self, entitytype="all"):
        logging.info("Cleaning previous annotations...")
        for pmid in self.documents:
            for s in self.documents[pmid].sentences:
                if "goldstandard" in s.entities.elist:
                    del s.entities.elist["goldstandard"]
                if entitytype != "all" and "goldstandard_" + entitytype in s.entities.elist:
                    del s.entities.elist["goldstandard_" + entitytype]
                for t in s.tokens:
                    if "goldstandard" in t.tags:
                        del t.tags["goldstandard"]
                        del t.tags["goldstandard_subtype"]
                    if entitytype != "all" and "goldstandard_" + entitytype in t.tags:
                        del t.tags["goldstandard_" + entitytype]

    def get_invalid_sentences(self):
        pass

    def evaluate_normalization(self):
        scores = []
        for did in self.documents:
            for s in self.documents[did].sentences:
                if "goldstandard" in s.entities.elist:
                    for e in s.entities.elist.get("goldstandard"):
                        scores.append(e.normalized_score)
        print "score average: {}".format(sum(scores)*1.0/len(scores))
        scores.sort()
        print scores[0], scores[-1]

    def get_sentences(self, hassource=None):
        for did in self.documents:
            for sentence in self.documents[did].sentences:
                if hassource and 'goldstandard' in sentence.entities.elist:
                    yield sentence
                elif hassource is None:
                    yield sentence

    def get_sentence(self, sid):
        for d in self.documents:
            for sentence in self.documents[d].sentences:
                if sentence.sid == sid:
                    return sentence

    def load_genia(self):
        os.chdir("bin/geniatagger-3.0.2/")
        c = pexpect.spawn('./geniatagger')
        c.timeout = 300
        c.expect("loading named_entity_models..done.\r\n")
        os.chdir("..")
        os.chdir("..")
        for did in self.documents:
            for sentence in self.documents[did].sentences:
                c.sendline(" ".join([t.text for t in sentence.tokens]))
                c.expect("\r\n\r\n")
                genia_results = c.before.split("\r\n")[1:]
                if len(genia_results) != len(sentence.tokens):
                    print "error with genia results", len(genia_results), len(sentence.tokens)
                    print " ".join([t.text for t in sentence.tokens])
                    print genia_results
                    for i, t in enumerate(sentence.tokens):
                        # if values[2] != sentence.tokens[i].pos:
                        #    print "pos:", values[0], values[2], sentence.tokens[i].pos
                        sentence.tokens[i].genia_pos = sentence.tokens[i].pos
                        sentence.tokens[i].genia_tag = sentence.tokens[i].tag
                        sentence.tokens[i].genia_chunk = "None"
                else:
                    for i, t in enumerate(genia_results):
                        values = t.split("\t")
                        # if values[2] != sentence.tokens[i].pos:
                        #     print "pos:", values[0], values[2], sentence.tokens[i].pos
                        sentence.tokens[i].genia_pos = values[2]
                        sentence.tokens[i].genia_tag = values[4]
                        sentence.tokens[i].genia_chunk = values[3]

        c.kill(0)



