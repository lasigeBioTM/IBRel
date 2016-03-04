#!/bin/sh
set -x
LOGLEVEL=${1:-WARNING}

# python src/main.py load_corpus --goldstd miRNACorpus_train --log $LOGLEVEL --entitytype all
# python src/main.py load_corpus --goldstd miRNACorpus_test --log $LOGLEVEL --entitytype all
# python src/main.py annotate --goldstd miRNACorpus_train --log $LOGLEVEL
# python src/main.py annotate --goldstd miRNACorpus_test --log $LOGLEVEL
# python src/main.py train_relations --goldstd miRNACorpus_train --log $LOGLEVEL --models goldstandard  --pairtype1 mirna --pairtype2 protein --kernel jsre
# python src/main.py test_relations --goldstd miRNACorpus_test --log $LOGLEVEL --models goldstandard --pairtype1 mirna --pairtype2 protein --kernel jsre -o pickle results/mirnatrain_on_mirnatest_mirnaprotein_jsre
# python src/evaluate.py evaluate miRNACorpus_test --results results/mirnatrain_on_mirnatest_mirnaprotein_jsre --models jsre --pairtype Specific_miRNAs-Genes/Proteins --log $LOGLEVEL

python src/main.py train_relations --goldstd miRNACorpus_train --log $LOGLEVEL --models goldstandard  --pairtype1 mirna --pairtype2 protein --kernel svmtk
python src/main.py test_relations --goldstd miRNACorpus_test --log $LOGLEVEL --models goldstandard --pairtype1 mirna --pairtype2 protein --kernel svmtk -o pickle results/mirnatrain_on_mirnatest_mirnaprotein_svmtk
python src/evaluate.py evaluate miRNACorpus_test --results results/mirnatrain_on_mirnatest_mirnaprotein_svmtk --models svmtk --pairtype Specific_miRNAs-Genes/Proteins --log $LOGLEVEL

# python src/main.py test_relations --goldstd miRNACorpus_test --log $LOGLEVEL --models goldstandard --pairtype1 mirna --pairtype2 protein --kernel rules -o pickle results/mirnatrain_on_mirnatest_mirnaprotein_rules --pairtype Specific_miRNAs-Genes/Proteins
# python src/evaluate.py evaluate miRNACorpus_test --results results/mirnatrain_on_mirnatest_mirnaprotein_rules --models rules --pairtype Specific_miRNAs-Genes/Proteins --log $LOGLEVEL
