from __future__ import unicode_literals

import random
import time
import logging
import sys
import os
from xml.etree import ElementTree as ET

import progressbar as pb

from postprocessing import ssm
from text.mirna_entity import mirna_graph
from text.protein_entity import get_uniprot_name

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '../..'))
from text.corpus import Corpus
from text.document import Document
from text.sentence import Sentence

type_match = {"Specific_miRNAs": "mirna",
              # "Non-Specific_miRNAs": "mirna",
              "Genes/Proteins": "protein",
              # "Non-Specific_miRNAs-Genes/Proteins": "miRNA-gene",
              "Specific_miRNAs-Genes/Proteins": "miRNA-gene",
              "Non-Specific_miRNAs-Diseases": "miRNA-disease",
              "Specific_miRNAs-Diseases": "miRNA-disease",
              "Relation_Trigger": "entity",
              "Diseases": "disease",
              "Species": "entity"}


class MirnaCorpus(Corpus):
    def __init__(self, corpusdir, **kwargs):
        super(MirnaCorpus, self).__init__(corpusdir, **kwargs)
        self.subtypes = ["miRNA", "disease", "protein"]
        #self.rel_types = ["Specific_miRNAs-Genes/Proteins"]

    def load_corpus(self, corenlpserver, process=True):
        # self.path is just one file with every document
        time_per_abs = []
        with open(self.path, 'r') as xml:
            t = time.time()
            root = ET.fromstring(xml.read())
            all_docs = root.findall("document")
            widgets = [pb.Percentage(), ' ', pb.Bar(), ' ', pb.AdaptiveETA(), ' ', pb.Timer()]
            pbar = pb.ProgressBar(widgets=widgets, maxval=len(all_docs)).start()
            for i, doc in enumerate(all_docs):
                doctext = ""
                did = doc.get('id')
                doc_sentences = [] # get the sentences of this document
                doc_offset = 0 # offset of the current sentence relative to the document
                for sentence in doc.findall('sentence'):
                    sid = sentence.get('id')
                    #logging.info(sid)
                    text = sentence.get('text')
                    #text = text.replace('\r\n', '  ')
                    doctext += " " + text # generate the full text of this document
                    this_sentence = Sentence(text, offset=doc_offset, sid=sid, did=did)
                    doc_offset = len(doctext)
                    doc_sentences.append(this_sentence)
                newdoc = Document(doctext, process=False, did=did)
                newdoc.sentences = doc_sentences[:]
                newdoc.process_document(corenlpserver, "biomedical")
                self.documents[newdoc.did] = newdoc
                abs_time = time.time() - t
                time_per_abs.append(abs_time)
                pbar.update(i+1)
            pbar.finish()
        abs_avg = sum(time_per_abs)*1.0/len(time_per_abs)
        logging.info("average time per abstract: %ss" % abs_avg)

    def getOffsets(self, offset):
        # check if its just one offset per entity or not
        # add 1 to offset end to agree with python's indexes
        offsets = []
        offsetList = offset.split(';')
        for o in offsetList:
            offsets.append(int(o.split('-')[0]))
            offsets.append(int(o.split('-')[1])+1)

        #if len(offsets) > 2:
        #    print "too many offsets!"
            #sys.exit()
        return offsets

    def load_annotations(self, ann_dir, etype, rtype):
        time_per_abs = []
        pmids = []
        tagged = 0
        not_tagged = 0
        logging.info("loading miRNA annotations...")
        with open(ann_dir, 'r') as xml:
            #parse DDI corpus file
            t = time.time()
            root = ET.fromstring(xml.read())
            for doc in root.findall("document"):
                did = doc.get('id')
                pmid = doc.get('origId')
                pmids.append(pmid)
                for sentence in doc.findall('sentence'):
                    sid = sentence.get('id')
                    this_sentence = self.documents[did].get_sentence(sid)
                    if this_sentence is None:
                        print did, sid, "sentence not found!"
                        for entity in sentence.findall('entity'):
                            print entity.get('charOffset'), entity.get("type")
                        print [s.sid for s in self.documents[did].sentences]
                        sys.exit()
                        #continue
                    original_to_eids = {}
                    for entity in sentence.findall('entity'):
                        original_eid = entity.get('id')
                        entity_offset = entity.get('charOffset')
                        offsets = self.getOffsets(entity_offset)
                        try:
                            entity_type = type_match.get(entity.get("type"))
                        except KeyError:
                            continue
                        #print this_sentence.text[offsets[0]:offsets[-1]], entity.get("text")
                        #if "protein" in entity_type.lower() or "mirna" in entity_type.lower():
                        if entity_type and (etype == "all" or etype == entity_type):
                            eid = this_sentence.tag_entity(offsets[0], offsets[-1], entity_type,
                                                     text=entity.get("text"), original_id=original_eid)
                            if eid is not None:
                                tagged += 1
                            else:
                                not_tagged += 1
                            original_to_eids[original_eid] = eid
                        else:
                            logging.debug("skipped {}-{}: {}".format(entity.get("type"), original_eid, entity.get("text")))
                    for pair in sentence.findall('pair'):
                        try:
                            p_type = type_match[pair.get("type")]
                        except KeyError:
                            continue
                        p_true = pair.get("interaction")
                        #print p_type, self.rel_types
                        if (p_type == rtype or rtype == "all") and p_true == "True":
                            p_e1 = pair.get("e1")
                            p_e2 = pair.get("e2")
                            # if this relations contains one entity that was ignored, skip
                            if p_e1 not in original_to_eids or p_e2 not in original_to_eids:
                                continue
                            source = this_sentence.entities.get_entity(original_to_eids[p_e1])
                            if source:
                                logging.info("adding this relation: {}={}>{}".format(source.text, p_type, original_to_eids[p_e2]))
                                source.targets.append((original_to_eids[p_e2], p_type))
        # self.evaluate_normalization()
        print "tagged: {} not tagged: {}".format(tagged, not_tagged)
        with open(ann_dir + "-pmids.txt", 'w') as pmidsfile:
            pmidsfile.write("\n".join(pmids) + "\n")
        # self.run_ss_analysis()


