#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

# python src/main.py load_corpus --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype mirna
# python src/main.py load_corpus --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype mirna
python src/main.py annotate --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype mirna
python src/main.py train --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype mirna --models models/mirna_train_mirna  --crf crfsuite
python src/main.py test --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype mirna --models models/mirna_train_mirna -o pickle results/mirnatrain_on_mirnatest_mirna  --crf crfsuite
python src/evaluate.py evaluate miRNACorpus_test --results results/mirnatrain_on_mirnatest_mirna --models models/mirna_train_mirna --entitytype mirna --log $LOGLEVEL


python src/main.py annotate --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype protein
python src/main.py train --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype protein --models models/mirna_train_protein  --crf crfsuite
python src/main.py test --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype protein --models models/mirna_train_protein -o pickle results/mirnatrain_on_mirnatest_protein  --crf crfsuite
python src/evaluate.py evaluate miRNACorpus_test --results results/mirnatrain_on_mirnatest_protein --models models/mirna_train_protein --entitytype protein

#python src/main.py annotate --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype mirna
#python src/main.py annotate --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype mirna
# python src/crossvalidation.py --goldstd miRNACorpus_train miRNACorpus_test --log $LOGLEVEL --entitytype mirna --models results/mirnacorpus_cv_mirna_crfsuite --cv 5 --crf crfsuite
#python src/crossvalidation.py --goldstd miRNACorpus_train miRNACorpus_test --log $LOGLEVEL --entitytype mirna --models results/mirnacorpus_cv_mirna_sner --cv 5

