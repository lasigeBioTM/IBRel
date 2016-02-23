#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

#python src/main.py load_corpus --goldstd genia_sample --log $LOGLEVEL --entitytype protein
    python src/main.py annotate --goldstd genia_sample --log $LOGLEVEL --entitytype protein
python src/crossvalidation.py --goldstd genia_sample --log $LOGLEVEL --entitytype protein --models results/genia_cv_protein --cv 10

python src/main.py annotate --goldstd genia_sample --log $LOGLEVEL --entitytype dna
python src/crossvalidation.py --goldstd genia_sample --log $LOGLEVEL --entitytype dna --models results/genia_cv_dna --cv 10

python src/main.py annotate --goldstd genia_sample --log $LOGLEVEL --entitytype all
python src/crossvalidation.py --goldstd genia_sample --log $LOGLEVEL --entitytype all --models results/genia_cv_all --cv 10