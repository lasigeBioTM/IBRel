#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

python src/main.py annotate --goldstd miRTex_test --log $LOGLEVEL --entitytype mirna
python src/main.py annotate --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype mirna
python src/main.py train --goldstd miRNACorpus_train miRTex_test --log $LOGLEVEL --entitytype mirna --models models/mirna_mirtex_mirna  #--crf crfsuite
python src/main.py test --goldstd miRTex_test --log $LOGLEVEL --entitytype mirna --models models/mirna_mirtex_mirna -o pickle results/mirnamirtex_on_mirtextest_mirna #--crf crfsuite
python src/evaluate.py evaluate miRTex_test --results results/mirnamirtex_on_mirtextest_mirna --models models/mirna_mirtex_mirna --entitytype mirna
python src/main.py test --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype mirna --models models/mirna_mirtex_mirna -o pickle results/mirnamirtex_on_mirnatest_mirna  #--crf crfsuite
python src/evaluate.py evaluate miRNACorpus_test --results results/mirnamirtex_on_mirnatest_mirna --models models/mirna_mirtex_mirna --entitytype mirna

python src/main.py annotate --goldstd miRTex_test --log $LOGLEVEL --entitytype protein
python src/main.py annotate --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype protein
python src/main.py train --goldstd miRNACorpus_train miRTex_test --log $LOGLEVEL --entitytype protein --models models/mirna_mirtex_protein  #--crf crfsuite
python src/main.py test --goldstd miRTex_test --log $LOGLEVEL --entitytype protein --models models/mirna_mirtex_protein -o pickle results/mirnamirtex_on_mirtextest_protein #--crf crfsuite
python src/evaluate.py evaluate miRTex_test --results results/mirnamirtex_on_mirtextest_protein --models models/mirna_mirtex_protein --entitytype protein
python src/main.py test --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype protein --models models/mirna_mirtex_protein -o pickle results/mirnamirtex_on_mirnatest_protein  #--crf crfsuite
python src/evaluate.py evaluate miRNACorpus_test --results results/mirnamirtex_on_mirnatest_protein --models models/mirna_mirtex_protein --entitytype protein
