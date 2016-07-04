#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}
#python src/generate_corpus.py
#python src/main.py load_genia --goldstd mirna_ds
#python src/main.py test --goldstd mirna_ds --log $LOGLEVEL --entitytype protein --models models/mirna_train_protein_crfsuite -o pickle results/mirnatrainprotein_on_mirnads_crfsuite --crf crfsuite
#python src/main.py test --goldstd mirna_ds --log $LOGLEVEL --entitytype protein --models models/mirna_train_protein_sner -o pickle results/mirnatrainprotein_on_mirnads_sner --crf stanford
##
#python src/main.py test --goldstd mirna_ds --log $LOGLEVEL --entitytype mirna --models models/mirna_train_mirna_crfsuite -o pickle results/mirnatrain_on_mirnads_crfsuite --crf crfsuite
#python src/main.py test --goldstd mirna_ds --log $LOGLEVEL --entitytype mirna --models models/mirna_train_mirna_sner -o pickle results/mirnatrain_on_mirnads_sner --crf stanford

#python src/evaluate.py combine mirna_ds --log $LOGLEVEL --entitytype all --models results/mirna_ds_entities \
#                                                                                --results results/mirnatrainprotein_on_mirnads_crfsuite \
#                                                                                          results/mirnatrainprotein_on_mirnads_sner \
#                                                                                          results/mirnatrain_on_mirnads_crfsuite \

#python src/normalize.py protein mirna_ds  --log $LOGLEVEL --models combined --results results/mirna_ds_entities
#python src/normalize.py mirna mirna_ds  --log $LOGLEVEL --models combined --results results/mirna_ds_entities
python src/generate_corpus.py annotate

#cp corpora/Thaliana/thaliana-documents_2.pickle data/
#python src/seedev_evaluation.py test_multiple --goldstd seedev_ds --log INFO --models models/seedev_train_entity -o pickle results/seedev_extended_ner

#python src/seedev_evaluation.py add_goldstandard --goldstd seedev_ds --log INFO

#python src/seedev_evaluation.py add_sentences --goldstd seedev_train --log INFO --models data/SeeDev-dev.txt.pickle
# python src/seedev_evaluation.py add_sentences --goldstd seedev_extended --log INFO --models data/thaliana-documents_1.pickle
#python src/seedev_evaluation.py train_relations --goldstd seedev_ds --log $LOGLEVEL --models goldstandard --kernel jsre --pairtype all
#python src/seedev_evaluation.py test_relations --goldstd seedev_test --log $LOGLEVEL --models goldstandard --kernel jsre -o pickle results/seedev_test_jsre_extended1 --pairtype all


