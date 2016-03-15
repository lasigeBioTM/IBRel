import json
import shutil

def main():
    with open("settings_base.json", "r") as settings:
        vals = json.load(settings)
        for k in vals:
            vals[k] = raw_input("{0}? (current: {1})".format(k, vals[k])) or vals[k]
    shutil.copy("bin/base.prop", vals["stanford_ner_dir"])
    with open("settings.json", "w") as settings:
        json.dump(vals, settings, sort_keys=True, indent=4)

if __name__ == "__main__":
    main()

with open("settings.json") as settings:
    vals = json.load(settings)
    use_chebi = vals["use_chebi"]
    if use_chebi:
        chebi_host = vals["chebi_host"]
        chebi_user = vals["chebi_user"]
        chebi_pw = vals["chebi_pw"]
        chebi_db = vals["chebi_db"]
    use_go = vals["use_go"]
    if use_go:
        go_host = vals["go_host"]
        go_user = vals["go_user"]
        go_pw = vals["go_pw"]
        go_db = vals["go_db"]
    host_ip = vals["host_ip"]
    geniass_path = vals["geniass_path"]
    florchebi_path = vals["florchebi_path"]
    corenlp_dir = vals["corenlp_dir"]
    stanford_ner_dir = vals["stanford_ner_dir"]
    stanford_ner_train_ram = vals["stanford_ner_train_ram"]
    stanford_ner_test_ram = vals["stanford_ner_test_ram"]
    stoplist = vals["stoplist"]
    mirbase_path = vals["mirbase_path"]

if use_chebi or use_go:
    import MySQLdb
if use_chebi:
    chebi_conn = MySQLdb.connect(host=chebi_host,
                                 user=chebi_user,
                                 passwd=chebi_pw,
                                 db=chebi_db)
if use_go:
    go_conn = MySQLdb.connect(host=go_host,
                              user=go_user,
                              passwd=go_pw,
                              db=go_db)

all_entity_types = ("Gene",
                     "Gene_Family",
                     "Box",
                     "Promoter",
                     "RNA",
                     "Protein",
                     "Protein_Family",
                     "Protein_Complex",
                     "Protein_Domain",
                     "Hormone",
                     "Regulatory_Network",
                     "Pathway",
                     "Genotype",
                     "Tissue",
                     "Development_Phase",
                     "Environmental_Factor")

all_entity_groups = {"DNA_Product": ("RNA", "Protein", "Protein_Family", "Protein_Complex", "Protein_Domain"),
                     "DNA": ("Gene", "Gene_Family", "Box", "Promoter"),
                     "Dynamic_Process": ("Regulatory_Network", "Pathway"),
                     "Internal_Factor": ("Tissue", "Development_Phase", "Genotype")}

all_entity_groups["Functional_Molecule"] = all_entity_groups["DNA_Product"] + ("Hormone",)
all_entity_groups["Molecule"] = all_entity_groups["DNA"] + all_entity_groups["Functional_Molecule"]
all_entity_groups["Factor"] = all_entity_groups["Internal_Factor"] + ("Environmental_Factor",)

