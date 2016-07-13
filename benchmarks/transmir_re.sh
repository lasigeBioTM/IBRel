#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

# python src/main.py load_corpus --goldstd transmir --log $LOGLEVEL
# python src/evaluate.py merge_entities transmir --models data/mirna_train --results results/mirna_train_transmir --output models/mirna_train
python src/main.py test_relations --goldstd transmir_annotated --log $LOGLEVEL --models results/mirna_train_transmir --pairtype miRNA-gene --kernel jsre -o pickle results/mirnatrain_on_transmir_mirnaprotein_mil --tag mirnatrain
python src/evaluate.py evaluate transmir_annotated --results results/mirnatrain_on_transmir_mirnaprotein_jsre --models jsre --pairtype miRNA-gene --log $LOGLEVEL
