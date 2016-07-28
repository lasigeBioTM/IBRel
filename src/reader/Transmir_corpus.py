import logging
import random

import progressbar as pb

from postprocessing import ssm
from reader.pubmed_corpus import PubmedCorpus
from mirna_base import MirbaseDB
from config import config
from text.mirna_entity import MirnaEntity, mirna_graph
from text.protein_entity import ProteinEntity, get_uniprot_name


class TransmirCorpus(PubmedCorpus):
    """
        Corpus generated from the TransmiR database, using distant supervision
    """
    def __init__(self, corpusdir, **kwargs):
        self.mirbase = MirbaseDB(config.mirbase_path)
        self.mirbase.load_graph()
        self.mirnas = {}
        self.tfs = {}
        self.pairs = {}
        self.pmids = set()
        self.normalized_mirnas = set() # normalized to miRBase
        self.normalized_tfs = set() #normalized to maybe UniProt
        self.normalized_pairs = set()
        self.db_path = corpusdir
        self.load_database()
        super(TransmirCorpus, self).__init__(corpusdir, self.pmids, **kwargs)
        # TODO: use negatome

    def load_database(self):
        logging.info("Loading TransmiR database...")
        with open(self.db_path, 'r') as dbfile:
            for line in dbfile:
                tsv = line.strip().split("\t")
                if tsv[-1].lower() == "human":
                    tfname = tsv[0]
                    mirname = tsv[3]
                    func = tsv[5].split(";")
                    disease = tsv[6].split(";")
                    active = tsv[7]
                    pmid = tsv[8].split(";")

                    # for f in func:
                    #     funcs.add(f.strip())
                    # for d in disease:
                    #     if d != "see HMDD (http://cmbi.bjmu.edu.cn/hmdd)":
                    #         diseases.add(d.strip())
                    for p in pmid:
                        logging.info(p)
                        self.pmids.add(p.strip())
                    #mirnas[mirname] = (func, [d for d in disease if d != "see HMDD (http://cmbi.bjmu.edu.cn/hmdd)"])
                    #entries[(tfname, mirname)] = (active, pmid)

    def normalize_entities(self):
        logging.info("Normalizing entities...")
        for mir in self.mirnas:
            match = self.mirbase.map_label(mir)
            #if match > 0.6:
            self.normalized_mirnas.add(match[0])

    def load_annotations(self, db_path, etype, ptype):
        self.mirnas = {}
        self.tfs = {}
        self.pairs = {}
        self.pmids = set()
        self.normalized_mirnas = set()  # normalized to miRBase
        self.normalized_tfs = set()  # normalized to maybe UniProt
        self.normalized_pairs = set()
        with open(db_path, 'r') as dbfile:
            for line in dbfile:
                tsv = line.strip().split("\t")
                if tsv[-1].lower() == "human":
                    pmids = tsv[8].split(";")
                    tfname = tsv[0]
                    mirname = tsv[3]
                    for pmid in pmids:
                        if pmid not in self.tfs:
                            self.tfs[pmid] = set()
                        if pmid not in self.mirnas:
                            self.mirnas[pmid] = set()

                        if not mirname.startswith("hsa-"):
                            mirname = "hsa-" + mirname
                        #self.mirnas[pmid].add(mirname)

                        tf = None
                        for pmidtf in self.tfs[pmid]:
                            if pmidtf.text == tfname:
                                tf = pmidtf
                        if tf is None:
                            eid = len(self.tfs[pmid]) + len(self.mirnas[pmid])
                            tf = ProteinEntity([], pmid, text=tfname, did=pmid, eid="{}.e{}".format(pmid, eid))
                            self.tfs[pmid].add(tf)

                        mirna = None
                        for pmidmir in self.mirnas[pmid]:
                            if pmidmir.text == mirname:
                                mirna = pmidmir
                        if mirna is None:
                            eid = len(self.tfs[pmid]) + len(self.mirnas[pmid])
                            mirna = MirnaEntity([], pmid, text=mirname, did=pmid, eid="{}.e{}".format(pmid, eid))
                            self.mirnas[pmid].add(mirna)
                        tf.targets.append((mirna.eid, "miRNA-gene"))
                        # print "tf gos: {}".format(" ".join(tf.go_ids))
                        #print "mirna gos: {}".format(" ".join(mirna.go_ids))


        # self.normalize_entities()
        #self.run_analysis()

    def run_analysis(self):
        correct_count = 0 # numver of real miRNA-gene pairs with common gos
        incorrect_count = 0 #number of random miRNA-gene pairs with common go
        all_tfs = []
        all_mirnas = []
        for pmid in self.tfs:
            all_tfs = []
            all_mirnas = []
            correct_count = 0  # numver of real miRNA-gene pairs with common gos
            incorrect_count = 0  # number of random miRNA-gene pairs with common go
            for tf in self.tfs[pmid]:
                all_tfs.append(tf)
                mirna = None
                for mirna_eid in tf.targets:
                    for m in self.mirnas[pmid]:
                        if m.eid == mirna_eid[0]:
                            mirna = m
                            break
                    all_mirnas.append(mirna)
                    # common_gos = set(tf.go_ids).intersection(set(mirna.go_ids))
                    # if len(common_gos) > 0:
                    #     print "{}->{} common gos:{}".format(tf.text, mirna.text, " ".join(common_gos))
                    #     correct_count += 1
            if len(all_tfs) > 1 and len(all_mirnas) > 1:
                for i in range(0, 10):
                    random_tf = random.choice(all_tfs)
                    random_mirna = random.choice(all_mirnas)
                    common_gos = set(random_tf.go_ids).intersection(set(random_mirna.go_ids))
                    if (random_mirna.eid, "miRNA-gene") in random_tf.targets:
                        #if len(common_gos) > 0:
                        if random_mirna.best_go.startswith("GO:") and random_tf.best_go.startswith("GO"):
                            ss = ssm.simui_go(random_mirna.best_go, random_tf.best_go)
                            #print "correct:", ss
                            correct_count += ss
                        else:
                            correct_count += 1
                    else:
                        #if len(common_gos) > 0:
                        if random_mirna.best_go.startswith("GO:") and random_tf.best_go.startswith("GO"):
                            ss = ssm.simui_go(random_mirna.best_go, random_tf.best_go)
                            print "incorrect:", ss
                            incorrect_count += ss
                        else:
                            incorrect_count += 1
                print "{}-{} ({} mirnas, {} tfs".format(correct_count, incorrect_count, len(all_mirnas), len(all_tfs))

