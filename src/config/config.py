import json

def main():
    with open("settings_base.json", "r") as settings:
        vals = json.load(settings)
        for k in vals:
            vals[k] = raw_input("{0}? (current: {1})".format(k, vals[k])) or vals[k]
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

paths = {
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
                       'cem': cpatents_sample_base,
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