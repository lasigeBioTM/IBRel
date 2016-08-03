#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}
#python src/generate_corpus.py
# python src/main.py load_genia --goldstd mirna_ds

#3k => 2 minutes => 8976 miRNA entities
#10k => 35 hours => 45438 miRNA entities
python src/main.py test --goldstd mirna_ds --log $LOGLEVEL --entitytype mirna --models models/mirna_train_mirna_crfsuite -o pickle results/mirnatrain_on_mirnads_crfsuite --crf crfsuite

#3k => 36 minutes => 19567 protein/gene entities
python src/main.py test --goldstd mirna_ds --log $LOGLEVEL --entitytype protein --models models/banner -o pickle results/banner_on_mirnads --crf banner
##

#10k => 62 hours =>  46626 miRNA entities
#3k => 2 minutes => 9240 miRNA entities
python src/main.py test --goldstd mirna_ds --log $LOGLEVEL --entitytype mirna --models models/mirna_train_mirna_sner -o pickle results/mirnatrain_on_mirnads_sner --crf stanford

#3k => 334 seconds
python src/evaluate.py combine mirna_ds --log $LOGLEVEL --entitytype all --models results/mirnads_ner \
                                                                                --results results/banner_on_mirnads \
                                                                                          results/mirnatrain_on_mirnads_sner \
                                                                                          results/mirnatrain_on_mirnads_crfsuite \


python src/normalize.py all mirna_ds  --log $LOGLEVEL --models results/mirnads_ner --results results/mirnads_ner
python src/evaluate.py savetocorpus mirna_ds --log $LOGLEVEL --results results/mirnads_ner --output data/mirna_ds_annotated_10k


