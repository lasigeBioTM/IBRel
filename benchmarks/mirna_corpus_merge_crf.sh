#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

python src/main.py annotate --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype mirna
python src/main.py train --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype mirna --models models/mirna_train_mirna  --crf crfsuite
python src/main.py test --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype mirna --models models/mirna_train_mirna -o pickle results/mirnatrain_on_mirnatest_mirna_crfsuite  --crf crfsuite
python src/evaluate.py evaluate miRNACorpus_test --results results/mirnatrain_on_mirnatest_mirna_crfsuite --models models/mirna_train_mirna --entitytype mirna
python src/main.py train --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype mirna --models models/mirna_train_mirna
python src/main.py test --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype mirna --models models/mirna_train_mirna -o pickle results/mirnatrain_on_mirnatest_mirna_sner
python src/evaluate.py evaluate miRNACorpus_test --results results/mirnatrain_on_mirnatest_mirna_sner --models models/mirna_train_mirna --entitytype mirna

python src/classification/results.py combine miRNACorpus_test --entitytype mirna --models models/mirna_train_mirna --results results/mirnatrain_on_mirnatest_mirna_sner results/mirnatrain_on_mirnatest_mirna_crfsuite -o results/mirnatrain_on_mirnatest_mirna_combined
python src/evaluate.py evaluate miRNACorpus_test --results results/mirnatrain_on_mirnatest_mirna_combined --models results/mirnatrain_on_mirnatest_mirna_combined --entitytype mirna


python src/main.py annotate --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype protein
python src/main.py train --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype protein --models models/mirna_train_protein  --crf crfsuite
python src/main.py test --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype protein --models models/mirna_train_protein -o pickle results/mirnatrain_on_mirnatest_protein_crfsuite  --crf crfsuite
python src/evaluate.py evaluate miRNACorpus_test --results results/mirnatrain_on_mirnatest_protein_crfsuite --models models/mirna_train_protein --entitytype protein
python src/main.py train --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype protein --models models/mirna_train_protein
python src/main.py test --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype protein --models models/mirna_train_protein -o pickle results/mirnatrain_on_mirnatest_protein_sner
python src/evaluate.py evaluate miRNACorpus_test --results results/mirnatrain_on_mirnatest_protein_sner --models models/mirna_train_protein --entitytype protein

python src/classification/results.py combine miRNACorpus_test --entitytype protein --models models/mirna_train_protein --results results/mirnatrain_on_mirnatest_protein_sner results/mirnatrain_on_mirnatest_protein_crfsuite -o results/mirnatrain_on_mirnatest_protein_combined
python src/evaluate.py evaluate miRNACorpus_test --results results/mirnatrain_on_mirnatest_protein_combined --models models/mirna_train_protein --entitytype protein