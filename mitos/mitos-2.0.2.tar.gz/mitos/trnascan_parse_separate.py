
from os import listdir
from os.path import isfile, join
import os
from trna.trnascan import trnascan, parse
from feature import trnafeature
from trna import trna_nameaamap, L1, L2, S1, S2, codon
from Bio.Data.IUPACData import ambiguous_dna_values
import sys
import logging

def tRNAscan_parse( trnascan_file, outfile ):

    """
    Parse tRNAscan tabular output -- the one without secondary structure
    This script takes as parameter the directory that contains all tRNAscan output files
    """
    fh = open( trnascan_file, "r" )  # ## the tRNAscan output file as input
    trnas = {}

    intronstart = 0
    intronstop = 0
    skip = False
    start = None
    stop = None
    strand = None
    score = None
    seq = None
    dotbracket = None
    name = None
    anticodonpos = None
    anticodon = None

    for l in fh.readlines():
        if l.startswith( "Sequence" ) or l.startswith( "Name" ) or l.startswith( "--" ):
            continue

        l = l.lstrip().rstrip().split()
        # empty line marks start of a new feature

        if l[5] == "???":
            continue
        # if l[0].startswith('NC_'): #USE THIS LINE
        if l[0].startswith( 'NC_' ) or l[0].startswith( 'As_mt_' ) or l[0].startswith( 'Bc_mt' ) or l[0].startswith( 'Ec1-6' ) or l[0].startswith( 'Gg_cons' ) or l[0].startswith( 'Hf_mt' ) or l[0].startswith( 'On_mt' ):
#            number = l[0].split( '.' )[-1][4:]

            # trnascan: positions are counted from 1 the first and the last
            # position belongs to the trna
            acc = l[0].split( "_" )[0] + "_" + l[0].split( "_" )[1]
            start = int( l[2] ) - 1
            stop = int( l[3] ) - 1

            # is start < stop then the sequence if on the reverse complement
            if start > stop:
                start, stop = stop, start
                strand = -1
            else:
                strand = 1

            anticodon = codon( l[5], "anticodon" )
            # anticodonpos = int( l[5].split( '-' )[0] )
            code = None
            if code != None:
                name = anticodon.get_aa( code )
            else:
                if l[4] in trna_nameaamap:
                    name = trna_nameaamap[l[4]]
                else:
                    name = l[4]

            score = float( l[8] )

            if name == "S":
                if  anticodon == S1:
                    name = "S1"
                elif anticodon == S2:
                    name = "S2"
                else:
                    name = "S"
                    logging.warning( "warning non standard Ser %s" % l[3] )

            if name == "L":
                if anticodon == L1:
                    name = "L1"
                elif anticodon == L2:
                    name = "L2"
                else:
                    name = "L"
                    logging.warning( "warning non standard Leu %s" % l[3] )

        if not acc in trnas:
            trnas[acc] = {}
        trnas[acc]["name"] = name
        trnas[acc]["start"] = start
        trnas[acc]["stop"] = stop
        if strand == -1:
            trnas[acc]["strand"] = "-"
        else:
            trnas[acc]["strand"] = "+"
        trnas[acc]["anticodon"] = anticodon
        trnas[acc]["score"] = score
        # print acc, name, start, stop, strand, anticodon,score
            # continue
    outname = sys.argv[1].split( "/" )[-1].split( "." )[0]


    for acc in trnas:
        print(acc + "\t" + str( trnas[acc]["start"] ) + "\t" + str( trnas[acc]["stop"] ) + "\t trn" + trnas[acc]["name"] + "(" + str( trnas[acc]["anticodon"].lower().reverse_complement() ) + ")\t" + str( trnas[acc]["score"] ) + "\t" + str( trnas[acc]["strand"] ))
        outfile.write( acc + "\t" + str( trnas[acc]["start"] ) + "\t" + str( trnas[acc]["stop"] ) + "\t trn" + trnas[acc]["name"] + "(" + str( trnas[acc]["anticodon"].lower().reverse_complement() ) + ")\t" + str( trnas[acc]["score"] ) + "\t" + str( trnas[acc]["strand"] ) + "\n" )
        # print acc+"\t"+str(trnas[acc]["start"])+"\t"+str(trnas[acc]["stop"])+"\t trn"+trnas[acc]["name"]+"("+trnas[acc]["anticodon"].lower().reverse_complement()+")\t"+str(trnas[acc]["score"])

    fh.close()


tRNAs = ["trnS1", "trnF", "trnD", "trnY", "trnS2", "trnL1", "trnL2", "trnH", "trnI", "trnM", "trnN", "trnC", "trnE", "trnP", "trnQ", "trnR", "trnT", "trnW", "trnK", "trnA", "trnG", "trnV"]

trnascan_out_path = sys.argv[1]

for g in tRNAs:
    outfile = open( "/home/wi93jaj/Documents/Work/MITOS/ncRNAs_171214/Fungi/tRNAscan/bedfiles/" + g + ".bed", "a" )
    mypath = trnascan_out_path + g
    trnascan_files = [ os.path.join( mypath, f ) for f in listdir( mypath ) if isfile( join( mypath, f ) ) ]
    for f in trnascan_files:
        i = 0
        print(f)
        test = open( f, "r" )  # # test if file contains only comments before calling the function
        for l in test:
            if not l.startswith( "#" ):
                i = 1
        test.close()
        if i == 1:
            tRNAscan_parse( f, outfile )
    outfile.close()




















