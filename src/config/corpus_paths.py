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
bc2gn_base = "corpora/BC2GN/"
lll_base = "corpora/LLL/"
paths = {

    'mirna_ds':{
        'corpus': "corpora/mirna-ds/abstracts.txt_3.pickle",
        'format': "mirna",
        'annotations': ""
    },
    'mirna_ds_annotated': {
        'corpus': "corpora/mirna-ds/abstracts_annotated.pickle",
        'format': "mirna",
        'annotations': ""
    },
    'mirna_ds_annotated_10k': {
        'corpus': "corpora/mirna-ds/abstracts_annotated_10k.pickle",
        'format': "mirna",
        'annotations': ""
    },

    ### LLL ###
    'lll_train':{
       'text': lll_base + "genic_interaction_data.txt",
       'annotations': lll_base + "genic_interaction_data.txt",
       'corpus': "data/LLL-train.pickle",
        'format': "lll"
    },
    'lll_test': {
        'text': lll_base + "basic_test_data.txt",
        'annotations': lll_base + "basic_test_data.txt",
        'corpus': "data/LLL-test.pickle",
        'format': "lll"
    },

    ### BioInfer ###
    'bioinfer': {
        'text': "corpora/BioInfer/BioInfer_corpus_1.1.1.xml",
        'annotations': "corpora/BioInfer/BioInfer_corpus_1.1.1.xml",
        'corpus': "data/bioinfer.pickle",
        'format': "bioinfer"
    },

    ### AIMed ###
    'aimed_proteins': {
        'text': "corpora/AIMed/proteins",
        'annotations': "corpora/AIMed/proteins",
        'corpus': "data/aimed.pickle",
        'format': "aimed"
    },

    ### BioCreative 2 Gene mention subtask
    'bc2gm_train': {
        'text': bc2gn_base + "bc2geneMention/train/train.in",
        'annotations': bc2gn_base + "bc2geneMention/train/GENE.eval",
        'corpus': "data/BC2GM-train.pickle",
        'format': "bc2"
    },
    'bc2gm_test': {
        'text': bc2gn_base + "BC2GM/test/test.in",
        'annotations': bc2gn_base + "BC2GM/test/GENE.eval",
        'corpus': "data/BC2GM-test.pickle",
        'format': "bc2"
    },

    ### BioNLP/NLPBA 2004 (GENIA version 3.02)
    'jnlpba_train':{
        'text': jnlpba_base + "train/Genia4ERtask2.iob2",
        'annotations': jnlpba_base + "train/Genia4ERtask2.iob2",
        'corpus': "data/Genia4ERtask1.raw.pickle",
        'format': "jnlpba"
    },
    'jnlpba_test':{
        'text': jnlpba_base + "test/Genia4EReval2.iob2",
        'annotations': jnlpba_base + "test/Genia4EReval2.iob2",
        'corpus': "data/Genia4EReval1.raw.pickle",
        'format': "jnlpba"
    },

    ### miRNA corpus (Bagewadi 2013)
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

    ### miRTex corpus (Li 2015)
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

    ### TransmiR corpus
    'transmir_tfs':{
        'text': transmir_base + "transmir_pmids.txt",
        'annotations': transmir_base + "transmir_tfs.txt",
        'corpus': "data/transmir_pmids.txt.pickle",
        'format': "pubmed"
    },
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

    ### GENIA
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


                #################################
                ####### Past Competitions #######
                #################################

    ### BioNLP '16 - Seedev-binary subtask
    'seedev_test': {
        'text': seedev_base + "BioNLP-ST-2016_SeeDev-binary_test/",
        'annotations': seedev_base + "BioNLP-ST-2016_SeeDev-binary_test/",
        'corpus': "data/SeeDev-test.txt.pickle",
        'format': "seedev"
    },
    'seedev_extended': {
        'corpus': "corpora/Thaliana/seedev-extended.pickle",
        'format': 'seedev'
    },
    'seedev_train': {
        'text': seedev_base + "BioNLP-ST-2016_SeeDev-binary_train/",
        'annotations': seedev_base + "BioNLP-ST-2016_SeeDev-binary_train/",
        'corpus': "data/SeeDev-train.txt.pickle",
        'format': "seedev"
    },
    'seedev_dev': {
        'text': seedev_base + "BioNLP-ST-2016_SeeDev-binary_dev/",
        'annotations': seedev_base + "BioNLP-ST-2016_SeeDev-binary_dev/",
        'corpus': "data/SeeDev-dev.txt.pickle",
        'format': "seedev"
    },
    'seedev_traindev': {
        'corpus': "data/SeeDev-traindev.txt.pickle",
        'format': "seedev"
    },
    'seedev_ds': {
        'corpus': "data/thaliana-documents_1.pickle",
        'format': "seedev"
    },

    ### Semeval '16 Task 12 Clinical TempEval
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

    ### BioCreative '13 CHEMDNER subtask
    'chemdner_sample': {
                         'text': chemdner_sample_base + "chemdner_sample_abstracts.txt",
                         'annotations': chemdner_sample_base + "chemdner_sample_annotations.txt",
                         'cem': chemdner_sample_base + "chemdner_sample_cem_gold_standard.txt",
                         'cdi': chemdner_sample_base + "chemdner_sample_cdi_gold_standard.txt",
                         'corpus': "data/chemdner_sample_abstracts.txt.pickle",
                         'format': "chemdner",
                         },

    ### BioCreative '15 CHEMDNER subtask
    'cemp_sample':{
                    'text': cpatents_sample_base + "chemdner_patents_sample_text.txt",
                    'annotations': cpatents_sample_base + "chemdner_cemp_gold_standard_sample.tsv",
                    'cem': cpatents_sample_base + "chemdner_cemp_gold_standard_sample_eval.tsv",
                    'corpus': "data/chemdner_patents_sample_text.txt.pickle",
                    'format': "chemdner",
                    },
    'gpro_dev':{
                 'text': gpro_dev_base + "gpro_patents_development_text.txt",
                 'annotations': gpro_dev_base + "chemdner_gpro_gold_standard_development.tsv",
                 'cem': gpro_dev_base + "chemdner_gpro_gold_standard_development_eval.tsv",
                 'corpus': "data/gpro_patents_development_text.txt.pickle",
                 'format': "gpro",
                 },

    ### Semeval '13 DDI subtask
    'ddi_trainall':{
                     'text': ddi_train_base,
                     'annotations': ddi_train_base,
                     'corpus': "data/ddi_trainall.txt.pickle",
                     'format': "ddi",
                     },
}