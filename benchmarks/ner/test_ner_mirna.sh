#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

# Load test corpora
#python src/main.py load_corpus --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype all
#python src/main.py load_corpus --goldstd miRTex_test --log $LOGLEVEL --entitytype all


#python src/main.py test --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype mirna --models models/mirna_train_mirna_crfsuite -o pickle results/mirnatrain_on_mirnatest_crfsuite --crf crfsuite
#python src/evaluate.py evaluate miRNACorpus_test --results results/mirnatrain_on_mirnatest_crfsuite --models models/mirna_train_mirna_crfsuite --entitytype mirna
#
#python src/main.py test --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype mirna --models models/mirna_train_mirna_sner -o pickle results/mirnatrain_on_mirnatest_sner --crf stanford
#python src/evaluate.py evaluate miRNACorpus_test --results results/mirnatrain_on_mirnatest_sner --models models/mirna_train_mirna_sner --entitytype mirna
#
#python src/main.py test --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype mirna --models models/mirtex_train_mirna_crfsuite -o pickle results/mirtextrain_on_mirnatest_crfsuite --crf crfsuite
#python src/evaluate.py evaluate miRNACorpus_test --results results/mirtextrain_on_mirnatest_crfsuite --models models/mirtex_train_mirna_crfsuite --entitytype mirna
#
#python src/main.py test --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype mirna --models models/mirtex_train_mirna_sner -o pickle results/mirtextrain_on_mirnatest_sner --crf stanford
#python src/evaluate.py evaluate miRNACorpus_test --results results/mirtextrain_on_mirnatest_sner --models models/mirtex_train_mirna_sner --entitytype mirna

python src/evaluate.py combine miRNACorpus_test --log $LOGLEVEL --entitytype mirna --models results/combined_mirna_test \
                                                                                --results results/mirnatrain_on_mirnatest_sner \
                                                                                          results/mirnatrain_on_mirnatest_crfsuite
python src/evaluate.py evaluate miRNACorpus_test  --log $LOGLEVEL --entitytype mirna --models combined --results results/combined_mirna_test
#python src/normalize.py protein jnlpba_test  --log $LOGLEVEL --models combined --results results/combined_jnlpba_test
#python src/evaluate.py evaluate jnlpba_test  --log $LOGLEVEL --entitytype protein --models combined --results results/combined_jnlpba_test --rules uniprot
python src/evaluate.py combine miRNACorpus_test --log $LOGLEVEL --entitytype mirna --models results/combined_mirna_test \
                                                                                --results results/mirnatrain_on_mirnatest_sner \
                                                                                          results/mirnatrain_on_mirnatest_crfsuite \
                                                                                          results/mirtextrain_on_mirnatest_crfsuite \
                                                                                          results/mirtextrain_on_mirnatest_sner
python src/evaluate.py evaluate miRNACorpus_test  --log $LOGLEVEL --entitytype mirna --models combined --results results/combined_mirna_test

#python src/normalize.py protein jnlpba_test  --log $LOGLEVEL --models combined --results results/combined_jnlpba_test
##python src/normalize.py ssm jnlpba_test  --log $LOGLEVEL --models combined --results results/combined_jnlpba_test --measure simui_go
#python src/evaluate.py evaluate jnlpba_test  --log $LOGLEVEL --entitytype protein --models combined --results results/combined_jnlpba_test
#python src/evaluate.py evaluate jnlpba_test  --log $LOGLEVEL --entitytype protein --models combined --results results/combined_jnlpba_test --rules uniprot
##python src/evaluate.py evaluate jnlpba_test --log $LOGLEVEL --entitytype protein --models combined --results results/combined_jnlpba_test --rules uniprot --ssm 0.01
#
#
