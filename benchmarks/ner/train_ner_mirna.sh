#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

# python src/main.py load_corpus --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype all
# python src/main.py load_corpus --goldstd miRTex_dev --log $LOGLEVEL --entitytype all

python src/main.py train --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype mirna --models models/mirna_train_mirna_crfsuite  --crf crfsuite
# python src/main.py train --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype mirna --models models/mirna_train_mirna_sner  --crf stanford

python src/main.py train --goldstd miRTex_dev --log $LOGLEVEL --entitytype mirna --models models/mirtex_train_mirna_crfsuite  --crf crfsuite
# python src/main.py train --goldstd miRTex_dev --log $LOGLEVEL --entitytype mirna --models models/mirtex_train_mirna_sner  --crf stanford



