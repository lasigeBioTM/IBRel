#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

python src/main.py test_matcher --goldstd miRTex_test --log $LOGLEVEL --entitytype mirna --models models/mirna_regex -o pickle results/mirnaregex_on_mirtextest_mirna --crf crfsuite
python src/evaluate.py evaluate miRTex_test --results results/mirnaregex_on_mirtextest_mirna --models models/mirna_regex

python src/main.py test_matcher --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype mirna --models models/mirna_regex -o pickle results/mirnaregex_on_mirnatest_mirna --crf crfsuite
python src/evaluate.py evaluate miRNACorpus_test --results results/mirnaregex_on_mirnatest_mirna --models models/mirna_regex

python src/main.py test_matcher --goldstd transmir --log $LOGLEVEL --entitytype mirna --models models/mirna_regex -o pickle results/mirnaregex_on_transmir_mirna #--crf crfsuite
python src/evaluate.py evaluate_list transmir --results results/mirnaregex_on_transmir_mirna --models models/mirna_regex
