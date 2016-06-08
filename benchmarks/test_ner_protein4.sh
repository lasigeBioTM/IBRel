#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

# Load test corpora
#python src/main.py load_corpus --goldstd miRTex_test --log $LOGLEVEL --entitytype protein
#python src/main.py load_corpus --goldstd lll_test --log $LOGLEVEL --entitytype protein

python src/main.py test --goldstd miRTex_test --log $LOGLEVEL --entitytype protein --models models/mirtex_train_protein_crfsuite -o pickle results/mirtextrainprotein_on_mirtextest_crfsuite --crf crfsuite
python src/evaluate.py evaluate miRTex_test --results results/mirtextrainprotein_on_mirtextest_crfsuite --models models/mirtex_train_protein_crfsuite --entitytype protein
#
python src/main.py test --goldstd miRTex_test --log $LOGLEVEL --entitytype protein --models models/mirtex_train_protein_sner -o pickle results/mirtextrainprotein_on_mirtextest_sner --crf stanford
python src/evaluate.py evaluate miRTex_test --results results/mirtextrainprotein_on_mirtextest_sner --models models/mirtex_train_protein_sner --entitytype protein
#
#
#python src/main.py test --goldstd miRTex_test --log $LOGLEVEL --entitytype protein --models models/bc2gm_train_protein_crfsuite -o pickle results/bc2gmtrain_on_mirtextest_crfsuite --crf crfsuite
#python src/evaluate.py evaluate miRTex_test --results results/bc2gmtrain_on_mirtextest_crfsuite --models models/bc2gm_train_protein_crfsuite --entitytype protein
##
#python src/main.py test --goldstd miRTex_test --log $LOGLEVEL --entitytype protein --models models/bc2gm_train_protein_sner -o pickle results/bc2gmtrain_on_mirtextest_sner --crf stanford
#python src/evaluate.py evaluate miRTex_test --results results/bc2gmtrain_on_mirtextest_sner --models models/bc2gm_train_protein_sner --entitytype protein
##
#python src/main.py test --goldstd miRTex_test --log $LOGLEVEL --entitytype protein --models models/jnlpba_train_protein_crfsuite -o pickle results/jnlpbatrain_on_mirtextest_crfsuite --crf crfsuite
#python src/evaluate.py evaluate miRTex_test --results results/jnlpbatrain_on_mirtextest_crfsuite --models models/jnlpba_train_protein_crfsuite --entitytype protein
##
#python src/main.py test --goldstd miRTex_test --log $LOGLEVEL --entitytype protein --models models/jnlpba_train_protein_sner -o pickle results/jnlpbatrain_on_mirtextest_sner --crf stanford
#python src/evaluate.py evaluate miRTex_test --results results/jnlpbatrain_on_mirtextest_sner --models models/jnlpba_train_protein_sner --entitytype protein
##
#python src/main.py test --goldstd miRTex_test --log $LOGLEVEL --entitytype protein --models models/banner -o pickle results/banner_on_mirtextest --crf banner
#python src/evaluate.py evaluate miRTex_test --results results/banner_on_mirtextest --models models/banner --entitytype protein

python src/evaluate.py combine miRTex_test --log $LOGLEVEL --entitytype protein --models results/combined_miRTex_test \
                                                                                --results results/mirtextrainprotein_on_mirtextest_crfsuite \
                                                                                          results/mirtextrainprotein_on_mirtextest_sner

python src/evaluate.py evaluate miRTex_test  --log $LOGLEVEL --entitytype protein --models combined --results results/combined_miRTex_test

python src/evaluate.py combine miRTex_test --log $LOGLEVEL --entitytype protein --models results/combined_miRTex_test \
                                                                                --results results/mirtextrainprotein_on_mirtextest_crfsuite \
                                                                                          results/mirtextrainprotein_on_mirtextest_sner \
                                                                                          results/banner_on_mirtextest
                                                                                          #results/jnlpbatrain_on_mirtextest_crfsuite \
                                                                                          #results/jnlpbatrain_on_mirtextest_sner
                                                                                          #results/bc2gmtrain_on_mirtextest_sner \
                                                                                          #results/bc2gmtrain_on_mirtextest_crfsuite \

python src/evaluate.py evaluate miRTex_test  --log $LOGLEVEL --entitytype protein --models combined --results results/combined_miRTex_test

python src/evaluate.py combine miRTex_test --log $LOGLEVEL --entitytype protein --models results/combined_miRTex_test \
                                                                                --results results/mirtextrainprotein_on_mirtextest_crfsuite \
                                                                                          results/mirtextrainprotein_on_mirtextest_sner \
                                                                                          results/banner_on_mirtextest \
                                                                                          results/jnlpbatrain_on_mirtextest_crfsuite \
                                                                                          results/jnlpbatrain_on_mirtextest_sner
                                                                                          results/bc2gmtrain_on_mirtextest_sner \
                                                                                          results/bc2gmtrain_on_mirtextest_crfsuite \

python src/evaluate.py evaluate miRTex_test  --log $LOGLEVEL --entitytype protein --models combined --results results/combined_miRTex_test


python src/normalize.py protein miRTex_test  --log $LOGLEVEL --models combined --results results/combined_miRTex_test
#python src/normalize.py ssm miRTex_test  --log $LOGLEVEL --models combined --results results/combined_miRTex_test --measure resnik_go
# python src/evaluate.py evaluate miRTex_test  --log $LOGLEVEL --entitytype protein --models combined --results results/combined_miRTex_test
python src/evaluate.py evaluate miRTex_test  --log $LOGLEVEL --entitytype protein --models combined --results results/combined_miRTex_test --rules uniprot
# python src/evaluate.py evaluate miRTex_test --log $LOGLEVEL --entitytype protein --models combined --results results/combined_miRTex_test --rules uniprot --ssm 0.1


