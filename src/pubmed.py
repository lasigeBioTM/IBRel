#!/usr/bin/env python
# -*- coding: utf-8 -*-
import httplib
#import xml.dom.minidom as minidom
#import urllib
import time, sys
import xml.etree.ElementTree as ET

def get_pubmed_abs(pmid):
    conn = httplib.HTTPConnection("eutils.ncbi.nlm.nih.gov")
    conn.request("GET", '/entrez/eutils/efetch.fcgi?db=pubmed&id=%s&retmode=xml&rettype=xml' % pmid)
    r1 = conn.getresponse()
    #print "Request Status: " + str(r1.status) + " " + str(r1.reason)
    response = r1.read()
    # print response
    title, abstract = parse_pubmed_xml(response)
    return title, abstract, str(r1.status) + ' ' + str(r1.reason)

    
def parse_pubmed_xml(xml):
    #print xml
    if xml.strip() == '':
        print "PMID not found"
        sys.exit()
    else:
        root = ET.fromstring(xml)
        title = root.findall('.//ArticleTitle').text
        abstext = root.findall('.//AbstractText')
        if len(abstext) > 0:
            abstext = abstext[0].text
        else:
            print "Abstract not found"
            sys.exit()
    return title, abstext
    
    
    
def main():
    print get_pubmed_abs(sys.argv[1])
    
if __name__ == "__main__":
    main()
    