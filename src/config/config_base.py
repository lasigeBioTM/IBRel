import MySQLdb
chebi_host = ""
chebi_user = ""
chebi_pw = ""
chebi_db = ""

chebi_conn = MySQLdb.connect(host=chebi_host,
                     user=chebi_user,
                     passwd=chebi_pw,
                     db=chebi_db)

go_host = ""
go_user = ""
go_pw = ""
go_db = ""

go_conn = MySQLdb.connect(host=go_host,
                     user=go_user,
                     passwd=go_pw,
                     db=go_db)

host_ip = ""
geniass_path = "./bin/geniass"
florchebi_path = "./bin"
corenlp_dir = "bin/stanford-corenlp-full-2015-01-30/"
stoplist = "data/stopwords.txt"

chemdner_base = "CHEMDNER/"
chemdner_train_base = "CHEMDNER/CHEMDNER_TRAIN_V01/"
chemdner_dev_base = "CHEMDNER/CHEMDNER_DEVELOPMENT_V02/"
chemdner_sample_base = "CHEMDNER/CHEMDNER_SAMPLE_JUNE25/"
chemdner_test_base = "CHEMDNER/CHEMDNER_TEST_ANNOTATION/"
chemdner_traindev_base = "CHEMDNER/CHEMDNER_DEV_TRAIN_V02/"

cpatents_sample_base = "CHEMDNER-patents/chemdner_cemp_sample_v02/"
cpatents_train_base = "CHEMDNER-patents/cemp_training_set/"
cpatents_train_base1 = "CHEMDNER-patents/cemp_training_set1/"
cpatents_train_base2 = "CHEMDNER-patents/cemp_training_set2/"
gpro_train_base1 = "CHEMDNER-patents/gpro_training_set1/"
gpro_train_base2 = "CHEMDNER-patents/gpro_training_set2/"
gpro_train_base = "CHEMDNER-patents/gpro_training_set_v02/"
cemp_dev_base = "CHEMDNER-patents/cemp_development_set_v03/"
cemp_test_base = "CHEMDNER-patents/CHEMDNER_TEST_TEXT/"
gpro_dev_base = "CHEMDNER-patents/gpro_development_set/"
gpro_test_base = "CHEMDNER-patents/CHEMDNER_TEST_TEXT/"

ddi_train_base = "DDICorpus/Train/All/"
ddi_smalltest_base = "DDICorpus/SmallTest/"

chebi_patents_base = "ChebiPatents/"

