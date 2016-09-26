#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

# Load test corpora
#python src/main.py load_corpus --goldstd jnlpba_test --log $LOGLEVEL --entitytype protein
#python src/main.py load_corpus --goldstd bc2gm_test --log $LOGLEVEL --entitytype protein
#python src/main.py load_corpus --goldstd lll_test --log $LOGLEVEL --entitytype protein

#python src/main.py test --goldstd jnlpba_test --log $LOGLEVEL --entitytype protein --models models/bc2gm_train_protein_crfsuite -o pickle results/bc2gmtrain_on_jnlpbatest_crfsuite --crf crfsuite
#python src/evaluate.py evaluate jnlpba_test --results results/bc2gmtrain_on_jnlpbatest_crfsuite --models models/bc2gm_train_protein_crfsuite --entitytype protein
#
#python src/main.py test --goldstd jnlpba_test --log $LOGLEVEL --entitytype protein --models models/bc2gm_train_protein_sner -o pickle results/bc2gmtrain_on_jnlpbatest_sner --crf stanford
#python src/evaluate.py evaluate jnlpba_test --results results/bc2gmtrain_on_jnlpbatest_sner --models models/bc2gm_train_protein_sner --entitytype protein

#python src/main.py test --goldstd jnlpba_test --log $LOGLEVEL --entitytype protein --models models/aimed_protein_crfsuite -o pickle results/aimed_on_jnlpbatest_crfsuite --crf crfsuite
#python src/evaluate.py evaluate jnlpba_test --results results/aimed_on_jnlpbatest_crfsuite --models models/aimed_protein_crfsuite --entitytype protein

#python src/main.py test --goldstd jnlpba_test --log $LOGLEVEL --entitytype protein --models models/aimed_protein_sner -o pickle results/aimed_on_jnlpbatest_sner --crf stanford
#python src/evaluate.py evaluate jnlpba_test --results results/aimed_on_jnlpbatest_sner --models models/aimed_protein_sner --entitytype protein

#python src/main.py test --goldstd jnlpba_test --log $LOGLEVEL --entitytype protein --models models/jnlpba_train_protein_crfsuite -o pickle results/jnlpbatrain_on_jnlpbatest_crfsuite --crf crfsuite
#python src/evaluate.py evaluate jnlpba_test --results results/jnlpbatrain_on_jnlpbatest_crfsuite --models models/jnlpba_train_protein_crfsuite --entitytype protein
#
#python src/main.py test --goldstd jnlpba_test --log $LOGLEVEL --entitytype protein --models models/jnlpba_train_protein_sner -o pickle results/jnlpbatrain_on_jnlpbatest_sner --crf stanford
#python src/evaluate.py evaluate jnlpba_test --results results/jnlpbatrain_on_jnlpbatest_sner --models models/jnlpba_train_protein_sner --entitytype protein

#python src/main.py test --goldstd jnlpba_test --log $LOGLEVEL --entitytype protein --models models/lll_train_protein_crfsuite -o pickle results/llltrain_on_jnlpbatest_crfsuite --crf crfsuite
#python src/evaluate.py evaluate jnlpba_test --results results/llltrain_on_jnlpbatest_crfsuite --models models/lll_train_protein_crfsuite --entitytype protein

#python src/main.py test --goldstd jnlpba_test --log $LOGLEVEL --entitytype protein --models models/lll_train_protein_sner -o pickle results/llltrain_on_jnlpbatest_sner --crf stanford
#python src/evaluate.py evaluate jnlpba_test --results results/llltrain_on_jnlpbatest_sner --models models/lll_train_protein_sner --entitytype protein

python src/main.py test --goldstd jnlpba_test --log $LOGLEVEL --entitytype protein --models models/banner -o pickle results/banner_on_jnlpbatest --crf banner
python src/evaluate.py evaluate jnlpba_test --results results/banner_on_jnlpbatest --models models/banner --entitytype protein


python src/evaluate.py combine jnlpba_test --log $LOGLEVEL --entitytype protein --models results/combined_jnlpba_test \
                                                                                --results results/jnlpbatrain_on_jnlpbatest_sner \
                                                                                          results/jnlpbatrain_on_jnlpbatest_crfsuite \
                                                                                          results/banner_on_jnlpbatest

python src/evaluate.py evaluate jnlpba_test  --log $LOGLEVEL --entitytype protein --models combined --results results/combined_jnlpba_test
python src/normalize.py protein jnlpba_test  --log $LOGLEVEL --models combined --results results/combined_jnlpba_test
python src/evaluate.py evaluate jnlpba_test  --log $LOGLEVEL --entitytype protein --models combined --results results/combined_jnlpba_test --rules uniprot
python src/evaluate.py combine jnlpba_test --log $LOGLEVEL --entitytype protein --models results/combined_jnlpba_test \
                                                                                --results results/jnlpbatrain_on_jnlpbatest_sner \
                                                                                          results/jnlpbatrain_on_jnlpbatest_crfsuite \
                                                                                          results/bc2gmtrain_on_jnlpbatest_sner \
                                                                                          results/bc2gmtrain_on_jnlpbatest_crfsuite \
                                                                                          results/banner_on_jnlpbatest
                                                                                          #results/aimed_on_jnlpbatest_crfsuite \
                                                                                          #results/aimed_on_jnlpbatest_sner

python src/normalize.py protein jnlpba_test  --log $LOGLEVEL --models combined --results results/combined_jnlpba_test
#python src/normalize.py ssm jnlpba_test  --log $LOGLEVEL --models combined --results results/combined_jnlpba_test --measure simui_go
python src/evaluate.py evaluate jnlpba_test  --log $LOGLEVEL --entitytype protein --models combined --results results/combined_jnlpba_test
python src/evaluate.py evaluate jnlpba_test  --log $LOGLEVEL --entitytype protein --models combined --results results/combined_jnlpba_test --rules uniprot
#python src/evaluate.py evaluate jnlpba_test --log $LOGLEVEL --entitytype protein --models combined --results results/combined_jnlpba_test --rules uniprot --ssm 0.01


