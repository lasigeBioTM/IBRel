#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

# Load test corpora
#python src/main.py load_corpus --goldstd jnlpba_test --log $LOGLEVEL --entitytype protein
#python src/main.py load_corpus --goldstd bc2gm_test --log $LOGLEVEL --entitytype protein
#python src/main.py load_corpus --goldstd lll_test --log $LOGLEVEL --entitytype protein

#python src/main.py test --goldstd jnlpba_test --log $LOGLEVEL --entitytype protein --models models/bc2gm_train_protein_crfsuite -o pickle results/bc2gmtrain_on_jnlpbatest_crfsuite --crf crfsuite
#python src/evaluate.py evaluate jnlpba_test --results results/bc2gmtrain_on_jnlpbatest_crfsuite --models models/bc2gm_train_protein_crfsuite --entitytype protein

#python src/main.py test --goldstd jnlpba_test --log $LOGLEVEL --entitytype protein --models models/bc2gm_train_protein_sner -o pickle results/bc2gmtrain_on_jnlpbatest_sner --crf stanford
#python src/evaluate.py evaluate jnlpba_test --results results/bc2gmtrain_on_jnlpbatest_sner --models models/bc2gm_train_protein_sner --entitytype protein

#python src/main.py test --goldstd jnlpba_test --log $LOGLEVEL --entitytype protein --models models/aimed_protein_crfsuite -o pickle results/aimed_on_jnlpbatest_crfsuite --crf crfsuite
#python src/evaluate.py evaluate jnlpba_test --results results/aimed_on_jnlpbatest_crfsuite --models models/aimed_protein_crfsuite --entitytype protein

#python src/main.py test --goldstd jnlpba_test --log $LOGLEVEL --entitytype protein --models models/aimed_protein_sner -o pickle results/aimed_on_jnlpbatest_sner --crf stanford
#python src/evaluate.py evaluate jnlpba_test --results results/aimed_on_jnlpbatest_sner --models models/aimed_protein_sner --entitytype protein

#python src/main.py test --goldstd jnlpba_test --log $LOGLEVEL --entitytype protein --models models/jnlpba_train_protein_crfsuite -o pickle results/jnlptrain_on_jnlpbatest_crfsuite --crf crfsuite
#python src/evaluate.py evaluate jnlpba_test --results results/jnlptrain_on_jnlpbatest_crfsuite --models models/jnlpba_train_protein_crfsuite --entitytype protein

#python src/main.py test --goldstd jnlpba_test --log $LOGLEVEL --entitytype protein --models models/jnlpba_train_protein_sner -o pickle results/jnlpbatrain_on_jnlpbatest_sner --crf stanford
#python src/evaluate.py evaluate jnlpba_test --results results/jnlpbatrain_on_jnlpbatest_sner --models models/jnlpba_train_protein_sner --entitytype protein

python src/evaluate.py combine jnlpba_test --log $LOGLEVEL --entitytype protein --models results/combined_jnlpba_test --results results/aimed_on_jnlpbatest_sner \
                                                                                                                                                  results/jnlptrain_on_jnlpbatest_crfsuite \
                                                                                                                                                  results/aimed_on_jnlpbatest_crfsuite \
                                                                                                                                                  results/aimed_on_jnlpbatest_sner \
                                                                                                                                                  results/bc2gmtrain_on_jnlpbatest_sner \
                                                                                                                                                  results/bc2gmtrain_on_jnlpbatest_crfsuite
python src/evaluate.py evaluate jnlpba_test  --log $LOGLEVEL --entitytype protein --models combined --results results/combined_jnlpba_test