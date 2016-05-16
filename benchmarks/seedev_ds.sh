#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

#python src/seedev_evaluation.py train_multiple --goldstd seedev_train --log INFO --models models/seedev_train_entity
#python src/seedev_evaluation.py test_multiple --goldstd seedev_dev --log INFO --models models/seedev_train_entity -o pickle results/seedev_dev_ner
#python src/seedev_evaluation.py evaluate_ner --goldstd seedev_dev --log INFO --models models/seedev_train_entity -o pickle results/seedev_dev_ner

#python src/seedev_evaluation.py train_multiple --goldstd seedev_traindev --log INFO --models models/seedev_train_entity
#python src/seedev_evaluation.py test_multiple --goldstd seedev_test --log INFO --models models/seedev_train_entity -o pickle results/seedev_test_ner
#python src/seedev_evaluation.py evaluate_ner --goldstd seedev_test --log INFO --models models/seedev_train_entity -o pickle results/seedev_test_ner

#cp corpora/Thaliana/thaliana-documents_2.pickle data/
#python src/seedev_evaluation.py test_multiple --goldstd seedev_ds --log INFO --models models/seedev_train_entity -o pickle results/seedev_extended_ner

#python src/seedev_evaluation.py add_goldstandard --goldstd seedev_ds --log INFO

#python src/seedev_evaluation.py add_sentences --goldstd seedev_train --log INFO --models data/SeeDev-dev.txt.pickle
# python src/seedev_evaluation.py add_sentences --goldstd seedev_extended --log INFO --models data/thaliana-documents_1.pickle
python src/seedev_evaluation.py train_relations --goldstd seedev_ds --log $LOGLEVEL --models goldstandard --kernel jsre --pairtype all
python src/seedev_evaluation.py test_relations --goldstd seedev_test --log $LOGLEVEL --models goldstandard --kernel jsre -o pickle results/seedev_test_jsre_extended1 --pairtype all


