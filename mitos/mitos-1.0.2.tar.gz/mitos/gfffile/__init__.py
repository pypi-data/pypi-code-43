'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).
'''

from sys import stdout

def gffwriter( featurelist, acc, outfile = None, mode = "w" ):
    """
	write the gff string for each feature 
	@param[in] featurelist a list of features to be written
    @param[in] acc string to be prepended to each line (e.g. accession)
    @param[in] outfile file to write into, if None: write to stdout 
    @param[in] mode file write mode, e.g. a, w, ... 
	"""

    featurelist.sort( key = lambda x:x.start )

    if isinstance( outfile, str ):
        file = open( outfile, mode )
        for feature in featurelist:
            file.write( "%s\n" % feature.gffstr( acc ) )
        file.close()
    elif outfile == None:
        for feature in featurelist:
            stdout.write( "%s\n" % feature.gffstr( acc ) )
    else:
        for feature in featurelist:
            outfile.write( "%s\n" % feature.gffstr( acc ) )

