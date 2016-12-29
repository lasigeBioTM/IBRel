#!/bin/sh
set -x
set -e
LOGLEVEL=${1:-WARNING}
#python src/generate_corpus.py
#python src/main.py load_genia --goldstd mirna_ds

for i in 2 3 4 5
do
#3k => 2 minutes => 8976 miRNA entities
#10k => 35 hours => 45438 miRNA entities
#python src/main.py test --goldstd mirna_ds$i --log $LOGLEVEL --entitytype mirna --models models/mirtex_dev_mirna_crfsuite  --crf crfsuite -o pickle results/mirtexdev_on_mirnads_crfsuite$i

#10k => 62 hours =>  46626 miRNA entities
#3k => 2 minutes => 9240 miRNA entities
#python src/main.py test --goldstd mirna_ds$i --log $LOGLEVEL --entitytype mirna --models models/mirtex_dev_mirna_sner -o pickle results/mirtexdev_on_mirnads_sner$i --crf stanford


#3k => 36 minutes => 19567 protein/gene entities
python src/main.py test --goldstd mirna_ds$i --log $LOGLEVEL --entitytype protein --models models/banner -o pickle results/banner_on_mirnads$i --crf banner
##

#3k => 36 minutes => 19567 protein/gene entities
python src/main.py test --goldstd mirna_ds$i --log $LOGLEVEL --entitytype protein --models models/jnlpba_train_protein_crfsuite -o pickle results/jnlpba_on_mirnads$i --crf crfsuite
##


#3k => 334 seconds
python src/evaluate.py combine mirna_ds$i --log $LOGLEVEL --entitytype all --models results/mirnads_ner \
                                                                                --results results/jnlpba_on_mirnads$i \
                                                                                          results/banner_on_mirnads$i \
                                                                                          results/mirna-ds/mirtexdev_on_mirnads_sner$i \
                                                                                          results/mirna-ds/mirtexdev_on_mirnads_crfsuite$i


python src/normalize.py all mirna_ds$i  --log $LOGLEVEL --models results/mirnads_ner --results results/mirnads_ner
python src/evaluate.py savetocorpus mirna_ds$i --log $LOGLEVEL --results results/mirnads_ner --output data/mirna_ds_annotated_$i

done
