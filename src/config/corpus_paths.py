chemdner_sample_base = "corpora/CHEMDNER/CHEMDNER_SAMPLE_JUNE25/"
cpatents_sample_base = "corpora/CHEMDNER-patents/chemdner_cemp_sample_v02/"
pubmed_test_base = "corpora/pubmed-test/"
transmir_base = "corpora/transmir/"
chemdner2017_base = "corpora/CHEMDNER2017/"
chemdner2017_1k = "corpora/CHEMDNER2017_1k/"
paths = {}
for i in range(1,11):
    paths["mirna_ds{}".format(i)] = {'corpus': "corpora/mirna-ds/abstracts_11k.txt_{}.pickle".format(i),
                                    'format': "mirna",
                                    'annotations': ""}
    paths["mirna_ds_annotated{}".format(i)] = {'corpus': "data/mirna_ds_annotated_{}.pickle".format(i),
                                               'format': "mirna",
                                               'annotations': ""
                                              }
paths.update({
    'mirna_cf': {
        'corpus': "corpora/cf_corpus/abstracts.txt.pickle",
        'format': "mirna",
        'annotations': ""
    },
    'mirna_cf_annotated': {
        'corpus': "data/mirna_cf_annotated.pickle",
        'format': "mirna",
        'annotations': ""
    },

    'mirna_ds': {
        'corpus': "corpora/mirna-ds/abstracts_11k.txt.pickle",
        'format': "mirna",
        'annotations': ""
    },
    'mirna_ds_annotated': {
        'corpus': "corpora/mirna-ds/mirna_ds_annotated.pickle",
        'format': "mirna",
        'annotations': ""
    },

    ### TransmiR corpus
    'transmir': {
        'text': "data/transmir_v1.2.tsv",
        'annotations': "data/transmir_v1.2.tsv",
        'corpus': "data/transmir_v1.2.tsv.pickle",
        'format': "transmir"
    },
    'transmir_annotated': {
        'text': "data/transmir_v1.2.tsv",
        'annotations': "data/transmir_v1.2.tsv",
        'corpus': "data/transmir_annotated.pickle",
        'format': "transmir"
    },
    'pubmed_test': {
        'text': pubmed_test_base + "pmids_test.txt",
        'annotations': "",
        'corpus': "data/pmids_test.txt.pickle",
        'format': "pubmed"
    },

    ### BioCreative '15 CHEMDNER subtask
    'cemp_sample':{
                    'text': cpatents_sample_base + "chemdner_patents_sample_text.txt",
                    'annotations': cpatents_sample_base + "chemdner_cemp_gold_standard_sample.tsv",
                    'cem': cpatents_sample_base + "chemdner_cemp_gold_standard_sample_eval.tsv",
                    'corpus': "data/chemdner_patents_sample_text.txt.pickle",
                    'format': "chemdner",
                    },

    'chemdner2017':{
                    'text': chemdner2017_base + "BioCreative V.5 training set.txt",
                    'annotations': chemdner2017_base + "CEMP_BioCreative V.5 training set annot.tsv",
                    #'cem': chemdner2017 + "chemdner_cemp_gold_standard_sample_eval.tsv",
                    'corpus': "data/chemdner_v5_text.txt.pickle",
                    'format': "chemdner",
                    },
    'chemdner2017_train':{
                    'text': chemdner2017_base + "chemdner2017_training_set.tsv",
                    'annotations': chemdner2017_base + "train_annotations.tsv",
                    #'cem': chemdner2017 + "chemdner_cemp_gold_standard_sample_eval.tsv",
                    'corpus': "data/chemdner_train_text.txt.pickle",
                    'format': "chemdner",
                    },
    'chemdner2017_dev': {
        'text': chemdner2017_base + "chemdner2017_development_set.tsv",
        'annotations': chemdner2017_base + "dev_annotations.tsv",
        # 'cem': chemdner2017 + "chemdner_cemp_gold_standard_sample_eval.tsv",
        'corpus': "data/chemdner_dev_text.txt.pickle",
        'format': "chemdner",
    },
    'chemdner2017_dev_ensemble': {
        'text': chemdner2017_base + "chemdner2017_development_set.tsv",
        'annotations': chemdner2017_base + "dev_annotations.tsv",
        # 'cem': chemdner2017 + "chemdner_cemp_gold_standard_sample_eval.tsv",
        'corpus': "data/chemdner_dev_ensemble.pickle",
        'format': "chemdner",
    },
    'chemdner2017_eval': {
        'text': chemdner2017_base + "chemdner2017_eval_set.tsv",
        'annotations': chemdner2017_base + "eval_annotations.tsv",
        'cem': chemdner2017_base + "eval_annotations.tsv",
        'corpus': "data/chemdner_eval_text.txt.pickle",
        'format': "chemdner",
    },
    'chemdner2017_eval_ensemble': {
        'text': chemdner2017_base + "chemdner2017_eval_set.tsv",
        'annotations': chemdner2017_base + "eval_annotations.tsv",
        'cem': chemdner2017_base + "eval_annotations.tsv",
        'corpus': "data/chemdner_eval_ensemble.pickle",
        'format': "chemdner",
    },
    'chemdner2017_test':{
                    'text': chemdner2017_base + "test_set_patents_BioCreative_V.5.tsv",
                    'annotations': "",
                    #'cem': chemdner2017 + "chemdner_cemp_gold_standard_sample_eval.tsv",
                    'corpus': "data/chemdner_test_text.txt.pickle",
                    'format': "chemdner",
                    },
})