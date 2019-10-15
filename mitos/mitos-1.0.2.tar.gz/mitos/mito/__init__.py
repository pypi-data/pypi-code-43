'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).

This module provides some useful things for mitochondrial genomes
'''

# list of the default tRNA names
dtrna = ["trnA", "trnC", "trnD", "trnE", "trnF", "trnG", "trnH", "trnI", \
         "trnK", "trnL1", "trnL2", "trnM", "trnN", "trnP", "trnQ", "trnR", \
         "trnS1", "trnS2", "trnT", "trnW", "trnY", "trnV"]

# list of all possible tRNA names
trna = dtrna + ["trnL", "trnS", "trnX"]

# list of tRNA names
trnamap = {'ALA':'trnA', 'ARG':'trnR', 'ASN':'trnN', 'ASP':'trnD', 'CYS':'trnC', \
           'GLN':'trnQ', 'GLU':'trnE', 'GLY':'trnG', 'HIS':'trnH', 'ILE':'trnI', \
           'LEU':'trnL', 'LEU1':'trnL1', 'LEU2':'trnL2', 'LYS':'trnK', \
           'MET':'trnM', 'PHE':'trnF', 'PRO':'trnP', 'SER':'trnS', \
           'SER1':'trnS1', 'SER2':'trnS2', 'THR':'trnT', 'TRP':'trnW', 'TYR':'trnY', \
           'VAL':'trnV', 'UNK':'trnX'}

revtrnamap = lambda smallname:[longname for longname in trnamap if trnamap[longname] == smallname][0]

# list of rRNAs
rrna = ["rrnS", "rrnL"]

rrnamap = {"rrnS":"s", "rrnL":"l"}

# list of protein coding genes
dprot = ['cox1', 'cox2', 'cox3', 'cob', 'atp6', 'atp8', 'nad1', \
        'nad2', 'nad3', 'nad4', 'nad4l', 'nad5', 'nad6']

prot = dprot + ['atp9']


revprot = {"cox1":"cytochrome c oxidase subunit 1", \
           "cox2":"cytochrome c oxidase subunit 2", \
           "cox3":"cytochrome c oxidase subunit 3", \
           "cob":"cytochrome b", \
           "nad1":"NADH dehydrogenase subunit 1", \
           "nad2":"NADH dehydrogenase subunit 2", \
           "nad3":"NADH dehydrogenase subunit 3", \
           "nad4":"NADH dehydrogenase subunit 4", \
           "nad4l":"NADH dehydrogenase subunit 4L", \
           "nad5":"NADH dehydrogenase subunit 5", \
           "nad6":"NADH dehydrogenase subunit 6", \
           "atp6":"ATP synthase F0 subunit 6", \
           "atp8":"ATP synthase F0 subunit 8", \
           "atp9":"ATP synthase F0 subunit 9"}

#        'COX1':'gene', 'COX2':'gene', \
#        'COX3':'gene', 'ATP6':'gene', 'ATP8':'gene', 'ATP9':'gene', \
#        'CYTB':'gene', 'ND1':'gene', 'ND2':'gene', 'ND3':'gene', \
#        'ND4':'gene', 'ND4L':'gene', 'ND5':'gene', 'ND6':'gene', \
#        'OH':'rep_origin', 'OL':'rep_origin', \
#         '12S':'rRNA', '16S':'rRNA',
#        'A':'tRNA', 'C':'tRNA', 'D':'tRNA', 'E':'tRNA', 'F':'tRNA', \
#        'G':'tRNA', 'H':'tRNA', 'I':'tRNA', 'K':'tRNA', 'L':'tRNA', \
#        'L1':'tRNA', 'L2':'tRNA', 'M':'tRNA', 'N':'tRNA', 'P':'tRNA', \
#        'Q':'tRNA', 'R':'tRNA', 'S':'tRNA', 'S1':'tRNA', 'S2':'tRNA', \
#        'T':'tRNA', 'V':'tRNA', 'W':'tRNA', 'X':'tRNA', 'Y':'tRNA', \

rep_origin = ["OH", "OL"]

types = {}
for t in trna:
    types[t] = "tRNA"
for t in rrna:
    types[t] = "rRNA"
for t in prot:
    types[t] = "gene"
for t in rep_origin:
    types[t] = "rep_origin"

# types = {\
#        'rrnS':'rRNA', 'rrnL':'rRNA', 'cox1':'gene', 'cox2':'gene', \
#        'cox3':'gene', 'atp6':'gene', 'atp8':'gene', 'atp9':'gene', \
#        'cob':'gene', 'nad1':'gene', 'nad2':'gene', 'nad3':'gene', \
#        'nad4':'gene', 'nad4l':'gene', 'nad5':'gene', 'nad6':'gene', \
#        'trnA':'tRNA', 'trnC':'tRNA', 'trnD':'tRNA', 'trnE':'tRNA', 'trnF':'tRNA', \
#        'trnG':'tRNA', 'trnH':'tRNA', 'trnI':'tRNA', 'trnK':'tRNA', 'trnL':'tRNA', \
#        'trnL1':'tRNA', 'trnL2':'tRNA', 'trnM':'tRNA', 'trnN':'tRNA', 'trnP':'tRNA', \
#        'trnQ':'tRNA', 'trnR':'tRNA', 'trnS':'tRNA', 'trnS1':'tRNA', 'trnS2':'tRNA', \
#        'trnT':'tRNA', 'trnV':'tRNA', 'trnW':'tRNA', 'trnY':'tRNA', 'trnX':'tRNA', \
#        }

# list of all genes
gene = trna + rrna + prot

