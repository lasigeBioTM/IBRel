#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

#python src/main.py load_corpus --goldstd jnlpba_train --log $LOGLEVEL --entitytype protein
#python src/main.py load_corpus --goldstd jnlpba_test --log $LOGLEVEL --entitytype protein
# python src/main.py annotate --goldstd jnlpba_train --log $LOGLEVEL --entitytype protein
#python src/main.py train --goldstd jnlpba_train --log $LOGLEVEL --entitytype protein --models models/jnlpba_train_protein_crfsuite --crf crfsuite
#python src/main.py test --goldstd jnlpba_test --log $LOGLEVEL --entitytype protein --models models/jnlpba_train_protein_crfsuite -o pickle results/jnlpbatrain_on_jnlpbatest_protein_crfsuite --crf crfsuite
#python src/evaluate.py evaluate jnlpba_test --results results/jnlpbatrain_on_jnlpbatest_protein_crfsuite --models models/jnlpba_train_protein_crfsuite --entitytype protein
#
python src/main.py train --goldstd jnlpba_train --log $LOGLEVEL --entitytype protein --models models/jnlpba_train_protein_sner
python src/main.py test --goldstd jnlpba_test --log $LOGLEVEL --entitytype protein --models models/jnlpba_train_protein_sner -o pickle results/jnlpbatrain_on_jnlpbatest_protein_sner
python src/evaluate.py evaluate jnlpba_test --results results/jnlpbatrain_on_jnlpbatest_protein_sner --models models/jnlpba_train_protein_sner --entitytype protein
#
#python src/classification/results.py combine jnlpba_test --entitytype protein --finalmodel models/jnlpba_train_protein_combined --results results/jnlpbatrain_on_jnlpbatest_protein_sner results/jnlpbatrain_on_jnlpbatest_protein_crfsuite -o results/jnlpbatrain_on_jnlpbatest_protein_combined --models models/jnlpba_train_protein_sner models/jnlpba_train_protein_crfsuite
#python src/evaluate.py evaluate jnlpba_test --results results/jnlpbatrain_on_jnlpbatest_protein_combined --models models/jnlpba_train_protein_combined --entitytype protein
#
#
#python src/main.py annotate --goldstd jnlpba_train --log $LOGLEVEL --entitytype DNA
#python src/main.py train --goldstd jnlpba_train --log $LOGLEVEL --entitytype DNA --models models/jnlpba_train_DNA_crfsuite --crf crfsuite
#python src/main.py test --goldstd jnlpba_test --log $LOGLEVEL --entitytype DNA --models models/jnlpba_train_DNA_crfsuite -o pickle results/jnlpbatrain_on_jnlpbatest_DNA_crfsuite --crf crfsuite
#python src/evaluate.py evaluate jnlpba_test --results results/jnlpbatrain_on_jnlpbatest_DNA_crfsuite --models models/jnlpba_train_DNA_crfsuite --entitytype DNA
#
#python src/main.py train --goldstd jnlpba_train --log $LOGLEVEL --entitytype DNA --models models/jnlpba_train_DNA_sner
#python src/main.py test --goldstd jnlpba_test --log $LOGLEVEL --entitytype DNA --models models/jnlpba_train_DNA_sner -o pickle results/jnlpbatrain_on_jnlpbatest_DNA_sner
#python src/evaluate.py evaluate jnlpba_test --results results/jnlpbatrain_on_jnlpbatest_DNA_sner --models models/jnlpba_train_DNA_sner --entitytype DNA
#
#python src/classification/results.py combine jnlpba_test --entitytype DNA --finalmodel models/jnlpba_train_DNA_combined --results results/jnlpbatrain_on_jnlpbatest_DNA_sner results/jnlpbatrain_on_jnlpbatest_DNA_crfsuite -o results/jnlpbatrain_on_jnlpbatest_DNA_combined --models models/jnlpba_train_DNA_sner models/jnlpba_train_DNA_crfsuite
#python src/evaluate.py evaluate jnlpba_test --results results/jnlpbatrain_on_jnlpbatest_DNA_combined --models models/jnlpba_train_DNA_combined --entitytype DNA
#
