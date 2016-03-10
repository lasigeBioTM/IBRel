#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

python src/main.py annotate --goldstd miRTex_dev --log $LOGLEVEL --entitytype mirna
python src/main.py train --goldstd miRTex_dev --log $LOGLEVEL --entitytype mirna --models models/mirtex_dev_mirna_crfsuite  --crf crfsuite
python src/main.py test --goldstd miRTex_test --log $LOGLEVEL --entitytype mirna --models models/mirtex_dev_mirna_crfsuite -o pickle results/mirtexdev_on_mirnatest_mirna_crfsuite  --crf crfsuite
python src/evaluate.py evaluate miRTex_test --results results/mirtexdev_on_mirnatest_mirna_crfsuite --models models/mirtex_dev_mirna_crfsuite --entitytype mirna
python src/main.py train --goldstd miRTex_dev --log $LOGLEVEL --entitytype mirna --models models/mirtex_dev_mirna_sner
python src/main.py test --goldstd miRTex_test --log $LOGLEVEL --entitytype mirna --models models/mirtex_dev_mirna_sner -o pickle results/mirtexdev_on_mirnatest_mirna_sner
python src/evaluate.py evaluate miRTex_test --results results/mirtexdev_on_mirnatest_mirna_sner --models models/mirtex_dev_mirna_sner --entitytype mirna

python src/classification/results.py combine miRTex_test --entitytype mirna --finalmodel models/mirtex_dev_mirna_combined --results results/mirtexdev_on_mirnatest_mirna_sner results/mirtexdev_on_mirnatest_mirna_crfsuite -o results/mirtexdev_on_mirnatest_mirna_combined --models models/mirtex_dev_mirna_crfsuite models/mirtex_dev_mirna_sner
python src/evaluate.py evaluate miRTex_test --results results/mirtexdev_on_mirnatest_mirna_combined --models models/mirtex_dev_mirna_combined --entitytype mirna


python src/main.py annotate --goldstd miRTex_dev --log $LOGLEVEL --entitytype protein
python src/main.py train --goldstd miRTex_dev --log $LOGLEVEL --entitytype protein --models models/mirtex_dev_protein_crfsuite  --crf crfsuite
python src/main.py test --goldstd miRTex_test --log $LOGLEVEL --entitytype protein --models models/mirtex_dev_protein_crfsuite -o pickle results/mirtexdev_on_mirnatest_protein_crfsuite  --crf crfsuite
python src/evaluate.py evaluate miRTex_test --results results/mirtexdev_on_mirnatest_protein_crfsuite --models models/mirtex_dev_protein_crfsuite --entitytype protein
python src/main.py train --goldstd miRTex_dev --log $LOGLEVEL --entitytype protein --models models/mirtex_dev_protein_sner
python src/main.py test --goldstd miRTex_test --log $LOGLEVEL --entitytype protein --models models/mirtex_dev_protein_sner -o pickle results/mirtexdev_on_mirnatest_protein_sner
python src/evaluate.py evaluate miRTex_test --results results/mirtexdev_on_mirnatest_protein_sner --models models/mirtex_dev_protein_sner --entitytype protein

python src/classification/results.py combine miRTex_test --entitytype protein --finalmodel models/mirtex_dev_protein_combined --results results/mirtexdev_on_mirnatest_protein_crfsuite results/mirtexdev_on_mirnatest_protein_sner -o results/mirtexdev_on_mirnatest_protein_combined --models models/mirtex_dev_protein_crfsuite models/mirtex_dev_protein_sner
python src/evaluate.py evaluate miRTex_test --results results/mirtexdev_on_mirnatest_protein_combined --models models/mirtex_dev_protein_combined --entitytype protein