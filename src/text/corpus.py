from __future__ import division, absolute_import
import logging
import pickle
import random
import socket
import sys
import os
from subprocess import PIPE, check_output
from subprocess import Popen
import pexpect

from postprocessing import ssm
from bllipparser import RerankingParser
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
                    allentitites[(did, "0", "0", e.lower())] = doc_entities[e]
            elif mode == "re":
                doc_pairs = {}
                # logging.info(self.documents[did].pairs.pairs)
                for p in self.documents[did].pairs.pairs:
                    if source in p.recognized_by:
                        middle_text = self.documents[did].text[p.entities[0].dstart:p.entities[1].dend]
                        doc_pairs[(did, p.entities[0].normalized, p.entities[1].normalized,
                                   p.entities[0].normalized + "=>" + p.entities[1].normalized)] = [middle_text]
                        # doc_pairs[("PMID", p.entities[0].normalized, p.entities[1].normalized,
                        #            p.entities[0].normalized + "=>" + p.entities[1].normalized)] = [middle_text]
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
                if hassource and hassource in sentence.entities.elist:
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

    def load_biomodel(self):
        rrp = RerankingParser.fetch_and_load('GENIA+PubMed', verbose=True)
        for did in self.documents:
            for sentence in self.documents[did].sentences:
                sentence_text = [t.text for t in sentence.tokens]
                #echocall = Popen(["echo", sentence_text] , stdout=PIPE, stderr=PIPE)
                #nc_params = ["nc", "localhost", "4449"]
                #echocall.wait()
                #call = check_output(nc_params , shell=True, stdin=echocall.stdout)

                #res = call.communicate()
                #res = netcat("localhost", 4449, sentence_text)
                #print res.strip()
                #print
                res = rrp.parse(sentence_text)
                if len(res) > 0:
                    print res[0].ptb_parse
                    print sentence.parsetree
                    print
                    #print
                    sentence.bio_parse = str(res[0].ptb_parse)
                else:
                    print sentence_text
                    print "no parse"
                    sentence.bio_parse = sentence.parsetree
                    print

    def run_ss_analysis(self, pairtype):
        correct_count = 0  # numver of real miRNA-gene pairs with common gos
        incorrect_count = 0  # number of random miRNA-gene pairs with common go
        all_tfs = []
        all_mirnas = []
        diff_count = []
        nexp = 10
        for did in self.documents:
            #for sentence in self.documents[did].sentences:
            all_tfs = []
            all_mirnas = []
            correct_count = 0  # numver of real miRNA-gene pairs with common gos
            incorrect_count = 0  # number of random miRNA-gene pairs with common go
            all_mirnas = self.documents[did].get_entities('goldstandard_mirna')
            all_tfs = self.documents[did].get_entities('goldstandard_protein')
            #count true relations
            if len(all_mirnas) > 0 and len(all_tfs) > 0:
                # for entity in sentence.entities.elist["goldstandard"]:
                #     if entity.type == "protein":
                #         all_tfs.append(entity)
                #     elif entity.type == "mirna":
                #         all_mirnas.append(entity)

                    #     correct_count += 1
                #if len(all_tfs) > 1 and len(all_mirnas) > 1:
                    # print sentence.sid
                correct = 0
                incorrect = 0
                while correct < nexp and incorrect < nexp:
                    random_tf = random.choice(all_tfs)
                    random_mirna = random.choice(all_mirnas)
                    # print dir(random_mirna)
                    # common_gos = set(random_tf.go_ids).intersection(set(random_mirna.go_ids))
                    if correct < nexp and (random_tf.eid, pairtype) in random_mirna.targets:
                        # if len(common_gos) > 0:
                        # if random_mirna.best_go.startswith("GO:") and random_tf.best_go.startswith("GO"):
                        # print random_mirna.best_go, random_tf.best_go
                        max_ss = []
                        for mirnago in random_mirna.go_ids:
                            for mirnatf in random_tf.go_ids:
                                ss = ssm.simui_go(mirnago, mirnatf)
                                max_ss.append(ss)
                                #if max_ss > ss:
                                #    max_ss = ss
                                    # ss = ssm.simui_go(random_mirna.best_go, random_tf.best_go)
                                    # print "correct:", ss
                        if len(max_ss) > 0:
                            correct_count += sum(max_ss)*1.0/len(max_ss)
                        # correct_count += len(common_gos)
                        correct += 1
                    elif incorrect < nexp:
                        # if len(common_gos) > 0:
                        # if random_mirna.best_go.startswith("GO:") and random_tf.best_go.startswith("GO"):
                        max_ss = []
                        for mirnago in random_mirna.go_ids:
                            for mirnatf in random_tf.go_ids:
                                # ss = ssm.simui_hindex_go(mirnago, mirnatf, h=0)
                                ss = ssm.simui_go(mirnago, mirnatf)
                                max_ss.append(ss)
                                #if max_ss > ss:
                                #    max_ss = ss
                                    # ss = ssm.simui_go(random_mirna.best_go, random_tf.best_go)
                                    # print "correct:", ss
                        if len(max_ss) > 0:
                            incorrect_count += sum(max_ss)*1.0/len(max_ss)
                        # incorrect_count += len(common_gos)
                        incorrect += 1
                if correct_count != 0 and incorrect_count != 0:
                    print "{}={}-{} ({} mirnas, {} tfs)".format(correct_count / nexp - incorrect_count / nexp,
                                                                correct_count / nexp, incorrect_count / nexp,
                                                                len(all_mirnas), len(all_tfs))
                    diff_count.append(correct_count / nexp - incorrect_count / nexp)

        print sum(diff_count) * 1.0 / len(diff_count)


def netcat(hostname, port, content):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostname, port))
    s.sendall(content)
    s.shutdown(socket.SHUT_WR)
    output = ""
    while 1:
        data = s.recv(1024)
        if data == "":
            break
        #print "Received:", repr(data)
        output += data
    #print "Connection closed."
    # res = repr(data)
    s.close()
    return output
