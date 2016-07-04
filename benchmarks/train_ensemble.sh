#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

# Load test corpora
#python src/main.py load_corpus --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype protein
#python src/main.py load_corpus --goldstd lll_test --log $LOGLEVEL --entitytype protein

python src/main.py test --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype protein --models models/mirna_train_protein_crfsuite -o pickle results/mirnatrainprotein_on_mirnatrain_crfsuite --crf crfsuite
python src/evaluate.py evaluate miRNACorpus_train --results results/mirnatrainprotein_on_mirnatrain_crfsuite --models models/mirna_train_protein_crfsuite --entitytype protein
##
python src/main.py test --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype protein --models models/mirna_train_protein_sner -o pickle results/mirnatrainprotein_on_mirnatrain_sner --crf stanford
python src/evaluate.py evaluate miRNACorpus_train --results results/mirnatrainprotein_on_mirnatrain_sner --models models/mirna_train_protein_sner --entitytype protein
#
##
#python src/main.py test --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype protein --models models/bc2gm_train_protein_crfsuite -o pickle results/bc2gmtrain_on_mirnatrain_crfsuite --crf crfsuite
#python src/evaluate.py evaluate miRNACorpus_train --results results/bc2gmtrain_on_mirnatrain_crfsuite --models models/bc2gm_train_protein_crfsuite --entitytype protein
##
#python src/main.py test --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype protein --models models/bc2gm_train_protein_sner -o pickle results/bc2gmtrain_on_mirnatrain_sner --crf stanford
#python src/evaluate.py evaluate miRNACorpus_train --results results/bc2gmtrain_on_mirnatrain_sner --models models/bc2gm_train_protein_sner --entitytype protein
##
#python src/main.py test --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype protein --models models/jnlpba_train_protein_crfsuite -o pickle results/jnlpbatrain_on_mirnatrain_crfsuite --crf crfsuite
#python src/evaluate.py evaluate miRNACorpus_train --results results/jnlpbatrain_on_mirnatrain_crfsuite --models models/jnlpba_train_protein_crfsuite --entitytype protein
##
#python src/main.py test --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype protein --models models/jnlpba_train_protein_sner -o pickle results/jnlpbatrain_on_mirnatrain_sner --crf stanford
#python src/evaluate.py evaluate miRNACorpus_train --results results/jnlpbatrain_on_mirnatrain_sner --models models/jnlpba_train_protein_sner --entitytype protein
##
#python src/main.py test --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype protein --models models/banner -o pickle results/banner_on_mirnatrain --crf banner
#python src/evaluate.py evaluate miRNACorpus_train --results results/banner_on_mirnatrain --models models/banner --entitytype protein



python src/evaluate.py train_ensemble miRNACorpus_train --log $LOGLEVEL --entitytype protein --models mirnatrain_ensemble \
                                                                                --results results/banner_on_mirnatrain \
                                                                                          results/jnlpbatrain_on_mirnatrain_crfsuite \
                                                                                          results/jnlpbatrain_on_mirnatrain_sner \
                                                                                          results/bc2gmtrain_on_mirnatrain_sner \
                                                                                          results/bc2gmtrain_on_mirnatrain_crfsuite \
                                                                                          results/mirnatrainprotein_on_mirnatrain_crfsuite \
                                                                                          results/mirnatrainprotein_on_mirnatrain_sner


#python src/main.py test --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype protein --models models/bc2gm_train_protein_crfsuite -o pickle results/bc2gmtrain_on_mirnatest_crfsuite --crf crfsuite
#python src/evaluate.py evaluate miRNACorpus_test --results results/bc2gmtrain_on_mirnatest_crfsuite --models models/bc2gm_train_protein_crfsuite --entitytype protein
##
#python src/main.py test --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype protein --models models/bc2gm_train_protein_sner -o pickle results/bc2gmtrain_on_mirnatest_sner --crf stanford
#python src/evaluate.py evaluate miRNACorpus_test --results results/bc2gmtrain_on_mirnatest_sner --models models/bc2gm_train_protein_sner --entitytype protein
##
#python src/main.py test --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype protein --models models/jnlpba_train_protein_crfsuite -o pickle results/jnlpbatrain_on_mirnatest_crfsuite --crf crfsuite
#python src/evaluate.py evaluate miRNACorpus_test --results results/jnlpbatrain_on_mirnatest_crfsuite --models models/jnlpba_train_protein_crfsuite --entitytype protein
##
#python src/main.py test --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype protein --models models/jnlpba_train_protein_sner -o pickle results/jnlpbatrain_on_mirnatest_sner --crf stanford
#python src/evaluate.py evaluate miRNACorpus_test --results results/jnlpbatrain_on_mirnatest_sner --models models/jnlpba_train_protein_sner --entitytype protein
##
#python src/main.py test --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype protein --models models/banner -o pickle results/banner_on_mirnatest --crf banner
#python src/evaluate.py evaluate miRNACorpus_test --results results/banner_on_mirnatest --models models/banner --entitytype protein

python src/main.py test --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype protein --models models/mirna_train_protein_crfsuite -o pickle results/mirnatrainprotein_on_mirnatest_crfsuite --crf crfsuite
python src/evaluate.py evaluate miRNACorpus_test --results results/mirnatrainprotein_on_mirnatest_crfsuite --models models/mirna_train_protein_crfsuite --entitytype protein
#
python src/main.py test --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype protein --models models/mirna_train_protein_sner -o pickle results/mirnatrainprotein_on_mirnatest_sner --crf stanford
python src/evaluate.py evaluate miRNACorpus_test --results results/mirnatrainprotein_on_mirnatest_sner --models models/mirna_train_protein_sner --entitytype protein


python src/evaluate.py test_ensemble miRNACorpus_test --log $LOGLEVEL --entitytype protein --models mirnatrain_ensemble \
                                                                        --results results/banner_on_mirnatest \
                                                                                  results/jnlpbatrain_on_mirnatest_crfsuite \
                                                                                  results/jnlpbatrain_on_mirnatest_sner \
                                                                                  results/bc2gmtrain_on_mirnatest_sner \
                                                                                  results/bc2gmtrain_on_mirnatest_crfsuite \
                                                                                  results/mirnatrainprotein_on_mirnatest_crfsuite \
                                                                                  results/mirnatrainprotein_on_mirnatest_sner

python src/evaluate.py evaluate miRNACorpus_test  --log $LOGLEVEL --entitytype protein --models mirnatrain_ensemble --results results/mirnatrain_ensemble


#python src/normalize.py protein miRNACorpus_test  --log $LOGLEVEL --models combined --results results/combined_miRNACorpus_test
#python src/normalize.py ssm miRNACorpus_test  --log $LOGLEVEL --models combined --results results/combined_miRNACorpus_test --measure resnik_go
# python src/evaluate.py evaluate miRNACorpus_test  --log $LOGLEVEL --entitytype protein --models combined --results results/combined_miRNACorpus_test
#python src/evaluate.py evaluate miRNACorpus_test  --log $LOGLEVEL --entitytype protein --models combined --results results/combined_miRNACorpus_test --rules uniprot
# python src/evaluate.py evaluate miRNACorpus_test --log $LOGLEVEL --entitytype protein --models combined --results results/combined_miRNACorpus_test --rules uniprot --ssm 0.1

#python src/evaluate.py test_ensemble miRNACorpus_test --log $LOGLEVEL --entitytype protein --models results/combined_miRNACorpus_test \
#                                                                                --results results/mirnatrainprotein_on_mirnatest_crfsuite \
#                                                                                          results/mirnatrainprotein_on_mirnatest_sner

