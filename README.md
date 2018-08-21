# IBRel
Framework for identifying biomedical relations

## Citation:

Lamurias A, Clarke LA, Couto FM (2017) Extracting microRNA-gene relations from biomedical literature using distant supervision. PLOS ONE 12(3): e0171929. doi: 10.1371/journal.pone.0171929

## Dependencies:
* Python 3.6 and Java 8
* Pre-processing:
    * [Genia Sentence Splitter](http://www.nactem.ac.uk/y-matsu/geniass/) (requires ruby)
    * [Python wrapper for Stanford CoreNLP](https://bitbucket.org/torotoki/corenlp-python)
* Term recognition
    * [Stanford NER 3.5.1](http://nlp.stanford.edu/software/CRF-NER.shtml)
* Relation extraction
    * [SVM-light-TK](http://disi.unitn.it/moschitti/Tree-Kernel.htm)
    * [Shallow Language Kernel](https://hlt-nlp.fbk.eu/technologies/jsre)
* requirements.txt - run `pip install -r requirements.txt`

## Configuration
A Dockerfile is provided to help with the installation.
Build and then run with the `-i` flag.
After setting up the dependencies, you have to run `python3 src/config/config.py` to set up some values.
You can use the [CHEMDNER-patents sample data](http://www.biocreative.org/media/store/files/2015/chemdner_patents_sample_v02.tar.zip) to check if the system is working correctly.
Then run ./benchmarks/check_setup.sh to confirm if everything is set up correctly.

## Usage
To run distant supervision multi-instance learning experiments, use src/trainevaluate.py and check mil.sh for an example.
