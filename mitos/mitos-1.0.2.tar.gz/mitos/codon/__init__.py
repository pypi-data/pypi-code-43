'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).
'''
import os

def parsecodon( code ):
    """
    parse start and stop codons from the ncbi code table 
    @param code genetic code identifier
    @return list of length two containing start and stop codons
    """

    # TODO check if in biopython version > 1.52 the most up to date
    # genetic code is included in biopython
    # currently it isnt
    # if so then remove this function, i.e. use Bio.Data.CodonTable
    # see comments in blast/findstart


    file = open( os.path.join( os.path.dirname( __file__ ), '..', "codons", "gc.prt"), "r" )
    lines = file.readlines()
    file.close()
    start = []
    stop = []
    for i in range( len( lines ) ):
        line = lines[i]
        # get the lines corresponding to code
        if line.strip( " ,\n\r" ).startswith( "id" ) and line.strip( " ,\n\r" ).split()[-1] == str( code ) :
            for k in range( len( lines[i + 1] ) ):
                if lines[i + 1][k] == "*":
                    stop.append( lines[i + 3][k] + lines[i + 4][k] + lines[i + 5][k] )
#                elif lines[i+1][k] == "M":
#                    start.append(lines[i+3][k]+lines[i+4][k]+lines[i+5][k])
                elif k < len( lines[i + 2] ) and lines[i + 2][k] == "M":
                    start.append( lines[i + 3][k] + lines[i + 4][k] + lines[i + 5][k] )
            return ( start, stop )

    return ( None, None )