paths = {
    'chemdner_train': {'text': chemdner_train_base + "chemdner_abs_training.txt",
                       'annotations': chemdner_train_base + "chemdner_ann_training_13-07-31.txt",
                       'cem': chemdner_train_base + "cem_ann_training_13-07-31.txt",
                       'cdi': chemdner_train_base + "cdi_ann_training_13-07-31.txt",
                       'corpus': "data/chemdner_abs_training.txt.pickle",
                       'format': "chemdner",
                       },
    'chemdner_dev':{
                    'text': chemdner_dev_base + "chemdner_abs_development.txt",
                    'annotations': chemdner_dev_base + "chemdner_ann_development_13-08-18.txt",
                    'cem': chemdner_dev_base + "cem_ann_development_13-08-18.txt",
                    'cdi': chemdner_dev_base + "cdi_ann_development_13-08-18.txt",
                    'corpus': "data/chemdner_abs_development.txt.pickle",
                       'format': "chemdner",
                    },
    'chemdner_sample': {
                        'text': chemdner_sample_base + "chemdner_sample_abstracts.txt",
                        'annotations': chemdner_sample_base + "chemdner_sample_annotations.txt",
                        'cem': chemdner_sample_base + "chemdner_sample_cem_gold_standard.txt",
                        'cdi': chemdner_sample_base + "chemdner_sample_cdi_gold_standard.txt",
                        'corpus': "data/chemdner_sample_abstracts.txt.pickle",
                       'format': "chemdner",
                      },
    'chemdner_microsample': {
                           'text': chemdner_base + "chemdner_microsample_abstracts.txt",
                           'annotations': chemdner_base + "chemdner_microsample_annotations.txt",
                           'corpus': "data/chemdner_microsample_abstracts.txt.pickle",
                       'format': "chemdner",
    },
    'chemdner_test': {
                      'text': chemdner_test_base + "chemdner_test_abs.txt",
                      'annotations': chemdner_test_base + "chemdner_ann_test_13-09-13.txt",
                      'cem': chemdner_test_base + "cem_ann_test_13-09-13.txt",
                      'cdi': chemdner_test_base + "cdi_ann_test_13-09-13.txt",
                      'corpus': "data/chemdner_test_abs.txt.pickle",
                       'format': "chemdner",
                    },
    'chemdner_traindev': {
                          'text': chemdner_traindev_base + "chemdner_abs.txt",
                          'annotations': chemdner_traindev_base + "chemdner_ann.txt",
                          'cem': chemdner_traindev_base + "cem_ann.txt-sampled.txt",
                          'cdi': chemdner_traindev_base + "cdi_ann.txt",
                          'corpus': "data/chemdner_abs.txt.pickle",
                       'format': "chemdner",
                         },
    'cemp_sample':{
                       'text': cpatents_sample_base + "chemdner_patents_sample_text.txt",
                       'annotations': cpatents_sample_base + "chemdner_cemp_gold_standard_sample.tsv",
                       'cem': cpatents_sample_base,
                       'corpus': "data/chemdner_patents_sample_text.txt.pickle",
                       'format': "chemdner",
                      },
    'cemp_train':{
                      'text': cpatents_train_base + "chemdner_patents_train_text.txt",
                      'annotations': cpatents_train_base + "chemdner_cemp_gold_standard_train.tsv",
                      'cem': cpatents_train_base + "chemdner_cemp_gold_standard_train_eval.tsv",
                      'corpus': "data/chemdner_patents_train_text.txt.pickle",
                      'format': "chemdner",
    },
    'cemp_train1':{
                      'text': cpatents_train_base1 + "chemdner_patents_train_text1.txt",
                      'annotations': cpatents_train_base1 + "chemdner_cemp_gold_standard_train1.tsv",
                      'cem': cpatents_train_base1 + "chemdner_cemp_gold_standard_train1_eval.tsv",
                      'corpus': "data/chemdner_patents_train_text1.txt.pickle",
                      'format': "chemdner",
    },
    'cemp_train2':{
                      'text': cpatents_train_base2 + "chemdner_patents_train_text2.txt",
                      'annotations': cpatents_train_base2 + "chemdner_cemp_gold_standard_train2.tsv",
                      'cem': cpatents_train_base2 + "chemdner_cemp_gold_standard_train2_eval.tsv",
                      'corpus': "data/chemdner_patents_train_text2.txt.pickle",
                      'format': "chemdner",
    },
    'gpro_train':{
                    'text': gpro_train_base + "gpro_patents_train_text.txt",
                    'annotations': gpro_train_base + "chemdner_gpro_gold_standard_train_v02.tsv",
                    'cem': gpro_train_base + "chemdner_gpro_gold_standard_train_eval_v02.tsv",
                    'corpus': "data/gpro_patents_train_text.txt.pickle",
                    'format': "gpro",
    },
    'gpro_train1':{
                  'text': gpro_train_base1 + "gpro_patents_train_text1.txt",
                  'annotations': gpro_train_base1 + "chemdner_gpro_gold_standard_train1.tsv",
                  'cem': gpro_train_base1 + "chemdner_cemp_gold_standard_train1_eval.tsv",
                  'corpus': "data/gpro_patents_train_text1.txt.pickle",
                  'format': "gpro",
    },
    'gpro_train2':{
                      'text': gpro_train_base2 + "gpro_patents_train_text2.txt",
                      'annotations': gpro_train_base2 + "chemdner_gpro_gold_standard_train2.tsv",
                      'cem': gpro_train_base2 + "chemdner_cemp_gold_standard_train2_eval.tsv",
                      'corpus': "data/chemdner_patents_train_text2.txt.pickle",
                      'format': "gpro",
    },
    'cemp_dev':{
            'text': cemp_dev_base + "chemdner_patents_development_text.txt",
            'annotations': cemp_dev_base + "chemdner_cemp_gold_standard_development_v03.tsv",
            'cem': cemp_dev_base + "chemdner_cemp_gold_standard_development_eval_v03.tsv",
            'corpus': "data/chemdner_patents_development_text.txt.pickle",
            'format': "chemdner",
    },
    'cemp_test':{
            'text': cemp_test_base + "chemdner_patents_test_background_text_release.txt",
            'annotations': cemp_test_base + "chemdner_patents_test_background_text_release.txt",
            #'cem': cemp_dev_base + "chemdner_cemp_gold_standard_development_eval_v02.tsv",
            'corpus': "data/chemdner_patents_test_background_text_release.txt.pickle",
            'format': "chemdner",
    },
    'cemp_test_divide':{
        'text': cemp_test_base + "chemdner_patents_test_background_text_release.txt",
        'annotations': cemp_test_base + "chemdner_patents_test_background_text_release.txt",
        #'cem': cemp_dev_base + "chemdner_cemp_gold_standard_development_eval_v02.tsv",
        'corpus': "data/chemdner_patents_test_background_text_release.txt.pickle",
        'format': "chemdner",
    },
    'gpro_test':{
            'text': gpro_test_base + "chemdner_patents_test_background_text_release.txt",
            'annotations': cemp_test_base + "chemdner_patents_test_background_text_release.txt",
            #'cem': cemp_dev_base + "chemdner_cemp_gold_standard_development_eval_v02.tsv",
            'corpus': "data/chemdner_patents_test_background_text_release.txt.pickle",
            'format': "chemdner",
    },
    'gpro_dev':{
            'text': gpro_dev_base + "gpro_patents_development_text.txt",
            'annotations': gpro_dev_base + "chemdner_gpro_gold_standard_development.tsv",
            'cem': gpro_dev_base + "chemdner_gpro_gold_standard_development_eval.tsv",
            'corpus': "data/gpro_patents_development_text.txt.pickle",
            'format': "gpro",
    },
    'ddi_trainall':{
        'text': ddi_train_base,
        'annotations': ddi_train_base,
        'corpus': "data/ddi_trainall.txt.pickle",
        'format': "ddi",
    },
    'ddi_smalltest':{
        'text': ddi_smalltest_base,
        'annotations': ddi_smalltest_base,
        'corpus': "data/ddi_smalltest.txt.pickle",
        'format': "ddi",
    },
    'chebi_patents': {
        'text': chebi_patents_base,
        'annotations': chebi_patents_base,
        'corpus': "data/chebi_patents.txt.pickle",
        'format': "chebi"
    }

}

for i in range(10):
    paths["cemp_test" + str(i)] = {"format": "chemdner"}
    paths["cemp_test" + str(i)]["corpus"] = "data/chemdner_patents_test_background_text_release{}.txt.pickle".format(str(i))
    paths["cemp_test" + str(i)]["annotations"] = "data/chemdner_patents_test_background_text_release{}.txt.pickle".format(str(i))