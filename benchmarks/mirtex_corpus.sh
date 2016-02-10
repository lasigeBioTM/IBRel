#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

python src/main.py load_corpus --goldstd miRTex_dev --log $LOGLEVEL --entitytype mirna
python src/main.py load_corpus --goldstd miRTex_test --log $LOGLEVEL --entitytype mirna
python src/main.py train --goldstd miRTex_dev --log $LOGLEVEL --entitytype mirna --models models/mirtex_dev_mirna #--crf crfsuite
python src/main.py test --goldstd miRTex_test --log $LOGLEVEL --entitytype mirna --models models/mirtex_dev_mirna -o pickle results/mirtexdev_on_mirtextext_mirna # --crf crfsuite
python src/evaluate.py evaluate miRTex_test --results results/mirtexdev_on_mirtextext_mirna --models models/mirtex_dev_mirna