#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

# python src/main.py load_corpus --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype mirna
python src/main.py load_corpus --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype mirna
python src/main.py annotate --goldstd miRNACorpus_train --log $LOGLEVEL
python src/main.py train_relations --goldstd miRNACorpus_train --log $LOGLEVEL --models goldstandard  --pairtype1 mirna --pairtype2 protein --kernel jsre
python src/main.py test_relations --goldstd miRNACorpus_test --log $LOGLEVEL --models goldstandard --pairtype1 mirna --pairtype2 protein --kernel jsre -o pickle results/mirnatrain_on_mirnatest_mirnaprotein
python src/evaluate.py evaluate miRNACorpus_test --results results/mirnatrain_on_mirnatest_mirnaprotein --models goldstandard --entitytype mirna --log $LOGLEVEL
