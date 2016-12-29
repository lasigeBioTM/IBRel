#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

#python src/main.py load_corpus --goldstd miRNACorpus_train --log DEBUG --entitytype mirna
#python src/main.py load_corpus --goldstd miRNACorpus_test --log DEBUG --entitytype mirna
#python src/main.py load_corpus --goldstd transmir --log $LOGLEVEL
#python src/main.py train --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype mirna --models models/mirtex_dev_mirna # --crf crfsuite
#python src/main.py test --goldstd transmir --log $LOGLEVEL --entitytype mirna --models models/mirtex_dev_mirna -o pickle results/mirtexdev_on_transmir_mirna # --crf crfsuite
#python src/evaluate.py evaluate_list transmir --results results/mirtexdev_on_transmir_mirna --models models/mirtex_dev_mirna --entitytype mirna --log $LOGLEVEL --rules separate_mirnas
#
#python src/main.py test --goldstd transmir --log $LOGLEVEL --entitytype mirna --models models/mirna_train_mirna -o pickle results/mirnatrain_on_transmir_mirna --crf crfsuite
#python src/evaluate.py evaluate_list transmir --results results/mirnatrain_on_transmir_mirna --models models/mirna_train_mirna --entitytype mirna --log $LOGLEVEL --rules separate_mirnas

#python src/main.py test --goldstd transmir --log $LOGLEVEL --entitytype protein --models models/mirna_train_protein -o pickle results/mirnatrain_on_transmir_protein --crf crfsuite
#python src/evaluate.py evaluate_list transmir --results results/mirnatrain_on_transmir_protein --models models/mirna_train_protein --entitytype protein --log $LOGLEVEL
#python src/main.py test --goldstd transmir --log $LOGLEVEL --entitytype protein --models models/banner -o pickle results/banner_on_transmir --crf banner
#python src/evaluate.py evaluate_list transmir --results results/banner_on_transmir --models models/banner --entitytype protein --rules stopwords

#python src/main.py test --goldstd transmir --log $LOGLEVEL --entitytype protein --models models/jnlpba_train_protein_crfsuite -o pickle results/jnlpba_on_transmir_crfsuite --crf crfsuite
#python src/evaluate.py evaluate_list transmir --results results/jnlpba_on_transmir_crfsuite --models models/jnlpba_train_protein_crfsuite --entitytype protein --rules stopwords

#python src/main.py test --goldstd transmir --entitytype protein --models models/jnlpba_train_protein_sner -o pickle results/jnlpba_on_transmir_sner
#python src/evaluate.py evaluate_list transmir --results results/jnlpba_on_transmir_sner --models models/jnlpba_train_protein_sner --entitytype protein

#python src/evaluate.py combine transmir  --log $LOGLEVEL --entitytype all --models results/transmir_ner --results results/mirnacorpus/mirnatrain_on_transmir_mirna results/jnlpba_on_transmir_crfsuite results/jnlpba_on_transmir_sner
python src/evaluate.py combine transmir  --log $LOGLEVEL --entitytype all --models results/transmir_ner --results results/mirnacorpus/mirnatrain_on_transmir_mirna results/banner_on_transmir # results/jnlpba_on_transmir_crfsuite results/jnlpba_on_transmir_sner
python src/normalize.py all transmir  --log $LOGLEVEL --models results/transmir_ner --results results/transmir_ner
#python src/normalize.py all transmir  --log $LOGLEVEL --models models/banner --results results/banner_on_transmir
python src/evaluate.py savetocorpus transmir --log $LOGLEVEL --results results/transmir_ner --output data/transmir_annotated
#python src/evaluate.py savetocorpus transmir --log $LOGLEVEL --results results/banner_on_transmir --output data/transmir_annotated
