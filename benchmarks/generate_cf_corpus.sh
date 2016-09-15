#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

#python src/generate_corpus.py download corpora/cf_corpus/abstracts.txt
#python src/generate_corpus.py process corpora/cf_corpus/abstracts.txt

#python src/main.py test --goldstd mirna_cf --log $LOGLEVEL --entitytype mirna --models models/mirtex_dev_mirna_crfsuite  --crf crfsuite -o pickle results/mirtexdev_on_cf_crfsuite
#python src/main.py test --goldstd mirna_cf --log $LOGLEVEL --entitytype mirna --models models/mirtex_dev_mirna_sner -o pickle results/mirtexdev_on_cf_sner --crf stanford
#python src/main.py test --goldstd mirna_cf --log $LOGLEVEL --entitytype protein --models models/banner -o pickle results/banner_on_cf --crf banner
#python src/evaluate.py combine mirna_cf --log $LOGLEVEL --entitytype all --models results/cf_ner \
#                                                                                --results results/banner_on_cf \
#                                                                                          results/mirtexdev_on_cf_sner \
#                                                                                          results/mirtexdev_on_cf_crfsuite
#
#
#python src/normalize.py all mirna_cf  --log $LOGLEVEL --models results/cf_ner --results results/cf_ner
#python src/evaluate.py savetocorpus mirna_cf --log $LOGLEVEL --results results/cf_ner --output data/mirna_cf_annotated
python src/trainevaluate.py --train mirna_ds_annotated2 --test mirna_cf_annotated --models results/mirnads_ner results/cf_ner --kernel mil --pairtype miRNA-gene --tag miltransmir --results results/mirnads_mil

#python src/trainevaluate.py --train mirna_ds_annotated2 mirna_ds_annotated3 mirna_ds_annotated4 mirna_ds_annotated5 --test mirna_cf_annotated --models results/mirnads_ner results/cf_ner --kernel mil --pairtype miRNA-gene --tag miltransmir --results results/mirnads_mil