pair_types = {
    "Binds_To":
        {"source_role": "Functional_Molecule",
         "source_types": all_entity_groups["Functional_Molecule"],
         "target_role": "Molecule",
         "target_types": all_entity_groups["Molecule"]},
    "Composes_Primary_Structure":
        {"source_role": "DNA_Part",
         "source_types": ("Box", "Promoter"),
         "target_role": "DNA",
         "target_types": all_entity_groups["DNA"]},
    "Composes_Protein_Complex":
        {"source_role": "Amino_Acid_Sequence",
         "source_types": ("Protein", "Protein_Family", "Protein_Complex", "Protein_Domain"),
         "target_role": "Protein_Complex",
         "target_types": ("Protein_Complex",)},
    "Exists_At_Stage":
        {"source_role": "Functional_Molecule",
         "source_types": all_entity_groups["Functional_Molecule"],
         "target_role": "Development",
         "target_types": ("Development_Phase",)},
    "Exists_At_Genotype":
        {"source_role": "Molecule",
         "source_types": all_entity_groups["Molecule"] + ("Biological context",),  # mutually exclusive
         "target_role": "Genotype",
         "target_types": ("Genotype",)},
    "Has_Sequence_Identical_To":
        {"source_role": "Element1",
         "source_types": all_entity_types,
         "target_role": "Element2",
         "target_types": all_entity_types},
    "Interacts_with":
        {"source_role": "Agent",
         "source_types": all_entity_groups["Molecule"],
         "target_role": "Target",
         "target_types": all_entity_groups["Molecule"]},
    "Is_Involved_In_Process":
        {"source_role": "Participant",
         "source_types": all_entity_groups["Molecule"],
         "target_role": "Process",
         "target_types": all_entity_groups["Dynamic_Process"]},
    "Is_Localized_In":
        {"source_role": "Functional_Molecule",
         "source_types": all_entity_groups["Functional_Molecule"] + all_entity_groups["Dynamic_Process"],
         "target_role": "Target_Tissue",
         "target_types": ("Tissue",)},
    "Is_Member_Of_Family":
        {"source_role": "Element",
         "source_types": ("Gene", "Gene_Family", "Protein", "Protein_Domain", "Protein_Family", "RNA"),
         "target_role": "Family",
         "target_types": ("Gene_Family", "Protein_Family", "RNA")},
    "Is_Protein_Domain_Of":
        {"source_role": "Domain",
         "source_types": ("Protein_Domain",),
         "target_role": "Product",
         "target_types": all_entity_groups["DNA_Product"]},
    "Occurs_During":
        {"source_role": "Process",
         "source_types": all_entity_groups["Dynamic_Process"],
         "target_role": "Development",
         "target_types": ("Development_Phase",)},
    "Occurs_In_Genotype":
        {"source_role": "Process",
         "source_types": all_entity_groups["Dynamic_Process"],
         "target_role": "Genotype",
         "target_types": ("Genotype",)},
    "Regulates_Accumulation":
        {"source_role": "Agent",
         "source_types": all_entity_types,
         "target_role": "Functional_Molecule",
         "target_types": all_entity_groups["Functional_Molecule"]},
    "Regulates_Development_Phase":
        {"source_role": "Agent",
         "source_types": all_entity_types,
         "target_role": "Development",
         "target_types": ("Development_Phase",)},
    "Regulates_Expression":
        {"source_role": "Agent",
         "source_types": all_entity_types,
         "target_role": "DNA",
         "target_types": all_entity_groups["DNA"]},
    "Regulates_Molecule_Activity":
        {"source_role": "Agent",
         "source_types": all_entity_types,
         "target_role": "Molecule",
         "target_types": all_entity_groups["Molecule"]},
    "Regulates_Process":
        {"source_role": "Agent",
         "source_types": all_entity_types,
         "target_role": "Process",
         "target_types": all_entity_groups["Dynamic_Process"]},
    "Regulates_Tissue_Development":
        {"source_role": "Agent",
         "source_types": all_entity_types,
         "target_role": "Target_Tissue",
         "target_types": ("Tissue",)},
    "Transcribes_Or_Translates_To":
        {"source_role": "Source",
         "source_types": all_entity_groups["DNA"] + ("RNA",),
         "target_role": "Product",
         "target_types": all_entity_groups["DNA_Product"]},
    "Is_Linked_To":
        {"source_role": "Agent",
         "source_types": all_entity_types,
         "target_role": "Target",
         "target_types": all_entity_types}
}

chemdner_base = "CHEMDNER/"
chemdner_sample_base = "CHEMDNER/CHEMDNER_SAMPLE_JUNE25/"

cpatents_sample_base = "CHEMDNER-patents/chemdner_cemp_sample_v02/"
gpro_dev_base = "CHEMDNER-patents/gpro_development_set/"
gpro_test_base = "CHEMDNER-patents/CHEMDNER_TEST_TEXT/"
ddi_train_base = "DDICorpus/Train/All/"
pubmed_test_base = "corpora/pubmed-test/"
transmir_base = "corpora/transmir/"
genia_base = "corpora/GENIA_term_3.02/"
genia_sample_base = "corpora/genia_sample/"
mirnacorpus_base = "corpora/miRNACorpus/"
mirtex_base = "corpora/miRTex/"
jnlpba_base = "corpora/JNLPBA/"
seedev_base = "corpora/SeeDev/"

