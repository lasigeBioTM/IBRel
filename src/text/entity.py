from __future__ import division, absolute_import, unicode_literals
import logging
import xml.etree.ElementTree as ET

from text.offset import Offset, Offsets, perfect_overlap, contained_by, contains
from postprocessing.chebi_resolution import element_base
from config import config

# words that may seem like they are not part of named chemical entities but they are
chem_words = set()
for e in element_base:
    chem_words.add(e.lower())
    chem_words.add(element_base[e][0].lower())

# words that are never part of chemical entities
chem_stopwords = set()
with open(config.stoplist, 'r') as stopfile:
    for l in stopfile:
        w = l.strip().lower()
        if w not in chem_words and len(w) > 1:
            chem_stopwords.add(w)


class Entity(object):
    """Base entity class"""

    def __init__(self, tokens, **kwargs):
        self.type = kwargs.get('e_type', None)
        self.text = kwargs.get("text", None)
        self.did = kwargs.get("did", None)
        self.eid = kwargs.get("eid")
        self.tokens = tokens
        self.start = tokens[0].start
        self.end = tokens[-1].end
        self.dstart = tokens[0].dstart
        self.dend = tokens[-1].dend
        self.recognized_by = []
        self.subentities = []
        self.score = kwargs.get("score", 0)
        #logging.info("created entity {} with score {}".format(self.text, self.score))

    def __str__(self):
        output = self.text + " relative to sentence:" + str(self.start) + ":" + str(self.end)
        output += " relative to document:" + str(self.dstart) + ":" + str(self.dend) + " => "
        output += ' '.join([t.text for t in self.tokens])
        return output

    def write_chemdner_line(self, outfile, rank=1):
        if self.sid.endswith(".s0"):
            ttype = "T"
        else:
            ttype = "A"
        start = str(self.tokens[0].dstart)
        end = str(self.tokens[-1].dend)
        loc = ttype + ":" + start + ":" + end
        if isinstance(self.score ,dict):
            conf = sum(self.score.values())/len(self.score)
        else:
            conf = self.score
        #outfile.write('\t'.join([self.did, loc, str(rank)]) + '\n')
        outfile.write("{0}\t{1}\t{2}\t{3}\t{4}\n".format(self.did, loc, str(rank), str(conf), self.text))
        return (self.did, loc, str(rank), str(conf), self.text)

    def write_bioc_annotation(self, parent):
        bioc_annotation = ET.SubElement(parent, "annotation")
        bioc_annotation_text = ET.SubElement(bioc_annotation, "text")
        bioc_annotation_text.text = self.text
        bioc_annotation_info = ET.SubElement(bioc_annotation, "infon", {"key":"type"})
        bioc_annotation_info.text = self.type
        bioc_annotation_id = ET.SubElement(bioc_annotation, "id")
        bioc_annotation_id.text = self.eid
        bioc_annotation_offset = ET.SubElement(bioc_annotation, "offset")
        bioc_annotation_offset.text = str(self.dstart)
        bioc_annotation_length = ET.SubElement(bioc_annotation, "length")
        bioc_annotation_length.text = str(self.dend - self.dstart)
        return bioc_annotation

    def get_dic(self):
        dic = {}
        dic["text"] = self.text
        dic["type"] = self.type
        dic["eid"] = self.eid
        dic["offset"] = self.dstart
        dic["size"] = self.dend - self.dstart
        dic["sentence_offset"] = self.start
        return dic


class ChemicalEntity(Entity):
    """Chemical entities"""
    def __init__(self, tokens, **kwargs):
        # Entity.__init__(self, kwargs)
        super(ChemicalEntity, self).__init__(tokens, **kwargs)
        self.type = "chemical"
        self.subtype = kwargs.get("subtype")
        self.chebi_id = None
        self.chebi_score = 0
        self.chebi_name = None

    def get_dic(self):
        dic = super(ChemicalEntity, self).get_dic()
        dic["subtype"] = self.subtype
        dic["chebi_id"] = self.chebi_id
        dic["chebi_name"] = self.chebi_name
        dic["ssm_score"] = self.ssm_score
        dic["ssm_entity"] = self.ssm_best_ID
        return dic
    
    def validate(self, ths, rules):
        """
        Use rules to validate if the entity was correctly identified
        :param rules: 
        :return: True if entity does not fall into any of the rules, False if it does
        """
        if "stopwords" in rules:
            words = self.text.split(" ")
            stop = False
            for s in chem_stopwords:
                if any([s == w.lower() for w in words]):
                    logging.debug("ignored stopword %s" % e.text)
                    stop = True
            if stop:
                return False

        if "paren" in rules:
            if (self.text[-1] == ")" and "(" not in self.text) or (self.text[-1] == "]" and "[" not in self.text) or \
                    (self.text[-1] == "}" and "{" not in self.text):
                logging.debug("parenthesis %s" % e.text)
                self.dend -= 1
                self.end -= 1
                self.text = self.text[:-1]
            if (self.text[0] == "(" and ")" not in self.text) or (self.text[0] == "[" and "]" not in self.text) or \
                    (self.text[0] == "{" and "}" not in self.text):
                logging.debug("parenthesis %s" % self.text)
                self.dstart += 1
                self.start += 1
                self.text = self.text[1:]

        if "hyphen" in rules and "-" in e.text and all([len(t) > 3 for t in e.text.split("-")]):
            logging.debug("ignored hyphen %s" % e.text)
            return False

        #if all filters are 0, do not even check
        if "ssm" in ths and ths["ssm"] != 0 and e.ssm_score < ths["ssm"] and e.text.lower() not in chem_words:
            #logging.debug("filtered %s => %s" % (e.text,  str(e.ssm_score)))
            return False

        if "alpha" in rules:
            alpha = False
            for c in e.text.strip():
                if c.isalpha():
                    alpha = True
                    break
            if not alpha:
                logging.debug("ignored no alpha %s" % e.text)
                return False

        if "dash" in rules and (e.text.startswith("-") or e.text.endswith("-")):
            logging.debug("excluded for -: {}".format(e.text))
            return False
        return True