def get_ddi_mirna_gold_ann_set(goldpath, entitytype, pairtype):
    logging.info("loading gold standard... {}".format(goldpath))
    gold_offsets = set()
    gold_pairs = set()
    original_id_to_offset = {}
    original_id_to_text = {}
    tree = ET.parse(goldpath)
    #with codecs.open(goldpath, 'r', 'utf-8') as xml:
    root = tree.getroot()
    #parse DDI corpus file
    t = time.time()
    # root = ET.fromstring(xml.read())
    rfile = open("corpora/miRNACorpus/miRNAcorpus_relations.txt", 'w')
    for doc in root.findall("document"):
        did = doc.get('id')
        doctext = ""
        for sentence in doc.findall('sentence'):
            sentence_text = sentence.get('text')
            #sentence_text = sentence_text.replace('\r\n', '  ')
            for entity in sentence.findall('entity'):
                entity_offset = entity.get('charOffset')
                if ";" in entity_offset:
                    continue
                offsets = entity_offset.split("-")
                start, end = int(offsets[0]) + len(doctext), int(offsets[1]) + len(doctext) + 1
                etype = type_match.get(entity.get("type"))
                original_id_to_offset[entity.get("id")] = (start, end)
                original_id_to_text[entity.get("id")] = entity.get("text")
                #print this_sentence.text[offsets[0]:offsets[-1]], entity.get("text")
                #if "protein" in entity_type.lower() or "mirna" in entity_type.lower():
                if etype == entitytype:
                    gold_offsets.add((did, start, end, entity.get("text")))
            for pair in sentence.findall('pair'):
                try:
                    p_type = type_match[pair.get("type")]
                except KeyError:
                    continue
                p_true = pair.get("interaction")
                if p_type == pairtype and p_true == "True":
                    gold_pair = (did, original_id_to_offset[pair.get("e1")], original_id_to_offset[pair.get("e2")],
                                    "{}={}>{}".format(original_id_to_text[pair.get("e1")], p_type, original_id_to_text[pair.get("e2")]))
                    gold_pairs.add(gold_pair)
                    norm_mirna = mirna_graph.map_label(original_id_to_text[pair.get("e1")])
                    if norm_mirna < 99:
                        norm_mirna[0] = original_id_to_text[pair.get("e1")]
                    norm_gene = get_uniprot_name(original_id_to_text[pair.get("e2")])
                    rfile.write("{}\t{}\n".format(norm_mirna[0], norm_gene[0]))
            doctext += " " + sentence_text # generate the full text of this document
    # logging.debug(gold_pairs)
    rfile.close()
    return gold_offsets, gold_pairs
