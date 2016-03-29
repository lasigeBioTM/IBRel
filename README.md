# IBEnt
Framework for identifying biomedical entities

## Dependencies:
* Python 2.7 and Java 8
* Pre-processing:
    * [Genia Sentence Splitter](http://www.nactem.ac.uk/y-matsu/geniass/)
        * Requires Ruby and compilation with `make`
    * [Stanford CoreNLP 3.6](http://stanfordnlp.github.io/CoreNLP/)
        * Use run_server.sh
* Term recognition
    * [Stanford NER 3.5.1](http://nlp.stanford.edu/software/CRF-NER.shtml)
* Relation extraction
    * [SVM-light-TK](http://disi.unitn.it/moschitti/Tree-Kernel.htm)
    * [Shallow Language Kernel](https://hlt-nlp.fbk.eu/technologies/jsre)
* Local [ChEBI](https://www.ebi.ac.uk/chebi/) MySQL database if you choose set use_chebi as true
    * Required ChEBI tables: term, term_synonym, word2term3, word3, descriptor3, SSM_TermDesc, graph_path
* requirements.txt - run `pip install -r requirements.txt`

## Configuration
After setting up the dependencies, you have to run `python src/config/config.py` to set up some values.
You can use the [CHEMDNER-patents sample data](http://www.biocreative.org/media/store/files/2015/chemdner_patents_sample_v02.tar.zip) to check if the system is working correctly.

## Usage

Start the server with `python src/server.py` and input text with `python src/client`.
You can test the server with predefined sentences using `python src/client [0-3]`
You can also use your own client, sending a POST request to the address in config.host_ip.
