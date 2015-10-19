from text.corpus import Corpus

class PubmedCorpus(Corpus):
    """
        Corpus composed by Pubmed documents
    """
    def __init__(self, corpusdir, pmidlist, **kwargs):
         super(PubmedCorpus, self).__init__(corpusdir, **kwargs)
         self.pmids = pmidlist

    def load_corpus(self, corenlpserver, process=True):
        """
        Use the PubMed web services to retrieve the title and abstract of each PMID
        :param corenlpserver:
        :param process:
        :return:
        """