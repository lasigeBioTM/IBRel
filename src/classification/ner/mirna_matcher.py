__author__ = 'Andre'
from matcher import MatcherModel

class MirnaMatcher(MatcherModel):
    """
       Find miRNAs based on a fixed set of expressions
    """
    def __init__(self, path, **kwargs):
        super(MirnaMatcher, self).__init__(path, **kwargs)
        self.prefixes = ["mir-", "let-", "miR-", "hsa-mir-"]

    def test(self, corpus):
        pass
