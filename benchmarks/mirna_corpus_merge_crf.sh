#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

python src/main.py annotate --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype mirna
python src/main.py train --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype mirna --models models/mirna_train_mirna_crfsuite  --crf crfsuite
python src/main.py test --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype mirna --models models/mirna_train_mirna_crfsuite -o pickle results/mirnatrain_on_mirnatest_mirna_crfsuite  --crf crfsuite
python src/evaluate.py evaluate miRNACorpus_test --results results/mirnatrain_on_mirnatest_mirna_crfsuite --models models/mirna_train_mirna_crfsuite --entitytype mirna
python src/main.py train --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype mirna --models models/mirna_train_mirna_sner
python src/main.py test --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype mirna --models models/mirna_train_mirna_sner -o pickle results/mirnatrain_on_mirnatest_mirna_sner
python src/evaluate.py evaluate miRNACorpus_test --results results/mirnatrain_on_mirnatest_mirna_sner --models models/mirna_train_mirna_sner --entitytype mirna

python src/classification/results.py combine miRNACorpus_test --entitytype mirna --finalmodel models/mirna_train_mirna_combined --results results/mirnatrain_on_mirnatest_mirna_sner results/mirnatrain_on_mirnatest_mirna_crfsuite -o results/mirnatrain_on_mirnatest_mirna_combined --models models/mirna_train_mirna_crfsuite models/mirna_train_mirna_sner
python src/evaluate.py evaluate miRNACorpus_test --results results/mirnatrain_on_mirnatest_mirna_combined --models models/mirna_train_mirna_combined --entitytype mirna


python src/main.py annotate --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype protein
python src/main.py train --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype protein --models models/mirna_train_protein_crfsuite  --crf crfsuite
python src/main.py test --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype protein --models models/mirna_train_protein_crfsuite -o pickle results/mirnatrain_on_mirnatest_protein_crfsuite  --crf crfsuite
python src/evaluate.py evaluate miRNACorpus_test --results results/mirnatrain_on_mirnatest_protein_crfsuite --models models/mirna_train_protein_crfsuite --entitytype protein
python src/main.py train --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype protein --models models/mirna_train_protein_sner
python src/main.py test --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype protein --models models/mirna_train_protein_sner -o pickle results/mirnatrain_on_mirnatest_protein_sner
python src/evaluate.py evaluate miRNACorpus_test --results results/mirnatrain_on_mirnatest_protein_sner --models models/mirna_train_protein_sner --entitytype protein

python src/classification/results.py combine miRNACorpus_test --entitytype protein --finalmodel models/mirna_train_protein_combined --results results/mirnatrain_on_mirnatest_protein_sner results/mirnatrain_on_mirnatest_protein_crfsuite -o results/mirnatrain_on_mirnatest_protein_combined --models models/mirna_train_protein_crfsuite models/mirna_train_protein_sner
python src/evaluate.py evaluate miRNACorpus_test --results results/mirnatrain_on_mirnatest_protein_combined --models models/mirna_train_protein_combined --entitytype protein