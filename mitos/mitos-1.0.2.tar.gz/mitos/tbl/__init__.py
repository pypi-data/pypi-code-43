'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).
'''

import re
from sys import stdout

from Bio import Data

from ..feature import feature
from ..gb import gb
from ..gb.unify import unify_name_protein, unify_name_trna, unify_name_rrna, unify_name_origin
from ..trna import codon, CodonError, L1, L2, S1, S2


class tblfromfile( gb ):
    def __init__( self, tblfile ):
        """
        tbl Parser that reads at least the files from MitoAnnotator
        
        @param[in] tblfile filename string 
        """
        gb.__init__( self )

        position = None  # is None until 1st feature
        name = None
        tpe = None

        tblhandle = open( tblfile )
        for line in tblhandle:
#             print line
            line = line.strip().split()

            if "TOPOLOGY" in line:
                if line[-1] == "circular":
                    self.circular = True
                else:
                    self.circular = False
#                 print "circular", self.circular

            if "organism" in line:
                line = line[-1].split( "_" )
                self.accession = "_".join( line[0:2] )
                self.name = " ".join( line[2:] )
#                 print "acc ", self.accession
#                 print "name ", self.name

            if "source" in line:
                self.size = self._parse_feature_location( line[1] )[1]
#                 print "size", self.size

            if ( "CDS" in line ) or ( "rRNA" in line ) or ( "tRNA" in line ) or ( "D-loop" in line ):
                if position != None:
                    self.features.append( feature( name, tpe, position[0], position[1], position[2], "tbl", "" ) )
#                     print "==>", self.features[-1].bedstr( self.accession )

                position = self._parse_feature_location( line[1] )
                if line[0] == "CDS":
                    tpe = "gene"
                else:
                    tpe = line[0]
                line = line[2:]


                # TODO add feature if not first
            if "product" in line or ( tpe == "D-loop" and "note" in line ):
                name = self._parse_feature_name( tpe, " ".join( line[1:] ), position[2] )
#                 print name

            if "note" in line:
                c = self._parse_feature_codon( " ".join( line[1:] ) )
                if c != None:
                    if name == "trnL" and c == L1:
                        name = "trnL1"
                    elif name == "trnL" and c == L2:
                        name = "trnL2"
                    elif name == "trnS" and c == S1:
                        name = "trnS1"
                    elif name == "trnS" and c == S2:
                        name = "trnS2"

        if position != None:
            self.features.append( feature( name, tpe, position[0], position[1], position[2], "tbl", "" ) )
#             print "==>", self.features[-1].bedstr( self.accession )

#         self.comment = ""
#         self.commonname = ""
#         self.complete = False
#         self.data_file_division = ""  # INV MAM PRI ROD VRT
#         self.date = ""
#         self.references = []  # list of references .. use biopython class
#             # data members: number, bases, authors, consrtm, title, journal, medline_id, pubmed_id, remark
#         self.sequence = ""
#         self.taxid = None
#         self.taxonomy = []  # taxonomy list
#         self.transl_table = 0
#         self.version = 0

    def _parse_feature_location( self, location ):
        """
        """

        if location.startswith( "complement(" ):
            location = location[11:-1]
            strand = -1
        else:
            strand = 1

        location = location.split( ".." )
        start = int( location[0] ) - 1
        stop = int( location[1] ) - 1

        return ( start, stop, strand )

    def _parse_feature_name( self, tpe, name, strand ):
        """
        try to determine the name of a feature from the product qualifier
        @param[in] f the feature
        @param[in] strand the strand of the featuunify_name_originre
        @return the name of None (if could not be determined)
        """

        if tpe == "gene":
            return unify_name_protein( name )
        elif tpe == "tRNA":
            return unify_name_trna( name )
        elif tpe == "rRNA":
            return unify_name_rrna( name )
        elif tpe == "D-loop":
            return unify_name_origin( name, strand )
        else:
            raise Exception( "Unknown type" )

    def _parse_feature_codon( self, note ):
        """
        
        """
        m = re.search( "([U%s]{3})" % Data.IUPACData.ambiguous_dna_letters, note )
        if m != None:
            return codon( m.group( 1 ), "anticodon" )
        else:
            return None




def tblwriter( featurelist, acc, outfile = None, mode = "w" ):
    out = ">Feature %s\n" % acc
    featurelist.sort( key = lambda x:x.start )
    for feature in featurelist:
        out += feature.tblstr()

    if isinstance( outfile, str ):
        file = open( outfile, mode )
        file.write( out )
        file.close()
    elif outfile == None:
        stdout.write( out )
    else:
        outfile.write( out )