paths = {
    'seedev_train':{
        'text': seedev_base + "BioNLP-ST-2016_SeeDev-binary_train/",
        'annotations': seedev_base + "BioNLP-ST-2016_SeeDev-binary_train/",
        'corpus': "data/SeeDev-train.txt.pickle",
        'format': "seedev"
    },
    'seedev_dev':{
        'text': seedev_base + "BioNLP-ST-2016_SeeDev-binary_dev/",
        'annotations': seedev_base + "BioNLP-ST-2016_SeeDev-binary_dev/",
        'corpus': "data/SeeDev-dev.txt.pickle",
        'format': "seedev"
    },
    'jnlpba_train':{ # pre processed genia corpus

    },
    'jnlpba_test':{
        'text': jnlpba_base + "test/Genia4EReval1.raw",
        'annotations': jnlpba_base + "test/Genia4EReval1.iob2",
        'corpus': "data/Genia4EReval1.raw.pickle",
        'format': "jnlpba"
    },
    'miRNACorpus_train':{
        'text': mirnacorpus_base + "miRNA-Train-Corpus.xml",
        'annotations': mirnacorpus_base + "miRNA-Train-Corpus.xml",
        'corpus': "data/miRNA-Train-Corpus.xml.pickle",
        'format': "ddi-mirna"
    },
    'miRNACorpus_test':{
        'text': mirnacorpus_base + "miRNA-Test-Corpus.xml",
        'annotations': mirnacorpus_base + "miRNA-Test-Corpus.xml",
        'corpus': "data/miRNA-Test-Corpus.xml.pickle",
        'format': "ddi-mirna"
    },
    'miRTex_dev':{
        'text': mirtex_base + "development/",
        'annotations': mirtex_base + "development/",
        'corpus': "data/miRTex-development.txt.pickle",
        'format': "mirtex"
    },
    'miRTex_test':{
        'text': mirtex_base + "test/",
        'annotations': mirtex_base + "test/",
        'corpus': "data/miRTex-test.txt.pickle",
        'format': "mirtex"
    },
    'transmir_tfs':{
        'text': transmir_base + "transmir_pmids.txt",
        'annotations': transmir_base + "transmir_tfs.txt",
        'corpus': "data/transmir_pmids.txt.pickle",
        'format': "pubmed"
    },
    'genia_sample': {
        'text': genia_sample_base + "genia_sample.xml",
        'annotations': genia_sample_base + "genia_sample.xml",
        'corpus': "data/genia_sample.xml.pickle",
        'format': "genia"
    },
    'genia': {
        'text': genia_base + "GENIAcorpus3.02.xml",
        'annotations': genia_base + "GENIAcorpus3.02.xml",
        'corpus': "data/GENIAcorpus3.02.xml.pickle",
        'format': "genia"
    },
    'transmir': {
        'text': "data/transmir_v1.2.tsv",
        'annotations': "data/transmir_v1.2.tsv",
        'corpus': "data/transmir_v1.2.tsv.pickle",
        'format': "transmir"
    },
    'pubmed_test': {
        'text': pubmed_test_base + "pmids_test.txt",
        'annotations': "",
        'corpus': "data/pmids_test.txt.pickle",
        'format': "pubmed"
    },
    'thymedata_dev':{
        'text': "corpora/thymedata-1.1.0/text/Dev/",
        'annotations': "corpora/thymedata-1.1.0/coloncancer/Dev/",
        'corpus': "data/coloncancer_dev.txt.pickle",
        'format': "tempeval"
    },

    'thymedata_sample':{
        'text': "corpora/thymedata-1.1.0/text/sample/",
        'annotations': "corpora/thymedata-1.1.0/sample/",
        'corpus': "data/thymedata_sample.txt.pickle",
        'format': "tempeval"
    },
    'thymedata_train':{
        'text': "corpora/thymedata-1.1.0/text/Train/",
        'annotations': "corpora/thymedata-1.1.0/coloncancer/Train/",
        'corpus': "data/coloncancer_train.txt.pickle",
        'format': "tempeval"
    },

        'thymedata_traindev':{
        'text': "corpora/thymedata-1.1.0/text/TrainDev/",
        'annotations': "corpora/thymedata-1.1.0/coloncancer/TrainDev/",
        'corpus': "data/coloncancer_traindev.txt.pickle",
        'format': "tempeval"
    },
    'thymedata_test':{
        'text': "corpora/thymedata-1.1.0/text/test/",
        'annotations': "corpora/thymedata-1.1.0/coloncancer/test/",
        'corpus': "data/coloncancer_test.txt.pickle",
        'format': "tempeval"
    },

    'chemdner_sample': { # CHEMDNER 2013
                         'text': chemdner_sample_base + "chemdner_sample_abstracts.txt",
                         'annotations': chemdner_sample_base + "chemdner_sample_annotations.txt",
                         'cem': chemdner_sample_base + "chemdner_sample_cem_gold_standard.txt",
                         'cdi': chemdner_sample_base + "chemdner_sample_cdi_gold_standard.txt",
                         'corpus': "data/chemdner_sample_abstracts.txt.pickle",
                         'format': "chemdner",
                         },
    'cemp_sample':{ # CHEMDNER 2015
                    'text': cpatents_sample_base + "chemdner_patents_sample_text.txt",
                    'annotations': cpatents_sample_base + "chemdner_cemp_gold_standard_sample.tsv",
                    'cem': cpatents_sample_base + "chemdner_cemp_gold_standard_sample_eval.tsv",
                    'corpus': "data/chemdner_patents_sample_text.txt.pickle",
                    'format': "chemdner",
                    },
    'gpro_dev':{ # CHEMDNER 2015 gene/protein NER
                 'text': gpro_dev_base + "gpro_patents_development_text.txt",
                 'annotations': gpro_dev_base + "chemdner_gpro_gold_standard_development.tsv",
                 'cem': gpro_dev_base + "chemdner_gpro_gold_standard_development_eval.tsv",
                 'corpus': "data/gpro_patents_development_text.txt.pickle",
                 'format': "gpro",
                 },
    'ddi_trainall':{ # DDI 2013 - drug-drug interactions
                     'text': ddi_train_base,
                     'annotations': ddi_train_base,
                     'corpus': "data/ddi_trainall.txt.pickle",
                     'format': "ddi",
                     },
}
