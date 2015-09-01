# coding=utf-8
from __future__ import division, unicode_literals
import sys

__author__ = 'Andre'
import requests

#payload = {'key1': 'value1', 'key2': 'value2'}


def main():
    if sys.argv[1] == "1":
        text = "Primary Leydig cells obtained from bank vole testes and the established tumor Leydig cell line (MA-10) have been used to explore the effects of 4-tert-octylphenol (OP). Leydig cells were treated with two concentrations of OP (10(-4)M, 10(-8)M) alone or concomitantly with anti-estrogen ICI 182,780 (1M). In OP-treated bank vole Leydig cells, inhomogeneous staining of estrogen receptor (ER) within cell nuclei was found, whereas it was of various intensity among MA-10 Leydig cells. The expression of ER mRNA and protein decreased in both primary and immortalized Leydig cells independently of OP dose. ICI partially reversed these effects at mRNA level while at protein level abrogation was found only in vole cells. Dissimilar action of OP on cAMP and androgen production was also observed. This study provides further evidence that OP shows estrogenic properties acting on Leydig cells. However, its effect is diverse depending on the cellular origin. "
    elif sys.argv[1] == "2":
        text = "Azole class of compounds are well known for their excellent therapeutic properties. Present paper describes about the synthesis of three series of new 1,2,4-triazole and benzoxazole derivatives containing substituted pyrazole moiety (11a-d, 12a-d and 13a-d). The newly synthesized compounds were characterized by spectral studies and also by C, H, N analyses. All the synthesized compounds were screened for their analgesic activity by the tail flick method. The antimicrobial activity of the new derivatives was also performed by Minimum Inhibitory Concentration (MIC) by the serial dilution method. The results revealed that the compound 11c having 2,5-dichlorothiophene substituent on pyrazole moiety and a triazole ring showed significant analgesic and antimicrobial activity."
    elif sys.argv[1] == "3":
        text = "Primary Leydig cells obtained from bank vole testes and the established tumor Leydig cell line (MA-10) have been used to explore the effects of 4-tert-octylphenol (OP)."
    payload = {'ttt': text}
    r = requests.post('http://10.10.4.63:8080/iice/chemdner/{text}/all.json'.format(text=text), data=payload)
    print r.text

if __name__ == "__main__":
    main()