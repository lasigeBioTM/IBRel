#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

#python src/main.py load_corpus --goldstd genia_sample --log $LOGLEVEL --entitytype protein
#python src/main.py annotate --goldstd genia_sample --log $LOGLEVEL --entitytype protein
#python src/crossvalidation.py --goldstd genia_sample --log $LOGLEVEL --entitytype protein --models genia_cv_protein

python src/main.py annotate --goldstd genia_sample --log $LOGLEVEL --entitytype dna
python src/crossvalidation.py --goldstd genia_sample --log $LOGLEVEL --entitytype dna --models genia_cv_dna