chemdner_sample_base = "corpora/CHEMDNER/CHEMDNER_SAMPLE_JUNE25/"
cpatents_sample_base = "corpora/CHEMDNER-patents/chemdner_cemp_sample_v02/"
pubmed_test_base = "corpora/pubmed-test/"
transmir_base = "corpora/transmir/"
chemdner2017_base = "corpora/CHEMDNER2017/"
chemdner2017_1k = "corpora/CHEMDNER2017_1k/"
mirnacorpus_base = "corpora/miRNACorpus/"
mirtex_base = "corpora/miRTex/"
jnlpba_base = "corpora/JNLPBA/"


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

    ### miRNA corpus (Bagewadi 2013)
    'miRNACorpus_train': {
        'text': mirnacorpus_base + "miRNA-Train-Corpus.xml",
        'annotations': mirnacorpus_base + "miRNA-Train-Corpus.xml",
        'corpus': "data/miRNA-Train-Corpus.xml.pickle",
        'format': "ddi-mirna"
    },
    'miRNACorpus_test': {
        'text': mirnacorpus_base + "miRNA-Test-Corpus.xml",
        'annotations': mirnacorpus_base + "miRNA-Test-Corpus.xml",
        'corpus': "data/miRNA-Test-Corpus.xml.pickle",
        'format': "ddi-mirna"
    },
    ### miRTex corpus (Li 2015)
    'miRTex_dev': {
        'text': mirtex_base + "development/",
        'annotations': mirtex_base + "development/",
        'corpus': "data/miRTex-development.txt.pickle",
        'format': "mirtex"
    },
    'miRTex_test': {
        'text': mirtex_base + "test/",
        'annotations': mirtex_base + "test/",
        'corpus': "data/miRTex-test.txt.pickle",
        'format': "mirtex"
    },
    'lurie_train': {
        'text': "corpora/luriechildren/train/texts/",
        'annotations': "corpora/luriechildren/train/annotations/",
        'corpus': "data/luriechildren_train.txt.pickle",
        'format': "brat"
    },
    'lurie_test': {
        'text': "corpora/luriechildren/test/texts/",
        'annotations': "corpora/luriechildren/test/annotations/",
        'corpus': "data/luriechildren_test.txt.pickle",
        'format': "brat"
    },
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

    ### BioNLP/NLPBA 2004 (GENIA version 3.02)
    'jnlpba_train': {
        'text': jnlpba_base + "train/Genia4ERtask2.iob2",
        'annotations': jnlpba_base + "train/Genia4ERtask2.iob2",
        'corpus': "data/Genia4ERtask1.raw.pickle",
        'format': "jnlpba"
    },
    'jnlpba_test': {
        'text': jnlpba_base + "test/Genia4EReval2.iob2",
        'annotations': jnlpba_base + "test/Genia4EReval2.iob2",
        'corpus': "data/Genia4EReval1.raw.pickle",
        'format': "jnlpba"
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
    'ensemble_chemdner_dev': {
        'text': chemdner2017_base + "chemdner2017_development_set.tsv",
        'annotations': chemdner2017_base + "dev_annotations.tsv",
        # 'cem': chemdner2017 + "chemdner_cemp_gold_standard_sample_eval.tsv",
        'corpus': "data/chemdner_dev_ensemble.pickle",
        'format': "chemdner",
    },
    'ensemble_chemdner_dev_ssm': {
        'text': chemdner2017_base + "chemdner2017_development_set.tsv",
        'annotations': chemdner2017_base + "dev_annotations.tsv",
        # 'cem': chemdner2017 + "chemdner_cemp_gold_standard_sample_eval.tsv",
        'corpus': "data/chemdner_dev_ensemble_ssm.pickle",
        'format': "chemdner",
    },
    'chemdner2017_eval': {
        'text': chemdner2017_base + "chemdner2017_eval_set.tsv",
        'annotations': chemdner2017_base + "eval_annotations.tsv",
        'cem': chemdner2017_base + "eval_annotations.tsv",
        'corpus': "data/chemdner_eval_text.txt.pickle",
        'format': "chemdner",
    },
    'ensemble_chemdner_eval': {
        'text': chemdner2017_base + "chemdner2017_eval_set.tsv",
        'annotations': chemdner2017_base + "eval_annotations.tsv",
        'cem': chemdner2017_base + "eval_annotations.tsv",
        'corpus': "data/chemdner_eval_ensemble.pickle",
        'format': "chemdner",
    },
    'ensemble_chemdner_eval_ssm': {
        'text': chemdner2017_base + "chemdner2017_eval_set.tsv",
        'annotations': chemdner2017_base + "eval_annotations.tsv",
        'cem': chemdner2017_base + "eval_annotations.tsv",
        'corpus': "data/chemdner_eval_ensemble_ssm.pickle",
        'format': "chemdner",
    },
    'chemdner2017_test':{
                    'text': chemdner2017_base + "test_set_patents_BioCreative_V.5.tsv",
                    'annotations': "",
                    #'cem': chemdner2017 + "chemdner_cemp_gold_standard_sample_eval.tsv",
                    'corpus': "data/chemdner_test_text.txt.pickle",
                    'format': "chemdner",
                    },
    'ensemble_chemdner_test': {
        'text': chemdner2017_base + "test_set_patents_BioCreative_V.5.tsv",
        'annotations': "",
        # 'cem': chemdner2017 + "chemdner_cemp_gold_standard_sample_eval.tsv",
        'corpus': "data/chemdner_test_ensemble.pickle",
        'format': "chemdner",
    },
    'ensemble_chemdner_test_ssm': {
        'text': chemdner2017_base + "test_set_patents_BioCreative_V.5.tsv",
        'annotations': "",
        # 'cem': chemdner2017 + "chemdner_cemp_gold_standard_sample_eval.tsv",
        'corpus': "data/chemdner_test_ensemble_ssm.pickle",
        'format': "chemdner",
    },
})