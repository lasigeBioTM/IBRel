#!/usr/bin/env python
# -*- coding: utf-8 -*-
import httplib
#import xml.dom.minidom as minidom
#import urllib
import logging
import requests
import time
import sys
import xml.etree.ElementTree as ET
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '../..'))
from text.document import Document
"""
Get texts from PubMed
"""

class PubmedDocument(Document):
    def __init__(self, pmid, **kwargs):
        self.pmid = pmid
        self.pmcid = None
        self.tables = []
        self.figures = []
        title, abstract, status = self.get_pubmed_abs(pmid)
        self.abstract = abstract
        if self.pmcid:
            print "pmc", self.pmcid
            self.get_pmc_captions()
        super(PubmedDocument, self).__init__(title + "\n" + abstract, ssplit=True, title=title,
                                             did="PMID" + pmid, **kwargs)

    def get_pubmed_abs(self, pmid):
        logging.info("gettting {}".format(pmid))
        #conn = httplib.HTTPConnection("eutils.ncbi.nlm.nih.gov")
        #conn.request("GET", '/entrez/eutils/efetch.fcgi?db=pubmed&id={}&retmode=xml&rettype=xml'.format(pmid))
        payload = {"db": "pubmed", "id": pmid, "retmode": "xml", "rettype": "xml"}
        try:
            r = requests.get('http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi', payload)
        except requests.exceptions.ConnectionError:
            r = requests.get('http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi', payload)
        # logging.debug("Request Status: " + str(r.status_code))
        response = r.text
        # logging.info(response)
        title, abstract = self.parse_pubmed_xml(response, pmid)
        return title, abstract, str(r.status_code)

    
    def parse_pubmed_xml(self, xml, pmid):
        if xml.strip() == '':
            print "PMID not found", pmid
            sys.exit()
        else:
            root = ET.fromstring(xml.encode("utf-8"))
            title = root.find('.//ArticleTitle')
            if title is not None:
                title = title.text
            else:
                title = ""
            abstext = root.findall('.//AbstractText')
            if abstext is not None and len(abstext) > 0:
                abstext = [a.text for a in abstext]
                if all([abst is not None for abst in abstext]):
                    abstext = '\n'.join(abstext)
                else:
                    abstext = ""
            else:
                print "Abstract not found:", title, pmid
                print xml[:50]
                abstext = ""
                #print xml
                #sys.exit()
            articleid = root.findall('.//ArticleId')
            for a in articleid:
                if a.get("IdType") == "pmc":
                    self.pmcid = a.text[3:]
        return title, abstext

    def get_pmc_captions(self):
        payload = {"db": "pmc", "id": self.pmcid, "tool": "ibent", "email": "alamurias@lasige.di.fc.ul.pt"}
        try:
            r = requests.get('http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi', payload)
        except requests.exceptions.ConnectionError:
            r = requests.get('http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi', payload)
        # logging.debug("Request Status: " + str(r.status_code))
        response = r.text
        root = ET.fromstring(response.encode("utf-8"))
        tables = root.findall('.//table-wrap')
        figures = root.findall('.//fig')
        for t in tables:
            caption = ''.join(ET.tostring(e) for e in t.find("caption"))
            content = ''.join(ET.tostring(e) for e in t.find("table"))
            table = {"caption": caption, "content": content}
            self.tables.append(table)
        for f in figures:
            caption = ''.join(ET.tostring(e) for e in f.find("caption"))
            figure = {"caption": caption}
            self.figures.append(figure)

    
def main():
    pubmeddoc = PubmedDocument(sys.argv[1])
    print pubmeddoc

    
if __name__ == "__main__":
    main()
    