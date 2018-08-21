# coding=utf-8
from __future__ import division, unicode_literals
import sys
import requests
from timeit import default_timer as timer
import pprint
pp = pprint.PrettyPrinter(indent=4)

class bcolors:
    #http://stackoverflow.com/a/287944
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def main():
    if sys.argv[1] == '0':
        text = "Administration of a higher dose of indinavir should be considered when coadministering with megestrol acetate."
    elif sys.argv[1] == "1":
        text = "Primary Leydig cells obtained from bank vole testes and the established tumor Leydig cell line (MA-10) have been used to explore the effects of 4-tert-octylphenol (OP). Leydig cells were treated with two concentrations of OP (10(-4)M, 10(-8)M) alone or concomitantly with anti-estrogen ICI 182,780 (1M). In OP-treated bank vole Leydig cells, inhomogeneous staining of estrogen receptor (ER) within cell nuclei was found, whereas it was of various intensity among MA-10 Leydig cells. The expression of ER mRNA and protein decreased in both primary and immortalized Leydig cells independently of OP dose. ICI partially reversed these effects at mRNA level while at protein level abrogation was found only in vole cells. Dissimilar action of OP on cAMP and androgen production was also observed. This study provides further evidence that OP shows estrogenic properties acting on Leydig cells. However, its effect is diverse depending on the cellular origin. "
    elif sys.argv[1] == "2":
        text = "Azole class of compounds are well known for their excellent therapeutic properties. Present paper describes about the synthesis of three series of new 1,2,4-triazole and benzoxazole derivatives containing substituted pyrazole moiety (11a-d, 12a-d and 13a-d). The newly synthesized compounds were characterized by spectral studies and also by C, H, N analyses. All the synthesized compounds were screened for their analgesic activity by the tail flick method. The antimicrobial activity of the new derivatives was also performed by Minimum Inhibitory Concentration (MIC) by the serial dilution method. The results revealed that the compound 11c having 2,5-dichlorothiophene substituent on pyrazole moiety and a triazole ring showed significant analgesic and antimicrobial activity."
    elif sys.argv[1] == "3":
        text = "Primary Leydig cells obtained from bank vole testes and the established tumor Leydig cell line (MA-10) have been used to explore the effects of 4-tert-octylphenol (OP)."
    elif sys.argv[1] == "4":
        text = "Loss-of-function mutations in progranulin (GRN) cause ubiquitin- and TAR DNA-binding protein 43 (TDP-43)-positive frontotemporal dementia (FTLD-U), a progressive neurodegenerative disease affecting approximately 10% of early-onset dementia patients. Common variation in the miR-659 binding-site of GRN is a major risk factor for TDP43-positive frontotemporal dementia. In support of these findings, the neuropathology of homozygous rs5848 T-allele carriers frequently resembled the pathological FTLD-U subtype of GRN mutation carriers. "
    elif sys.argv[1] == "5":
        text = "Co-suppression of miR-221/222 cluster suppresses human glioma cell growth by targeting p27kip1 in vitro and in vivo."
    else:
        text = sys.argv[1]
    data = {"text": text, "format": "json"}
    start_total = timer()

    #r = requests.post('http://10.10.4.63:8080/iice/chemical/entities', json=data)

    # print bcolors.OKBLUE + "Submit new document" + bcolors.ENDC
    # start = timer()
    # r = requests.post('http://10.10.4.63:8080/ibent/DOC{}'.format(sys.argv[1]), json=data)
    # print r.url, ":", timer() - start
    # pp.pprint(r.json())

    # print bcolors.OKBLUE + "Fetch document" + bcolors.ENDC
    # start = timer()
    # r = requests.get('http://10.10.4.63:8080/ibent/DOC{}'.format(sys.argv[1]))
    # print r.url, ":", timer() - start
    # pp.pprint(r.json())
    #
    # print bcolors.OKBLUE + "Annotate miRNA" + bcolors.ENDC
    # start = timer()
    # r = requests.post('http://10.10.4.63:8080/ibent/entities/DOC{}/mirtex_train_mirna_sner'.format(sys.argv[1]))
    # print r.url, ":", timer() - start
    # pp.pprint(r.json())
    #
    # print bcolors.OKBLUE + "Annotate chemical" + bcolors.ENDC
    # start = timer()
    # r = requests.post('http://10.10.4.63:8080/ibent/entities/DOC{}/chemdner_train_all'.format(sys.argv[1]))
    # print r.url, ":", timer() - start
    # pp.pprint(r.json())
    #
    # print bcolors.OKBLUE + "Get chemicals" + bcolors.ENDC
    # start = timer()
    # r = requests.get('http://10.10.4.63:8080/ibent/entities/DOC{}/chemdner_train_all'.format(sys.argv[1]))
    # print r.url, ":", timer() - start
    # pp.pprint(r.json())
    #
    # print bcolors.OKBLUE + "Annotate gene/proteins" + bcolors.ENDC
    # start = timer()
    # r = requests.post('http://10.10.4.63:8080/ibent/entities/DOC{}/genia_sample_gene'.format(sys.argv[1]))
    # print r.url, ":", timer() - start
    # pp.pprint(r.json())
    #
    # print bcolors.OKBLUE + "Annotate DDI relations" + bcolors.ENDC
    # start = timer()
    # r = requests.post('http://10.10.4.63:8080/ibent/relations/DOC{}/all_ddi_train_slk'.format(sys.argv[1]))
    # print r.url, ":", timer() - start
    # #pp.pprint(r.json())
    # print r.text
    #
    # print bcolors.OKBLUE + "Get DDI relations" + bcolors.ENDC
    # start = timer()
    # r = requests.get('http://10.10.4.63:8080/ibent/relations/DOC{}/all_ddi_train_slk'.format(sys.argv[1]))
    # print r.url, ":", timer() - start
    # pp.pprint(r.json())
    # print r.text

    print bcolors.OKBLUE + "Get miRNA-gene relations" + bcolors.ENDC
    start = timer()
    r = requests.post('http://10.10.4.63:8080/ibent/relations/DOC{}/mil_classifier4k'.format(sys.argv[1]))
    print r.url, ":", timer() - start
    pp.pprint(r.json())
    #print r.text

    print "Total time:", timer() - start_total
    # if len(sys.argv) > 2 and sys.argv[2] == "int":
    #     data = r.json()
    #     headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    #     rel = requests.post('http://10.10.4.63:8080/iice/chemical/interactions', json=data)
    #     print
    #     print rel.json()


if __name__ == "__main__":
    main()