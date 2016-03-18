#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

# python src/main.py load_corpus --goldstd seedev_train --log $LOGLEVEL --entitytype all
# python src/main.py load_corpus --goldstd seedev_dev --log $LOGLEVEL --entitytype all
# python src/main.py annotate --goldstd seedev_train --log $LOGLEVEL
# python src/main.py annotate --goldstd seedev_dev --log $LOGLEVEL

#python src/seedev_evaluation.py test_relations --goldstd seedev_dev --models goldstandard --kernel rules --pairtype all -o pickle results/seedev_train_rules


#
# python src/seedev_evaluation.py train_relations --goldstd seedev_train --log $LOGLEVEL --models goldstandard --kernel jsre --pairtype all
# python src/seedev_evaluation.py test_relations --goldstd seedev_dev --log $LOGLEVEL --models goldstandard --kernel jsre -o pickle results/seedev_dev_jsre --pairtype all
# python src/evaluate.py evaluate_list seedev_dev --results results/mirtexdev_on_mirtextest_mirnaprotein_jsre --models jsre --pairtype "miRNA-gene regulation" --log $LOGLEVEL
#
#python src/main.py train_relations --goldstd seedev_train --log $LOGLEVEL --models goldstandard  --etype1 mirna --etype2 protein --kernel svmtk
#python src/main.py test_relations --goldstd seedev_dev --log $LOGLEVEL --models goldstandard --etype1 mirna --etype2 protein --kernel svmtk -o pickle results/mirtexdev_on_mirtextest_mirnaprotein_svmtk
#python src/evaluate.py evaluate_list seedev_dev --results results/mirtexdev_on_mirtextest_mirnaprotein_svmtk --models svmtk --pairtype "miRNA-gene regulation" --log $LOGLEVEL
#
python src/seedev_evaluation.py train_relations --goldstd seedev_train --log $LOGLEVEL --models goldstandard  --kernel scikit --pairtype all
python src/seedev_evaluation.py test_relations --goldstd seedev_dev --log $LOGLEVEL --models goldstandard --kernel scikit -o pickle results/seedev_dev_scikit --pairtype all
#python src/evaluate.py evaluate_list seedev_dev --results results/mirtexdev_on_mirtextest_mirnaprotein_scikit --models scikit --pairtype "miRNA-gene regulation" --log $LOGLEVEL
#
#python src/main.py test_relations --goldstd seedev_dev --log $LOGLEVEL --models goldstandard --etype1 mirna --etype2 protein --kernel rules -o pickle results/mirtexdev_on_mirtextest_mirnaprotein_rules --pairtype Specific_miRNAs-Genes/Proteins
#python src/evaluate.py evaluate_list seedev_dev --results results/mirtexdev_on_mirtextest_mirnaprotein_rules --models rules --pairtype "miRNA-gene regulation" --log $LOGLEVEL
