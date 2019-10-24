#Matching the given ids to regex to identify them
import re, sys
import annofetch.lib.type as type

""" The different patterns of the accession for UniProtKB, Embl/NCBI/DDBJ,
HGNC or GI-Numbers.
NCBI/EMBL/DDBJ: https://www.ncbi.nlm.nih.gov/Sequin/acc.html
UniProtKB: https://www.uniprot.org/help/accession_numbers
"""
""" UniProtKB Accession """
uniprot_pattern = '[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}'

uniprot_fasta_prefix = '((sp|tr)\|)?'

uniprot_search_pattern = uniprot_fasta_prefix + uniprot_pattern

uniprot = re.compile(uniprot_pattern)
uniprot_search = re.compile(uniprot_search_pattern)

""" NCBI/Embl/DDBJ Accession """
nucleotide_pattern = '([A-Z][0-9]{5}|[A-Z]{2}[0-9]{6}([A-Z]{2})?(\.[0-9]*)?)'
protein_pattern = '([A-Z]{3}[0-9]{5}([0-9]{2})?(\.[0-9]*)?)'
#wgs_pattern = '[A-Z]{4}[0-9]{8}[0-9]*|[A-Z]{6}[0-9]{9}[0-9]*'
#mga_pattern = '[A-Z]{5}[0-9]{7}'
accession_fasta_prefix = '((embl|gb|dbj)\|)?'

genbank_pattern = nucleotide_pattern + '|' + protein_pattern
genbank = re.compile(genbank_pattern)

genbank_search_pattern = accession_fasta_prefix + '(' + genbank_pattern + ')'
genbank_search = re.compile(genbank_search_pattern)

""" GI-number """
gi = re.compile('gi\|[0-9]{1,}')

""" HGNC Accession """
hgnc_or_gi = re.compile('[0-9]{1,}')

"""
Match the example id to one of the accession patterns
"""
def which_accession(id):

    if uniprot_search.match(id):
        return type.uniprot
    elif genbank_search.match(id):
        return type.accession
    elif gi.match(id):
        return type.gi
    elif hgnc_or_gi.match(id):
        return type.hgnc_or_gi
    else:
        return type.none

def get_uniprot_accession(id):
    match = uniprot.search(id)
    if match:
        return match.group(0)
    else:
        return None

def get_accession(id):
    match = genbank.search(id)
    if match:
        return match.group(0)
    else:
        return None

def get_gi_or_hgnc(id):
    match = hgnc_or_gi.search(id)
    if match:
        return match.group(0)
    else:
        return None

"""
Match the optionally given flag to the status types.
"""
def which_flag(args):

    if args.accession:
        return type.accession
    elif args.uniprot:
        return type.uniprot
    elif args.gi:
        return type.gi
    elif args.hgnc:
        return type.hgnc
    else:
        return type.none

def shorten_descr(descr, organism):
    raw = re.escape(organism)
    short = re.sub(raw, '', descr)
    return short.strip()
