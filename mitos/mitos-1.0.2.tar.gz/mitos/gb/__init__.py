'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).
'''

import re
import sys
import logging
from os.path import splitext
from Bio import GenBank
from Bio import SeqIO
from Bio.Alphabet import IUPAC
from Bio import Seq
from Bio import Data


from .. import feature
from .. import mito
from . import unify
from .. import sequence
from ..trna import codon, CodonError, L1, L2, S1, S2

class gb:
    def __init__( self ):

        self.accession = ""
        self.circular = False
        self.comment = ""
        self.commonname = ""
        self.complete = False
        self.data_file_division = ""  # INV MAM PRI ROD VRT
        self.date = ""
        self.features = []
        self.name = ""
        self.references = []  # list of references .. use biopython class
            # data members: number, bases, authors, consrtm, title, journal, medline_id, pubmed_id, remark
        self.sequence = ""
        self.size = 0
        self.taxid = None
        self.taxonomy = []  # taxonomy list
        self.transl_table = 0
        self.version = 0

        return

    def _add_feature( self, name, tpe, start, stop, strand, translation ):
        """
        add a feature ..  
        """
        nf = feature( name, tpe, start, stop, strand, "genBank", translation )
        self.features.append( nf )


    def abspre( self, genes ):
        """
        return a string describing the absence or presence of genes
        @param genes the genes to check for (a list of names)
        @return comma separated list giving the number of occurences of the genes (sorted by name)        
        """

        gdict = { }
        for g in genes:
            gdict[g] = 0

        for f in self.features:
            try:
                gdict[f.name] += 1
            except:
                gdict[f.name] = 1

        return ",".join( [ str( gdict[g] ) for g in sorted( genes ) ] )

    def dellowscoreparts( self ):
        """
        delete all parts except one of the same name (those with best score) 
        """

        bestscores = {}
        for f in self.features:
            if not f.name in bestscores  or ( ( f.type == "gene" and bestscores[f.name] < f.score ) or ( f.type != "gene" and bestscores[f.name] > f.score ) ):
                bestscores[f.name] = f.score

        i = 0
        while i < len( self.features ):
            if self.features[i].name in bestscores and bestscores[self.features[i].name] != self.features[i].score:
#                print self.features[i]
                del self.features[i]
            else:
                i += 1


    def getfeatures( self, anames = None, fnames = None, atypes = None, ftypes = None, astrand = None ):
        """
        get a list of features 
        \param anames list of allowed feature names (None: everything allowed)
        \param fnames list of forbidden feature names (None: nothing forbidden)
        \param atypes list of allowed feature types (None: everything allowed)
        \param ftypes list of forbidden feature types (None: nothing forbidden)
        \param astrand allowed strand (None: both strands allowed) 
        \return list of features
        """

        return [ x for x in self.features if x.is_allowed( anames, fnames, atypes, ftypes, astrand ) ]
        # return [ x for x in self.features if (x.name in name) or (x.type in name) ]

    def geneorder( self, anames = None, fnames = None, atypes = None, ftypes = None, signed = True ):
        """
        get the gene order as list
        \param atypes list of allowed feature types (None: everything allowed)
        \param ftypes list of forbidden feature types (None: nothing forbidden)
        \param signed make the gene order signed (default: True) 
        """

        features = self.getfeatures( anames = anames, fnames = fnames, atypes = atypes, ftypes = ftypes )
        order = []
        for f in features:
            if signed == True and f.strand < 0:
                order.append( "-" + f.name )
            else:
                order.append( f.name )
        return order

    def is_allowed( self, atax = None, ftax = None ):
        """
        checks if the gb file to certain taxonomic groups
        \param atax list of allowed taxonomic groups or a string of a group  
        \param ftax forbidden taxonomic groups 
        \return true iff gb in atax and gb not in ftax
        """

        if isinstance( atax, str ):
            atax = [atax]
        if isinstance( ftax, str ):
            ftax = [ftax]

        if atax != None and len( filter( lambda x:x in self.taxonomy, atax ) ) == 0:
            return False
        elif ftax != None and len( filter( lambda x:x in self.taxonomy, ftax ) ) > 0:
            return False

        return True

    def start_stop_subsequence( self, max = False ):
        """
        get (start,stop, strand) tuples of the sequence such that at start is a 
        start codon and at end a end codon
        \param max only return maximal sequences, i.e. if there are two sequences 
        (s1,e) and (s2,e) with s1<s2 then only (s1,e) will be returned
        """
        return self.sequence.start_stop_subsequence( self.transl_table, max )

class gbfromfile( gb ):
    def __init__( self, gbfile ):
        """
        @param gbfile: filename string 
        
        1. parse circular/linear (from residue_type)
           circular iff residue_type ends with "circular"
        2. parse accession and version (from accession, version, and locus)
           accession is taken directly, version is parsed from the string given 
           by accession.version, additional warnings are printed if the accession
           is not equal to the locus or the accession part of the version string
        3. parse the complete property and the name of the species 
           (from definition, organism, and source)
           - if definition contains the string "complete" the complete property is set
           - name is set to the content of organism
           - a warning is written if source does not start with 'mitochondrion '+name
           - if source ends with ')' then the common name is taken from the 
             parenthesised part
        4. size, comment, data_file_division, date, references, taxonomy  is taken directly 
           from the corresponding entries of the record
        5. sequence is taken directly from sequence with ambiguous DNA (IUPAC) alphabet
        6. transl_table is parsed from all features with a key "transl_table"
           - if not exactly one is found (but different or none) a warning is printed
           - the one of the found translation tables is returned
        7. the taxid is parsed from source feature (as the qualifier of the key db_xref)
        8. for each of features (parts):
        8a. the locations are parsed recursively given some string describing the location 
            and the currently active strand initialized to +1:
           - for a string join(x) or order(x) the method is recursively called 
             for each part of the contained comma separated list x (keeping the active strand as is)
           - for a string complement(x) the method is recursively called for x 
             (with the currently active strand inverted)
           - otherwise all numbers are parsed from the string and a position is added 
               on the currently active strand
             * if one number n is found a location [n,n]
             * if two numbers n,m are found a location [n,m] is added on 
             * otherwise an error message is printed
        8b. get the translation from the key "translation" as a linear sequence 
            with extended amino acid alphabet (IUPAC)
        8c. get a list of possible names 
            specialized methods for the extraction of the name of tRNA, rRNA, proteins, 
            and origins are applied on certain values (of key,value pairs) depending 
            on the feature type: 
            - qualifier key "gene" or "product" and feature type
              * feature type is "tRNA" or "gene"  -> tRNA function
              * feature type is "rRNA" or "gene"  -> rRNA function
              * feature type is "CDS" or "gene"  -> protein function
            - qualifier key "standard_name", "note", or "direction"
              * feature type either "rep_origin", "D-loop", "misc_feature"
            each function checks a list of regular expressions. if one matches the 
            corresponding name is appended to a list of possible names of the feature.
            - if the list has length 0 
              * if feature type is "rep_origin" or "D-loop" 
                -> OH is returned if strand is +1 and OL if it is -1
              * else None is returned
            - if the list is longer than 1 None is returned
            - if the list has length 1
              - if the name is L or S it is tries to parse the anticodon 
                from the feature to distinguish L1, L2, S1, S2
              the name is returned 
        8d. depending on the determined name the feature type is determined
        8e. if the feature part name could be determined  then the parts (all determined
            locations) are appended to the list of features as follows:
            - all previously added features of the same name are checked 
            i) if there is a feature which is included in the new feature then the 
              new feature is not added to the list (idea: we take the parts of the 
              features, instead of the complete one)
            ii) if there is a feature which is included the new one then the feature
              is deleted (and the new feature might be appended depending on 
               the following checks) 
            if all checks are done and i) never applied then the feature is added 
        """
        gb.__init__( self )

#        record = GenBank.RecordParser().parse( gbhandle )
        extparsemap = {'.gb':'genbank', '.gbk':'genbank', '.embl':'embl'}
        extension = splitext( gbfile )[1]
        if extension in extparsemap:
            parser = extparsemap[extension]
        else:
            raise Exception( "Unknown Extension", extension );
        gbhandle = open( gbfile, "r" )
        record = SeqIO.read( gbhandle, parser )
        gbhandle.close()
#        print dir( record )
#        print "annotations", record.annotations
#        print "dbxref", record.dbxrefs
#        print "descriptions", record.description

#        print "format", record.format
#        print "id", record.id
#        print "letter_annotations", record.letter_annotations
#        print "lower", record.lower
#        print "name", record.name
#        print "seq", record.seq
#        print "upper", record.upper


#        self._parse_circular( record.residue_type )

        logging.warning( "using True as default for circular" )
        self.circular = True
        self._parse_accession_version( record.annotations )
        # print self.accession

        self._parse_complete( record.description )
        self._parse_names( record.annotations )

        # size of the chromosome = length of the sequence
        # thus, sequence[size-1] gives the last element of the sequence
        self.size = int( len( record.seq ) )
        self.sequence = sequence( str( record.seq ), IUPAC.ambiguous_dna, self.circular )

        try:
            self.comment = record.annotations['comment']
        except:
            self.comment = ""

        self.data_file_division = record.annotations['data_file_division']
        try:
            self.date = record.annotations['date']
        except:
            self.date = ""

        self.references = record.annotations['references']


        self.taxonomy = record.annotations['taxonomy']

        # get the coding table

        self._parse_transl_table( record.features )

#        print "features", record.features

        _cpymap = {}

        for f in record.features:

            if f.type == "source":
                self._parse_source( f )
                continue

            # feature types found in metazoan gb files
            # - definitely of interest
            #    CDS
            #    * D-loop                displacement loop; a region within mitochondrial DNA in which a short stretch of RNA is paired with one strand of DNA, displacing the original partner DNA strand in this region; also used to describe the displacement of a region of one strand of duplex DNA by a single stranded invader in the reaction catalyzed by RecA protein
            #    gene                region of biological interest identified as a gene and for which a name has been assigned;
            #    * rRNA                mature ribosomal RNA; RNA component of the ribonucleoprotein particle (ribosome) which assembles amino acids into proteins.
            #     * rep_origin            origin of replication; starting site for duplication of nucleic acid to give two identical copies
            #    * tRNA                mature transfer RNA, a small RNA molecule (75-85 bases long) that mediates the translation of a nucleic acid sequence into an amino acid sequence;
            # - maybe of interest
            #    misc_feature        region of biological interest which cannot be described by any other feature key; a new or rare feature;
            #    repeat_region        region of genome containing repeating units;
            #    repeat_unit            single repeat element;
            #    source                identifies the biological source of the specified span of the sequence; this key is mandatory; more than one source key per sequence is allowed; every entry/record will have, as a minimum, either a single source key spanning the entire sequence or multiple source keys, which together, span the entire sequence.
            #    stem_loop            hairpin; a double-helical region formed by base-pairing between adjacent (inverted) complementary sequences in a single strand of RNA or DNA.
            # - most likely uninteresting
            #    3'UTR                region at the 3' end of a mature transcript (following the stop codon) that is not translated into a protein;
            #    conflict             independent determinations of the "same" sequence differ at this site or region;
            #    exon                region of genome that codes for portion of spliced mRNA, rRNA and tRNA; may contain 5'UTR, all CDSs and 3' UTR;
            #    gap                    gap in the sequence
            #    intron                a segment of DNA that is transcribed, but removed from within the transcript by splicing together the sequences (exons) on either side of it;
            #    misc_difference        feature sequence is different from that presented in the entry and cannot be described by any other Difference key (conflict, unsure, old_sequence, variation, or modified_base);
            #    promoter            region on a DNA molecule involved in RNA polymerase binding to initiate transcription;
            #    STS                    sequence tagged site; short, single-copy DNA sequence that characterizes a mapping landmark on the genome and can be detected by PCR; a region of the genome can be mapped by determining the order of a series of STSs;
            #    unsure                author is unsure of exact sequence in this region;
            #    variation            a related strain contains stable mutations from the same gene (e.g., RFLPs, polymorphisms, etc.) which differ from the presented sequence at this location (and possibly others);

#            print f

#            strand, start, stop = self._parse_feature_location( f.location )

            loc = self._parse_feature_locations( f )
            translation = self._parse_translation( f )
            copy = None

            for i in range( len( loc ) ):
                start = loc[i][0]
                stop = loc[i][1]
                strand = loc[i][2]

                name = self._parse_feature_name( f, strand )
                # anticodon = self._parse_feature_anticodon(f, strand)
                tpe = unify.feature_type( name )
#                 print "NAMETYPE", name, tpe
#                print name, "|", tpe, "|", f.type, "|",
#                try:
#                    print f.qualifiers["gene"], "|",
#                except:
#                    print "|",
#                try:
#                    print f.qualifiers["product"], "|",
#                except:
#                    print "|",
#                try:
#                    print f.qualifiers["standard_name"], "|",
#                except:
#                    print "|",
#                try:
#                    print f.qualifiers["note"], "|",
#                except:
#                    print "|",
#                try:
#                    print f.qualifiers["directon"], "|",
#                except:
#                    print "|",
# #                print
#                print self.accession

    #                print f.key, "name: ", name, type, strand, start, stop
                # ignore features if name or type could not be determined
                if name == None or tpe == None:
                    continue

                # ignore protein (related) features which are not CDS
                # like exons, introns, ...
                if name in mito.prot and f.type != "CDS":
                    continue

                if i == 0:
                    if not _name in cpymap:
                        _cpymap[name] = 0
                    else:
                        _cpymap[name] += 1

                nf = feature( name, tpe, start, stop, strand, "GenBank", translation )
#                print "===> ", nf

                if len( loc ) > 1:
                    nf.part = i

                if _cpymap[name] > 0:
                    nf.copy = _cpymap[name]

                self._add_smaller_feature( nf )

#            print "-----------------    "

                    # else:
                    #    print nf, "==", self.features[-1]

            # if name == None:
            #    if f.key in ["CDS","gene","tRNA"]:
            #        print f
            # print name, tpe
        # self._control_features()
        # print len(self.features)
        # if len(self.features) > 39:
        #    print self.accession, len(self.features)
        #    for f in self.features:
        #        print f

#        for f in self.features:
#            print f
        return

    def _add_smaller_feature( self, nf ):
        """
        add a feature: 
        - the feature is added if it does not include feature with the same 
          name and strand 
        - features that include the new feature are deleted
        
        the feature will be inserted such that the list of features is sorted in increasing order (by start positions) 
        """

#        print "add", nf
        i = 0
        while i < len( self.features ):
#            print i
            if not self.features[i].equal_name_type( nf ):
                i += 1
                continue

            if self.features[i].name != nf.name:
                if nf.name.startswith( self.features[i].name ):
                    self.features[i].name = nf.name
#                    print self.features[i].name, "<-", nf.name
                if self.features[i].name.startswith( nf.name ):
                    nf.name = self.features[i].name
#                    print nf.name, "<-", self.features[i].name

            cap, cup = self.features[i].capcup( nf, self.circular, self.size )
            # features[i] included in nf
            # => nf will not be inserted
            if cap == self.features[i].length( self.circular, self.size ) and \
                cup == nf.length( self.circular, self.size ):
#                print nf, "includes", self.features[i]
                return

            # nf included in features[i]
            # => features[i] will be deleted
            if cap == nf.length( self.circular, self.size ) and \
                cup == self.features[i].length( self.circular, self.size ):
#                print self.features[i], "includes", nf
                del self.features[i]
                continue

            # correct position is found
            if self.features[i].start > nf.start:
                break
            else:
                i += 1

        self.features.insert( i + 1, nf )
        return

    def _add_feature( self, nf ):
        """
        add a feature .. if the last feature added has the same name and 
        overlaps by more than 5% the features will be merged
        
        @param[in] nf a new feature 
        """

#

        # if name == "ND5":
        #   print name, type, start, stop, strand, translation
        # try to merge with existing feature with overlap and same name
        i = 0
        # print "len: ", len(self.features)
        while i < len( self.features ):
            # print self.features[i], nf, self.features[i].overlap(nf)
            # take the complement of the feature if the length of the feature
            # spans more than half of the genome

            # TODO do not compute here swap at initialisation of feature
            if abs( nf.stop - nf.start + 1 ) > self.size / 2:
                stop = nf.stop + self.size
            else:
                stop = nf.stop
            # print "stop: ", stop
            if stop + 1 < self.features[i].start:
                # print "break"
                i += 1
                continue

            # merge features if overlap of more than 5% with feature of same name and type
            # print "overlap: ", self.features[i].overlap(nf, size), "\tequal name: ", self.features[i].equal_name_type(nf)
            if self.features[i].equal_name_type( nf ) and self.features[i].overlap( nf, self.circular, self.size ) > 5:
#                print "overlap: ", nf, self.features[i]
                nf += self.features[i]
                del self.features[i]
                break
            i += 1

        # insert at a position such that the resulting feature list is sorted
        i = 0
        while i < len( self.features ):

            # TODO do not compute here swap at initialisation of feature
            if abs( self.features[i].stop - self.features[i].start ) > self.size / 2:
                start = self.features[i].start - self.size
            else:
                start = self.features[i].start

            if start >= nf.start:
                # print start, " >= ", nf.start
                break
            else:
                # print start, " < ", nf.start
                i += 1

        # print "insert at ",i+1
        self.features.insert( i + 1, nf )
        # print self.features
        # for f in self.features:
        #    print "\t",f
        return



    def _parse_accession_version( self, annotations ):
        """
        parse accession and version from the accession, version string
        """

        if len( annotations['accessions'] ) != 1:
            sys.stderr.write( "warning: accession list not of length 1\n" )
            sys.stderr.write( "         %s\n" % str( annotations['accessions'] ) )
            # sys.exit()

        self.accession = annotations['accessions'][0]

#        if self.accession != locus:
#            sys.stderr.write( "warning: accession (%s) != locus (%s)\n" % ( self.accession, locus ) )
#            #sys.exit()

        try:
            self.version = annotations['sequence_version']
        except:
            self.version = -1
#        m = re.match( "^([\w]{2}_{0,1}[\d]+)\.(\d+)$", version )
#        if m != None:
#            if m.group( 1 ) != self.accession:
#                sys.stderr.write( "error: accession in version string (%s) does not match accession (%s)\n" % ( version, self.accession ) )
#                #sys.exit()
#            self.version = int( m.group( 2 ) )
#        else:
#            sys.stderr.write( "error: version string (%s) does not match\n" % ( version ) )
#            sys.exit()

    def _parse_anticodon( self, v, strand ):
        """
        try to get a codon from value
        \return the anticodon
        """

        cdn = None
        nam = None

        v = v.upper()

        m = re.search( "POS:([\d]+)\.\.([\d]+),AA:(\w{3})", v )
        if m != None:
            s = int( m.group( 1 ) ) - 1
            e = int( m.group( 2 ) )
            try:
                cdn = codon( str( self.sequence.subseq( s, e, strand ) ), "anticodon" )
            except CodonError:
                # print "invalid codon", self.sequence.subseq(s, e, strand)
                pass
            nam = unify.unify_name_trna( m.group( 2 ) )

        m = re.match( "ANTICODON: ([U%s]{3})" % Data.IUPACData.ambiguous_dna_letters, v )
        if m != None:
            # seq = sequence(m.group(1), IUPAC.ambiguous_rna, circular=False).reverse_complement()
            # print "ac2 %s" %(seq)
            try:
                cdn = codon( m.group( 1 ), "anticodon" )
            except CodonError:
                # print "invalid codon", m.group(1)
                pass

        m = re.match( "^ANTICODON[ \s]{1,2}([U%s]{3}).*" % Data.IUPACData.ambiguous_dna_letters, v )
        if m != None:
            # seq = sequence(m.group(1), IUPAC.ambiguous_rna, circular=False).reverse_complement()
            # print "ac3 %s" %(seq)
            try:
                cdn = codon( m.group( 1 ), "anticodon" )
            except CodonError:
                # print "invalid codon", m.group(1)
                pass

        nam = unify.unify_name_trna( v )
        if nam != None:
            m = re.search( "\(([U%s]{3})\)" % Data.IUPACData.ambiguous_dna_letters, v )
            if m != None:
                try:
                    cdn = codon( m.group( 1 ), "anticodon" )
                except CodonError:
                    pass

        if cdn != None and nam == None:
            return cdn
        elif cdn != None and nam != None:
            aa = list( cdn.get_aa( self.transl_table ) )
            # print cdn, aa, nam
            if( len( aa ) == 1 and nam.startswith( aa[0] ) ):
                # print "ACDN MATCH"
                return cdn
        else:
            return None


    def _parse_codon_from_product( self, v ):
        m = re.search( "\(([U%s]{3})\)" % Data.IUPACData.ambiguous_dna_letters, v )
        if m == None:
            return None
        else:
#            print "->", m.group( 1 )
            return codon( m.group( 1 ), "codon" )


    def _parse_codon_recognized( self, v, strand ):
        """
        try to get a codon from value 
        return codon, anticodon pair
        """

        cdn = None
        nam = None

        v = v.upper()

        m = re.match( "^([U%s]{3})$" % Data.IUPACData.ambiguous_dna_letters, v )
        if m != None:
            try:
                cdn = codon( v, "codon" )
            except CodonError:
                # print "invalid codon", v
                pass

        m = re.match( "^CODONS? RECOGN[IZ]{2}ED[\s:]+([U%s]{3}$)" % Data.IUPACData.ambiguous_dna_letters, v )
        if m != None:
            # s =
            # print "CR %s" %(s)
            try:
                cdn = codon( m.group( 1 ), "codon" )
            except CodonError:
                # print "invalid codon", m.group(1)
                pass


        nam = unify.unify_name_trna( v )
        if nam != None:
            m = re.search( "\(([U%s]{3})\)" % Data.IUPACData.ambiguous_dna_letters, v )
            if m != None:
                try:
                    cdn = codon( m.group( 1 ), "codon" )
                except CodonError:
                    pass

        if cdn != None and nam == None:
            return cdn
        elif cdn != None and nam != None:
            aa = list( cdn.get_aa( self.transl_table ) )
            # print cdn, aa, nam
            if( len( aa ) == 1 and nam.startswith( aa[0] ) ):
                # print "CDN MATCH"
                return cdn
        else:
            return None

    def _parse_circular( self, rt ):
        """
        parse circularity from residuetype string
        \param rt residuetype string
        """

        if rt.endswith( "circular" ):
            self.circular = True
        else:
            self.circular = False
        return

    def _parse_complete( self, description ):
        if description.find( "complete" ) != -1:
            self.complete = True

    def _parse_names( self, annotations ):
        """
        parse the name, common name, and completeness from the definition 
        organism and source lines
        """

#        gb 'organism': 'Daphnia pulex'
#        embl 'organism': 'Astropecten polyacanthus (seastar)'
#        gb: 'source': 'mitochondrion Daphnia pulex (water flea)'
#        embl:no source

        # take organism as name
        try:
            self.name = annotations["organism"]
        except:
            raise Exception( "NoName", str( annotations ) )

        # try to get common name from source

        n = self.name.replace( "(", "\(" ).replace( ")", "\)" )

        if "source" in annotations:
            m = re.match( 'mitochondrion %s(?P<commonname> \(.*\)){0,1}$' % n, annotations["source"] )

            if m != None:
                if m.group( 'commonname' ) != None:
                    self.commonname = m.group( 'commonname' )[2:-1]
                else:
                    self.commonname = ""
            else:
                logging.warning( "%s malformed source %s %s" % ( self.accession, annotations["source"], n ) )
#                raise Exception( "Malformed", "source", annotations["source"], n )

#        for i in ['source', 'organism']:
#            try:
#                a = annotations[i]
#            except:
#                continue
#
#            m = re.match( '(mitochondrion ){0,1}(?P<name>.*)(?P<commonname> \([^(]*\)){0,1}$', a )
#            if m == None:
#                raise Exception( "Malformed", i, annotations[i] )
#
#            if self.name == "" or self.name == m.group( 'name' ):
#                self.name = m.group( 'name' )
#            else:
#                raise Exception( "Name mismatch in source/organism", self.name, m.group( 'name' ) )
#
#            if m.group( 'commonname' ) != None:
#                cn = m.group( 'commonname' )[2:-1]
#                if self.commonname == "" or self.commonname == cn:
#                    self.commonname = cn
#                else:
#                    logging.info( "CommonName mismatch in source/organism %s %s" % ( self.commonname, cn ) )


    def _parse_feature_codon( self, f, strand ):
        """
        try to parse the anticodon from a feature
        /anticodon=/codon_recognized
        """

        if f.type != "gene" and f.type != "tRNA":
            return None

#        print f
#        print f.qualifiers
        codons = []
        for q in f.qualifiers:
            if q in ["product", "gene"]:
                for x in f.qualifiers[q]:
                    codons.append( self._parse_codon_from_product( x ) )
            if q == "anticodon":
                for x in f.qualifiers[q]:
                    c = self._parse_anticodon( x, strand )
                    codons.append( c )
            elif q == "codon_recognized":
                for x in f.qualifiers[q]:
                    c = self._parse_codon_recognized( x, strand )
                    codons.append( c )
            elif q in ["note" , "gene", "product"]:
                for x in f.qualifiers[q]:
                    c = self._parse_anticodon( x, strand )
                    codons.append( c )
                    c = self._parse_codon_recognized( x, strand )
                    codons.append( c )

        return [ x for x in codons if x != None ]

        # print clean
        # t = [ Seq.translate( c, table = self.transl_table ) for c in codons ]


        # if len(s) != 1:
        #   if len(s) > 1:
        #        print "anticodon ???"
        #        print f
        #        print s
        #        print "================"
        #    return None
        # else:
        #    return list(s)[0]

        # todo return
        # todo codon, anticodon identities

#    def _parse_feature_location( self, location ):
#        """
#        (simple) parse a location string and return strand, start, and end
#
#        @param[in] location the genbank location string
#        @return triple (start, stop, strand):
#            strand = -1 iff location string starts with complement
#            start & stop = smallest and largest number found in the location
#        """
#
#        return

    def _parse_feature_locations( self, feature ):
        """
        parse location(s) from subfeatures 
        @return list of locations, i.e. list of triples (start, stop, strand)
        """

#        print feature, dir( feature )
        loc = []
        if len( feature.sub_features ) > 0:
            for f in feature.sub_features:
                loc += self._parse_feature_locations( f )
        else:
            # print feature
#            print "no subfeatures"
#            print "strand ", feature.strand
            if feature.strand == None or feature.strand >= 0:
                strand = 1
            else:
                strand = -1

            loc.append( ( feature.location.start.position, feature.location.end.position - 1, strand ) )


        return loc

    def _parse_feature_name( self, f, strand ):
        """
        try to determine the name of a feature
        for trna, rrna, and genes try to guess the name from the gene or product qualifier

        in order to get the origins additionally: 
        for rep_origin, D-loop, misc_feature try to guess the name from standard_name, note, direction"

        if there are several different guesses -> return None
        otherwise assign OH/OL to an origin feature
        and try to get the number of Leu/Ser tRNAs
        
        @param[in] f the feature
        @param[in] strand the strand of the feature
        @return the name of None (if could not be determined)
        """

        s = set()
        for q in f.qualifiers:
            if q in ["gene", "product"]:
                if f.type in ["tRNA", "gene"]:
                    for x in f.qualifiers[q]:
                        s.add( unify.unify_name_trna( x ) )
                if f.type in ["rRNA", "gene"]:
                    for x in f.qualifiers[q]:
                        s.add( unify.unify_name_rrna( x ) )
                if f.type in ["gene", "CDS"]:
                    for x in f.qualifiers[q]:
#                        print "%s?%s\n" % ( x, unify.unify_name_protein( x ) )
                        s.add( unify.unify_name_protein( x ) )
            elif q in ["standard_name", "note", "direction"]:
                if f.type in ["rep_origin", "D-loop", "misc_feature"]:
                    for x in f.qualifiers[q]:
#                        print "XXX", x, unify.unify_name_origin( x, strand )
                        s.add( unify.unify_name_origin( x, strand ) )

        s.discard( None )
        s = list( s )

#        for q in f.qualifiers:
#            k = q.key.strip( "\t /=" )
#            v = q.value.strip( "\" " )
# #            print k, v
#            if k in ["gene", "product"]:
#                print v,
#            if k in ["standard_name", "note", "direction"]:
#                if f.key in ["rep_origin", "D-loop", "misc_feature"]:
#                    print v,
#        print ""

        # if we have L and L1 or L2 remove L
        if "trnL" in s and ( ( "trnL1" in s ) or ( "trnL2" in s ) ):
            s.remove( "trnL" )
        # if we have S and S1 or S2 remove S
        if "trnS" in s and ( ( "trnS1" in s ) or ( "trnS2" in s ) ):
            s.remove( "trnS" )

        # check if there is exactly one element in s
        # 0 .. could not determine the name
        #      this is ok for origins because they often do not have a name
        #      and are only identified by its type
        # > 1 .. could not determine a unique name
        if len( s ) == 0:
#             if f.type in ["rep_origin", "D-loop"]:
#                 if strand == 1:
#                     return "OH"
#                 else:
#                     return "OL"
#             else:
            return None

        elif len( s ) > 1:
            # if "tRNA" in [f.key]+[ unify.feature_type(x) for x in s ]:
            # print f
            # print s
            # print "================"
            return None

        name = s[0]
        if name in ["trnL", "trnS"]:
            s = set()
            codons = self._parse_feature_codon( f, strand )
            for c in codons:
                if name == "trnL" and c == L1:
                    s.add( "trnL1" )
                elif name == "trnL" and c == L2:
                    s.add( "trnL2" )
                elif name == "trnS" and c == S1:
                    s.add( "trnS1" )
                elif name == "trnS" and c == S2:
                    s.add( "trnS2" )
            if len( s ) == 1:
                return list( s )[0]
            else:
                return name
            #    print name
                # print f
                # print "===================="
            # else:

        else:
            return name



        # now we have a uniq name
        # name = s[0]
        # tpe = unify.feature_type(name)
        # if tpe == "tRNA":
        #
        #    for c in codons:
        #        if c != None:
        #            s += c.get_aa(self.transl_table)

            # rint self.accession
            # rint f
            # f len(set(s)) != 1:
            #   print "FAIL ", s
            # lse:
            #   print "OKAY ", s
            # rint "=========================="
            # print s
                # clean.append( str(c) )
        # return aa


        # if f.key != tpe and ( f.key != "gene" or (tpe != "rRNA" and tpe != "tRNA") ) and ( f.key != "CDS" or tpe != "gene" ) :
        #    print "%s!=%s %s"%(f.key, tpe, name)

    def _parse_source( self, feature ):
        """
        parse entries from the source feature
        currently this is the taxid
        @param[in] feature the source feature
        @return nothing
        """

#        print feature, dir( feature )
#        print "key", feature.key
#        print "location", feature.location
        try:
            dbxref = feature.qualifiers['db_xref'][0]
        except:
            dbxref = ""

        if dbxref.startswith( "taxon:" ):
            self.taxid = int( dbxref[6:] )

        if self.taxid == None:
            sys.stderr.write( "warning: %s could not determine taxid\n" % self.accession )

    def _parse_translation( self, feature ):
        """
        if the given feature has a translation entry get it
        @param[in] feature a feature
        @return the translation of the feature, or None if it has none
        """

        try:
            return sequence( feature.qualifiers['translation'][0], IUPAC.extended_protein, False )
        except:
            return None


    def _parse_transl_table( self, features ):
        """
        get the translation table which is stored in the CDS features
        ensure that the codon table is unique for the species
        """

        s = set()
        for f in features:
            if "transl_table" in f.qualifiers:
                s.update( set( f.qualifiers["transl_table"] ) )

        if len( s ) != 1:
            if len( s ) == 0:
                logging.warning( "warning (%s) no translation table found" % self.accession )
            else:
                logging.warning( "warning (%s) more than one translation table found (%s)" % ( self.accession, str( s ) ) )
            self.transl_table = 1
        else:
            self.transl_table = int( list( s )[0] )

        if not self.transl_table in Data.CodonTable.unambiguous_dna_by_id:
            logging.warning( "warning (%s) has unknown translation table %d" % ( self.accession, self.transl_table ) )
            self.transl_table = 1


