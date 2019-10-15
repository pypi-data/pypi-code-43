'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).
'''

from sys import stdout

from ..feature import feature, trnafeature
from ..gb import gb
from .. import trna

def mitowriter( featurelist, acc, outfile, mode = "w" ):

    featurelist.sort( key = lambda x:x.start )

    if isinstance( outfile, str ) or isinstance( outfile, unicode ):
        f = open( outfile, mode )
        for feature in featurelist:
            f.write( "%s\n" % feature.mitostr( acc ) )
        f.close()
    elif outfile == None:
        for feature in featurelist:
            stdout.write( "%s\n" % feature.mitostr( acc ) )
    else:
        for feature in featurelist:
            outfile.write( "%s\n" % feature.mitostr( acc ) )

class mitofromfile( gb ):

    def __init__( self, mitofile ):
        gb.__init__( self )

        mitohandle = open( mitofile )
        for line in mitohandle:
            line = [x.strip() for x in line.split()]
            # ACC    type    name    method    start    stop    strand    score(punkt falls nicht da)    anticodon(- falls nicht trna)    part(. falls nicht da)    copy(. falls nicht da)
            self.accession = line[0]
            type = line[1]
            name = line[2]
            method = line[3]
            start = int( line[4] )
            stop = int( line[5] )
            strand = int( line[6] )
            if line[7] == ".":
                score = None
            else:
                score = float( line[7] )
            if line[8] == "-":
                anticodon = None
            else:
                anticodon = trna.codon( line[8], "anticodon" )

            if len( line ) >= 12 and line[11] != ".":
                structure = line[11]
            else:
                structure = None

            if len( line ) >= 13 and line[12] != ".":
                acp = line[12]
            else:
                acp = None

            if type == "tRNA" or type == "rRNA":
                nf = trnafeature( name = name, type = type, start = start, \
                                 stop = stop, strand = strand, method = method, \
                                 score = score, sequence = None, \
                                 struct = structure, anticodonpos = acp, \
                                 anticodon = anticodon, evalscore = score )
            else:
                nf = feature( name = name, type = type, method = method, \
                          start = start, stop = stop, \
                          strand = strand, score = score, anticodon = anticodon )

            if line[9] != ".":
                nf.part = int( line[9] )
            if line[10] != ".":
                nf.copy = int( line[10] )

            self.features.append( nf )
        mitohandle.close()
