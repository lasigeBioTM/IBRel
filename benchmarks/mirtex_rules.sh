#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

#python src/main.py annotate --goldstd miRTex_test --log $LOGLEVEL --pairtype "miRNA-gene"
python src/main.py test_relations --goldstd miRTex_test --log $LOGLEVEL --models goldstandard --pairtype "miRNA-gene" --kernel mirtex_rules -o pickle results/mirtexrules_on_mirtextest_mirnaprotein --tag mirnatrain
python src/evaluate.py evaluate_list miRTex_test --results results/mirtexrules_on_mirtextest_mirnaprotein --models mirtex_rules --pairtype "miRNA-gene" --log $LOGLEVEL # -tag mirnatrain
#

#python src/main.py test_relations --goldstd miRTex_test --log $LOGLEVEL --models goldstandard --pairtype "miRNA-gene" --kernel rules -o pickle results/rules_on_mirtextest_mirnaprotein --tag mirnatrain
#python src/evaluate.py evaluate_list miRTex_test --results results/rules_on_mirtextest_mirnaprotein --models rules --pairtype "miRNA-gene" --log $LOGLEVEL # -tag mirnatrain
