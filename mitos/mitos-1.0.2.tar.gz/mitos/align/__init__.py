'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).
'''

# path to water binary
WATER = "/usr/bin/water"



class alignment:
    """
    base class for a pairwise alignment
    derived classes mist implement a align member function
    """


    def __init__( self, aln1seq, aln2seq, aln1start, aln1stop, aln2start, aln2stop ):
        """
        
        """

        self.seq1 = aln1seq
        self.start1 = aln1start
        self.stop1 = aln1stop

        self.seq2 = aln2seq
        self.start2 = aln2start
        self.stop2 = aln2stop

        return

    def __str__( self ):
        """
        
        """

        mm = []
        for i in range( len( self.seq1 ) ):
            if self.seq1[i] == self.seq2[i]:
                mm.append( '|' )
            else:
                mm.append( ' ' )

        return """%s %d - %d
%s 
%s %d - %d""" % ( self.seq1, self.start1, self.stop1, "".join( mm ), self.seq2, self.start2, self.stop2 )

