__author__ = 'Andre'
import logging

class Token2(object):
    '''Token that is part of a sentence'''
    def __init__(self, text, **kwargs):
        self.text = text
        self.sid = kwargs.get("sid")
        self.order = kwargs.get("order")
        # logging.debug("order: {}".format(self.order))
        self.features = {}
        self.tags = {}
        self.tid = kwargs.get("tid")