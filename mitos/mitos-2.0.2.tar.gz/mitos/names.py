'''
Created on Apr 12, 2016

get full names of all features

@author: maze
'''
from Bio import SeqIO

import sys

def parse( record ):
    # print( "%s %i" % ( record.id, len( record ) ) )

    locations = {}

    for f in record.features:
        if not f.type in ["tRNA", "tmRNA", "rRNA", "ncRNA", "gene", "CDS"]:
            continue

        l = ( f.location.start.position, f.location.end.position )
        if not f.location in locations:
            locations[l] = set()

        for q in f.qualifiers:
            if q in ["gene", "product", "gene_synonym"]:
                for x in f.qualifiers[q]:
                    locations[l].add( x )

    for l in locations:
        print(";".join( locations[l] ))

if __name__ == '__main__':
    for record in SeqIO.parse( sys.argv[1], 'genbank' ):
        parse( record )
    pass
