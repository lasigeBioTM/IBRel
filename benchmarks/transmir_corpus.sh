#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

#python src/main.py load_corpus --goldstd miRNACorpus_train --log DEBUG --entitytype mirna
#python src/main.py load_corpus --goldstd miRNACorpus_test --log DEBUG --entitytype mirna
python src/main.py load_corpus --goldstd transmir --log $LOGLEVEL --entitytype mirna
#python src/main.py train --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype mirna --models models/mirtex_dev_mirna # --crf crfsuite
python src/main.py test --goldstd transmir --log $LOGLEVEL --entitytype mirna --models models/mirtex_dev_mirna -o pickle results/mirtexdev_on_transmir_mirna #--crf crfsuite
python src/evaluate.py evaluate_list transmir --results results/mirtexdev_on_transmir_mirna --models models/mirtex_dev_mirna

python src/main.py test --goldstd transmir --log $LOGLEVEL --entitytype mirna --models models/mirna_train_mirna -o pickle results/mirnatrain_on_transmir_mirna #--crf crfsuite
python src/evaluate.py evaluate_list transmir --results results/mirnatrain_on_transmir_mirna --models models/mirna_train_mirna
