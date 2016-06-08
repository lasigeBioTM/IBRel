#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

# python src/main.py load_corpus --goldstd miRTex_dev --log $LOGLEVEL --entitytype all
# python src/main.py load_corpus --goldstd miRTex_test --log $LOGLEVEL --entitytype all
#python src/main.py annotate --goldstd miRTex_dev --log $LOGLEVEL --pairtype "miRNA-gene regulation"
python src/main.py annotate --goldstd miRTex_test --log $LOGLEVEL --pairtype "miRNA-gene regulation"
#
#python src/main.py train_relations --goldstd miRTex_dev --log $LOGLEVEL --models goldstandard  --etype1 mirna --etype2 protein --kernel jsre
#python src/main.py test_relations --goldstd miRTex_test --log $LOGLEVEL --models goldstandard --etype1 mirna --etype2 protein --kernel jsre -o pickle results/mirtexdev_on_mirtextest_mirnaprotein_jsre
#python src/evaluate.py evaluate_list miRTex_test --results results/mirtexdev_on_mirtextest_mirnaprotein_jsre --models jsre --pairtype "miRNA-gene regulation" --log $LOGLEVEL
#
#python src/main.py train_relations --goldstd miRTex_dev --log $LOGLEVEL --models goldstandard  --etype1 mirna --etype2 protein --kernel svmtk
#python src/main.py test_relations --goldstd miRTex_test --log $LOGLEVEL --models goldstandard --etype1 mirna --etype2 protein --kernel svmtk -o pickle results/mirtexdev_on_mirtextest_mirnaprotein_svmtk
#python src/evaluate.py evaluate_list miRTex_test --results results/mirtexdev_on_mirtextest_mirnaprotein_svmtk --models svmtk --pairtype "miRNA-gene regulation" --log $LOGLEVEL
#
# python src/main.py train_relations --goldstd miRTex_dev --log $LOGLEVEL --models goldstandard  --pairtype miRNA-gene --kernel jsre
python src/main.py test_relations --goldstd miRTex_test --log $LOGLEVEL --models goldstandard --pairtype miRNA-gene --kernel jsre -o pickle results/mirnatrain_on_mirtextest_mirnaprotein_jsre --tag mirnatrain
python src/evaluate.py evaluate_list miRTex_test --results results/mirnatrain_on_mirtextest_mirnaprotein_jsre --models jsre --pairtype miRNA-gene --log $LOGLEVEL
#
#python src/main.py test_relations --goldstd miRTex_test --log $LOGLEVEL --models goldstandard --etype1 mirna --etype2 protein --kernel rules -o pickle results/mirtexdev_on_mirtextest_mirnaprotein_rules --pairtype Specific_miRNAs-Genes/Proteins
#python src/evaluate.py evaluate_list miRTex_test --results results/mirtexdev_on_mirtextest_mirnaprotein_rules --models rules --pairtype "miRNA-gene regulation" --log $LOGLEVEL
