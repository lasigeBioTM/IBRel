#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

#python src/main.py merge_corpus --goldstd mirna_ds_annotated1 mirna_ds_annotated2 mirna_ds_annotated3 mirna_ds_annotated4 mirna_ds_annotated5 mirna_ds_annotated6 mirna_ds_annotated7 mirna_ds_annotated8 mirna_ds_annotated9 mirna_ds_annotated10 --output corpus mirna_ds_annotated
#python src/main.py merge_corpus --log $LOGLEVEL --goldstd mirna_ds_annotated1 --output corpus mirna_ds_annotated

#python src/main.py test --goldstd mirna_ds --log $LOGLEVEL --entitytype mirna --models models/mirna_train_mirna -o pickle results/mirnatrain_on_mirnads_mirna --crf crfsuite
# python src/evaluate.py evaluate_list transmir --results results/mirnatrain_on_transmir_mirna --models models/mirna_train_mirna --entitytype mirna --log $LOGLEVEL --rules separate_mirnas

#python src/main.py test --goldstd transmir --log $LOGLEVEL --entitytype protein --models models/mirna_train_protein -o pickle results/mirnatrain_on_transmir_protein --crf crfsuite
#python src/evaluate.py evaluate_list transmir --results results/mirnatrain_on_transmir_protein --models models/mirna_train_protein --entitytype protein --log $LOGLEVEL
#python src/main.py test --goldstd mirna_ds --log $LOGLEVEL --entitytype protein --models models/banner -o pickle results/banner_on_mirnads --crf banner
# python src/evaluate.py evaluate_list transmir --results results/banner_on_transmir --models models/banner --entitytype protein --rules stopwords

#python src/evaluate.py combine mirna_ds  --log $LOGLEVEL --entitytype all --models results/mirnads_ner --results results/mirnatrain_on_mirnads_mirna results/banner_on_mirnads
#python src/normalize.py all mirna_ds  --log $LOGLEVEL --models results/mirnads_ner --results results/mirnads_ner
#python src/evaluate.py savetocorpus mirna_ds --log $LOGLEVEL --results results/mirnads_ner --output corpora/mirna-ds/abstracts_annotated


#python src/trainevaluate.py mirna_ds_annotated transmir_annotated --log info --models results/mirnads_ner results/transmir_ner --kernel mil --pairtype miRNA-gene --tag miltransmir --results results/mirnads_on_transmir_mirnaprotein_mil
# python src/trainevaluate.py --train mirna_ds_annotated1 --test transmir_annotated miRTex_test miRNACorpus_test --log $LOGLEVEL --models results/mirnads_ner results/transmir_ner goldstandard goldstandard --kernel mil --pairtype miRNA-gene --tag miltransmir --results results/mirnads_mil
# python src/trainevaluate.py mirna_ds_annotated miRTex_test miRNACorpus_test --log info --models results/mirnads_ner goldstandard goldstandard --kernel mil --pairtype miRNA-gene --tag miltransmir --results results/mirnads_mil
python src/trainevaluate.py --train mirna_ds_annotated2 --test transmir_annotated miRTex_test miRNACorpus_test --models results/mirnads_ner results/transmir_ner goldstandard goldstandard --kernel mil --pairtype miRNA-gene --tag miltransmir --results results/mirnads_mil
python src/trainevaluate.py --train mirna_ds_annotated2 mirna_ds_annotated3 --test transmir_annotated miRTex_test miRNACorpus_test --models results/mirnads_ner results/transmir_ner goldstandard goldstandard --kernel mil --pairtype miRNA-gene --tag miltransmir --results results/mirnads_mil
#python src/trainevaluate.py --train mirna_ds_annotated2 mirna_ds_annotated3 mirna_ds_annotated4 --test transmir_annotated miRTex_test miRNACorpus_test --models results/mirnads_ner results/transmir_ner goldstandard goldstandard --kernel mil --pairtype miRNA-gene --tag miltransmir --results results/mirnads_mil
#python src/trainevaluate.py --train mirna_ds_annotated2 mirna_ds_annotated3 mirna_ds_annotated4 mirna_ds_annotated5  --test transmir_annotated miRTex_test miRNACorpus_test --models results/mirnads_ner results/transmir_ner goldstandard goldstandard --kernel mil --pairtype miRNA-gene --tag miltransmir --results results/mirnads_mil