class ChemdnerAnnotation(ChemicalEntity):
    """Chemical entity annotated on the CHEMDNER corpus"""
    def __init__(self, tokens, sid, **kwargs):
        # ChemicalEntity.__init__(self, kwargs)
        super(ChemdnerAnnotation, self).__init__(tokens, **kwargs)
        self.sid = sid


class ProteinEntity(Entity):
    def __init__(self, tokens, **kwargs):
        # Entity.__init__(self, kwargs)
        super(ProteinEntity, self).__init__(tokens, **kwargs)
        self.type = "protein"
        self.subtype = kwargs.get("subtype")


    def get_dic(self):
        dic = super(ProteinEntity, self).get_dic()
        dic["subtype"] = self.subtype
        dic["ssm_score"] = self.ssm_score
        dic["ssm_entity"] = self.ssm_go_ID
        return dic


class Entities(object):
    """Group of entities related to a text"""

    def __init__(self, **kwargs):
        self.elist = {}
        self.sid = kwargs.get("sid")
        self.did = kwargs.get("did")

    def add_entity(self, entity, esource):
        if esource not in self.elist:
            self.elist[esource] = []
            # logging.debug("created new entry %s for %s" % (esource, self.sid))
        #if entity in self.elist[esource]:
        #    logging.info("Repeated entity! %s", entity.eid)
        self.elist[esource].append(entity)

    def write_chemdner_results(self, source, outfile, ths={"ssm":0.0}, rules=[], totalentities=0):
        """
        Write results that can be evaluated with the BioCreative evaluation script
        :param source: Base model path
        :param outfile: Text Results path to be evaluated
        :param ths: Thresholds
        :param rules: Validation rules
        :param totalentities: Number of entities already validated on this document (for ranking)
        :return:
        """
        lines = []
        offsets = Offsets()
        rank = totalentities
        #    print self.elist.keys()
        for s in self.elist:
            #if s != "goldstandard":
            #    logging.info("%s - %s(%s)" % (self.sid, s, source))
            if s.startswith(source): #use everything
                #logging.info("%s - %s" % (self.sid, s))

                for e in self.elist[s]:
                    val = e.validate(ths, rules)
                    if not val:
                        continue

                    # Overlap rules
                    eid_offset = Offset(e.dstart, e.dend, text=e.text, sid=e.sid)
                    exclude = [perfect_overlap]
                    if "contained_by" in rules:
                        exclude.append(contained_by)
                    toadd, v, alt = offsets.add_offset(eid_offset, exclude_if=exclude)
                    if toadd:
                        #logging.info("added %s" % e)
                        line = e.write_chemdner_line(outfile, rank)
                        lines.append(line)
                        rank += 1
        return lines, rank

    def get_results(self, esource):
        return self.elist.get(esource)

    def find_entity(self, start, end):
        """Find entity in this sentence between start and end (relative to document)"""
        entity = None
        for eid in self.elist["combined_results"]:
            if eid.start == start and eid.end == end:
                entity = eid
        return entity

    def combine_entities(self, base_model, name):
        """
        Combine entities from multiple models starting with base_model into one module named name
        :param base_model: string corresponding to the prefix of the models
        :param name: new model path
        """
        combined = {}
        offsets = Offsets()
        for s in self.elist:
            #logging.info("%s - %s" % (self.sid, s))
            if s.startswith(base_model) and s != name: #use everything
                for e in self.elist[s]: # TODO: filter for classifier confidence
                    #if any([word in e.text for word in self.stopwords]):
                    #    logging.info("ignored stopword %s" % e.text)
                    #    continue
                    #eid_alt =  e.sid + ":" + str(e.dstart) + ':' + str(e.dend)
                    next_eid = "{0}.e{1}".format(e.sid, len(combined))
                    eid_offset = Offset(e.dstart, e.dend, text=e.text, sid=e.sid, eid=next_eid)
                    added = False
                    # check for perfect overlaps
                    for i, o in enumerate(offsets.offsets):
                        overlap = eid_offset.overlap(o)
                        if overlap == perfect_overlap:
                            combined[o.eid].recognized_by.append(s)
                            combined[o.eid].score[s] = e.score
                            combined[o.eid].ssm_score_all[s] = e.ssm_score
                            added = True
                            #logging.info(combined[o.eid].ssm_score_all)
                            #logging.info("added {0}-{1} to entity {2}".format(s.split("_")[-1], e.text, combined[o.eid].text))
                            break
                    if not added:
                        offsets.offsets.add(eid_offset)
                        e.recognized_by = [s]
                        e.score = {s: e.score}
                        e.ssm_score_all= {s: e.ssm_score}
                        combined[next_eid] = e
                        #logging.info("new entity: {0}-{1}".format(s.split("_")[-1], combined[next_eid].text))
        self.elist[name] = combined.values()