#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

#python src/trainevaluate.py mirna_ds_annotated transmir_annotated --log info --models results/mirnads_ner results/transmir_ner --kernel mil --pairtype miRNA-gene --tag miltransmir --results results/mirnads_on_transmir_mirnaprotein_mil
# python src/trainevaluate.py --train mirna_ds_annotated1 --test transmir_annotated miRTex_test miRNACorpus_test --log $LOGLEVEL --models results/mirnads_ner results/transmir_ner goldstandard goldstandard --kernel mil --pairtype miRNA-gene --tag miltransmir --results results/mirnads_mil
# python src/trainevaluate.py mirna_ds_annotated miRTex_test miRNACorpus_test --log info --models results/mirnads_ner goldstandard goldstandard --kernel mil --pairtype miRNA-gene --tag miltransmir --results results/mirnads_mil
python src/trainevaluate.py --train mirna_ds_annotated2 --test transmir_annotated miRTex_test miRNACorpus_test --models results/mirnads_ner results/transmir_ner goldstandard goldstandard --kernel mil --pairtype miRNA-gene --tag miltransmir --results results/mirnads_mil
python src/trainevaluate.py --train mirna_ds_annotated2 mirna_ds_annotated3 --test transmir_annotated miRTex_test miRNACorpus_test --models results/mirnads_ner results/transmir_ner goldstandard goldstandard --kernel mil --pairtype miRNA-gene --tag miltransmir --results results/mirnads_mil
#python src/trainevaluate.py --train mirna_ds_annotated2 mirna_ds_annotated3 mirna_ds_annotated4 --test transmir_annotated miRTex_test miRNACorpus_test --models results/mirnads_ner results/transmir_ner goldstandard goldstandard --kernel mil --pairtype miRNA-gene --tag miltransmir --results results/mirnads_mil
#python src/trainevaluate.py --train mirna_ds_annotated2 mirna_ds_annotated3 mirna_ds_annotated4 mirna_ds_annotated5  --test transmir_annotated miRTex_test miRNACorpus_test --models results/mirnads_ner results/transmir_ner goldstandard goldstandard --kernel mil --pairtype miRNA-gene --tag miltransmir --results results/mirnads_mil
