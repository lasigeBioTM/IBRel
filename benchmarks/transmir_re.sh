#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

#python src/main.py test_relations --goldstd transmir_annotated --log $LOGLEVEL --models results/transmir_ner --pairtype miRNA-gene --kernel jsre -o pickle results/mirnatrain_on_transmir_mirnaprotein_jsre --tag mirnatrain
#python src/evaluate.py evaluate_list transmir_annotated --results results/mirnatrain_on_transmir_mirnaprotein_jsre --models jsre --pairtype miRNA-gene --log $LOGLEVEL

python src/main.py test_relations --goldstd transmir_annotated --log $LOGLEVEL --models results/transmir_ner --pairtype miRNA-gene --kernel rules -o pickle results/rules_on_transmir_mirnaprotein_jsre --tag transmir
python src/evaluate.py evaluate_list transmir_annotated --results results/rules_on_transmir_mirnaprotein_jsre --models rules --pairtype miRNA-gene --log $LOGLEVEL
# python src/main.py load_corpus --goldstd transmir --log $LOGLEVEL
# python src/evaluate.py merge_entities transmir --models data/mirna_train --results results/mirna_train_transmir --output models/mirna_train

#python src/main.py train_relations --goldstd transmir_annotated --log $LOGLEVEL --models results/transmir_ner --pairtype miRNA-gene --kernel mil --tag miltransmir
#python src/main.py test_relations --goldstd transmir_annotated --log $LOGLEVEL --models results/transmir_ner --pairtype miRNA-gene --kernel mil -o pickle results/transmir_on_transmir_mirnaprotein_mil --tag miltransmir
#python src/evaluate.py evaluate_list transmir_annotated --results results/transmir_on_transmir_mirnaprotein_mil --models mil --pairtype miRNA-gene --log $LOGLEVEL

#python src/trainevaluate.py transmir_annotated transmir_annotated --log $LOGLEVEL --models results/transmir_ner results/transmir_ner --kernel mil --pairtype miRNA-gene --tag miltransmir --results results/transmir_on_transmir_mirnaprotein_mil
#python src/trainevaluate.py mirna_ds_annotated transmir_annotated --log $LOGLEVEL --models results/mirnads_ner results/transmir_ner --kernel mil --pairtype miRNA-gene --tag miltransmir --results results/mirnads_on_transmir_mirnaprotein_mil