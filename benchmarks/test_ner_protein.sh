#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

# Load test corpora
python src/main.py load_corpus --goldstd jnlpba_test --log $LOGLEVEL --entitytype protein
python src/main.py load_corpus --goldstd bc2gm_test --log $LOGLEVEL --entitytype protein
python src/main.py load_corpus --goldstd lll_test --log $LOGLEVEL --entitytype protein
