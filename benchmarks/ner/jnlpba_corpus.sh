#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

python src/main.py load_corpus --goldstd jnlpba_train --log $LOGLEVEL --entitytype protein
python src/main.py load_corpus --goldstd jnlpba_test --log $LOGLEVEL --entitytype protein
python src/main.py annotate --goldstd jnlpba_train --log $LOGLEVEL --entitytype protein
python src/main.py train --goldstd jnlpba_train --log $LOGLEVEL --entitytype protein --models models/jnlpba_train_protein #--crf crfsuite
python src/main.py test --goldstd jnlpba_test --log $LOGLEVEL --entitytype protein --models models/jnlpba_train_protein -o pickle results/jnlpbatrain_on_jnlpbatest_protein #--crf crfsuite
python src/evaluate.py evaluate jnlpba_test --results results/jnlpbatrain_on_jnlpbatest_protein --models models/jnlpba_train_protein --entitytype protein
