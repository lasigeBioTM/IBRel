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
paths = {
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