def get_transmir_gold_ann_set(goldpath, entitytype):
    logging.info("loading gold standard... {}".format(goldpath))
    gold_entities = set()
    gold_relations = {}
    with open(goldpath, 'r') as goldfile:
        for l in goldfile:
            tsv = l.strip().split("\t")
            if tsv[-1].lower() == "human":
                # print "gold standard", tsv[8], tsv[0], tsv[3], entitytype
                pmids = tsv[8].split(";")
                norm_mirna = mirna_graph.map_label(tsv[3])
                if norm_mirna < 99:
                    norm_mirna[0] = tsv[3]
                norm_gene = get_uniprot_name(tsv[0])
                for did in pmids:
                    if entitytype == "mirna":
                        gold_entities.add(("PMID" + did, "0", "0", norm_mirna[0].lower()))
                    elif entitytype == "protein":
                        gold_entities.add(("PMID" + did, "0", "0", norm_gene[0].lower()))
                    gold_relations[("PMID" + did, norm_mirna[0], norm_gene[0], norm_mirna[0] + "=>" + norm_gene[0])] = [tsv[3] + "=>" + tsv[0]]
                    #gold_relations[("PMID", norm_mirna[0], norm_gene[0], norm_mirna[0] + "=>" + norm_gene[0])] = [tsv[3] + "=>" + tsv[0]]

    # print gold_entities
    return gold_entities, gold_relations


