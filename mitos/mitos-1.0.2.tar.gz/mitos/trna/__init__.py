'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).
'''

from Bio import Alphabet
from Bio import Data

from ..sequence import sequence
from ..rna.vienna import RNAeval

trna_nameaamap = {'Ala':'A', 'Arg':'R', 'Asn':'N', 'Asp':'D', 'Cys':'C', 'Glu':'E', 'Gln':'Q', 'Gly':'G', \
        'His':'H', 'Ile':'I', 'Leu':'L', 'Lys':'K', 'Met':'M', 'Phe':'F', 'Pro':'P', 'Ser':'S', 'Thr':'T', \
        'Trp':'W', 'Tyr':'Y', 'Val':'V' }

class CodonError( Exception ):
    def __init__( self, value ):
        self.value = value
    def __str__( self ):
        return "Invalid Anticodon / Codon " + self.value


# note for codons
# annotated strand     : codon
# mRNA                 : codon

# tRNA                 : anticodon
# sense strand tRNAgene: anticodon !!!

# in the code table also the codon is given
class codon( sequence ):
    def __init__( self, seq, type ):
        """
        init a codon from codon / anticodon sequence
        \param seq a D/RNA sequence of length 3 (a string)
        \param type specify if seq is the codon or anticodon 
        """

        # codon must be of length 3
        if len( seq ) != 3:
            raise CodonError, seq

        # print "codon init", type, seq,
        # replace possible Us .. this is unfortunately inconsistent
        # in the genbankfile .. but be want to have it as DNA .. so ..
        seq = seq.replace( "U", "T" ).replace( "u", "t" )
        if type == "anticodon":
            seq = str( sequence( seq, circular = False, alphabet = Alphabet.IUPAC.ambiguous_dna, upper = True ).reverse_complement() )

        elif type != "codon":
            raise "InvalidType", "Invalid type " + str( type )

        sequence.__init__( self, seq, circular = False, alphabet = Alphabet.IUPAC.ambiguous_dna, upper = True )

    def get_anticodon( self ):
        """
        return the anticodon as string
        """
        return str( self.reverse_complement() )

    def get_codon( self ):
        """
        return the codon as string
        """
        return str( self._data )

    def get_aa( self, transl_table ):
        """
        determine for which aminoacid the stored codon codes
        @param[in] transl_table int
        @return - the corresponding aa
            - '*' for stop codons
            - '?' else
        """
        # print "get_aa", str(self)

        table = Data.CodonTable.unambiguous_dna_by_id[transl_table]
        aa = ""

        if self._data in table.forward_table:
            return table.forward_table[ self._data ]

#        if self._data in table.start_codons:
#            aa += "start"

        if self._data in table.stop_codons:
            return '*'

        return '?'

    def isstart( self, transl_table ):
        """
        check if the codon is a start codon
        """

        table = Data.CodonTable.unambiguous_dna_by_id[transl_table]
        if self.data in table.start_codons:
            return True
        else:
            return False

    def isstop( self, transl_table ):
        """
        check if the codon is a stop codon
        """

        table = Data.CodonTable.unambiguous_dna_by_id[transl_table]
        if self.data in table.stop_codons:
            return True
        else:
            return False

def threetoone( name ):
    """
    function for determining the one letter name for a trna given in the three letter representation
    \param name the three letter representation
    \return the upper case one letter representation or None if invalid name is given
    """

    return trnamappings.tto.get( name.upper() )

L1 = codon( "CTN", "codon" )
L2 = codon( "TTR", "codon" )

S1 = codon( "AGN", "codon" )
S2 = codon( "TCN", "codon" )
