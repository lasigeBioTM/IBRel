import logging
import xml.etree.ElementTree as ET
import os
import sys
import progressbar as pb
import time

from text.corpus import Corpus
from text.document import Document
from text.sentence import Sentence

type_match = {"DNA": "protein",
              "protein": "protein"}

class JNLPBACorpus(Corpus):
    def __init__(self, corpusdir, **kwargs):
        super(JNLPBACorpus, self).__init__(corpusdir, **kwargs)
        self.subtypes = ["protein", "DNA"]