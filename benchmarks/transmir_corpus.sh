#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

#python src/main.py load_corpus --goldstd miRNACorpus_train --log DEBUG --entitytype mirna
#python src/main.py load_corpus --goldstd miRNACorpus_test --log DEBUG --entitytype mirna
# python src/main.py load_corpus --goldstd transmir --log $LOGLEVEL
#python src/main.py train --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype mirna --models models/mirtex_dev_mirna # --crf crfsuite
#python src/main.py test --goldstd transmir --log $LOGLEVEL --entitytype mirna --models models/mirtex_dev_mirna -o pickle results/mirtexdev_on_transmir_mirna # --crf crfsuite
#python src/evaluate.py evaluate_list transmir --results results/mirtexdev_on_transmir_mirna --models models/mirtex_dev_mirna --entitytype mirna --log $LOGLEVEL --rules separate_mirnas

python src/main.py test --goldstd transmir --log $LOGLEVEL --entitytype mirna --models models/mirna_train_mirna -o pickle results/mirnatrain_on_transmir_mirna --crf crfsuite
python src/evaluate.py evaluate_list transmir --results results/mirnatrain_on_transmir_mirna --models models/mirna_train_mirna --entitytype mirna --log $LOGLEVEL --rules separate_mirnas

python src/main.py test --goldstd transmir --log $LOGLEVEL --entitytype protein --models models/mirna_train_protein -o pickle results/mirnatrain_on_transmir_protein --crf crfsuite
python src/evaluate.py evaluate_list transmir --results results/mirnatrain_on_transmir_protein --models models/mirna_train_protein --entitytype protein --log $LOGLEVEL

python src/evaluate.py combine transmir  --log $LOGLEVEL --entitytype all --models results/mirna_train_transmir --results results/mirnatrain_on_transmir_mirna results/mirnatrain_on_transmir_protein
python src/normalize.py all transmir  --log $LOGLEVEL --models results/mirna_train_transmir --results results/mirna_train_transmir
python src/evaluate.py savetocorpus transmir --log $LOGLEVEL --results results/mirna_train_transmir --output data/transmir_annotated
