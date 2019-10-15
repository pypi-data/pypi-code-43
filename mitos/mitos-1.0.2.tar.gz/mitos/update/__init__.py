'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).
'''

from Bio import GenBank
import datetime
import glob
import logging
import os
from os.path import basename, exists, splitext
import re
from StringIO import StringIO
import sys
import time
import traceback

from .. import blast
from ..gb import gbfromfile
from .. import mitfi
from ..trna import arwenscan, trnascan

trnamap = {'ALA':'A', 'ARG':'R', 'ASN':'N', 'ASP':'D', 'CYS':'C', 'GLN':'Q', 'GLU':'E'\
           , 'GLY':'G', 'HIS':'H', 'ILE':'I', 'LEU':'L', 'LYS':'K', 'MET':'M', 'PHE':'F'\
           , 'PRO':'P', 'SER':'S', 'THR':'T', 'TRP':'W', 'TYR':'Y', 'VAL':'V'}


def prepareFiles( dir ):
    """
    - create sub directories 'featureNuc' and 'featureProt' (old data is 
      removed if existent)
    - for each genbank file in the given directory: 
      * write nucleotide sequences of the features annotated in the genbank 
        file to the corresponding file in 'featureNuc' 
      * write amino acid sequences of the features annotated in the genbank 
        file file to the corresponding file in 'featureProt' (take the given 
        amino acid sequence, NOT the translation of the annotated range) 
    - create BLAST data bases of all created fasta 
    @param dir the directory containing the genbank files and where the 
               fasta files and BLAST data bases should be written  
    """
    feature_nuc_path = dir + "/featureNuc/"
    feature_prot_path = dir + "/featureProt/"

    # create nuc and prot directories
    logging.debug( "create directories for nucleotide features (%s) and for protein features (%s)" % ( feature_nuc_path, feature_prot_path ) )
    if os.path.exists( feature_nuc_path ):
        logging.debug( "directory %s already exists - removing old files" % ( feature_nuc_path ) )
        os.system( "rm -f %s*" % ( feature_nuc_path ) )  # remove all outdated files in this directory
    else:
        os.system( "mkdir %s" % ( feature_nuc_path ) )  # creating directory

    if os.path.exists( feature_prot_path ):
        logging.debug( "directory %s already exists - removing old files" % ( feature_prot_path ) )
        os.system( "rm -f %s*" % ( feature_prot_path ) )  # remove all outdated files in this directory
    else:
        os.system( "mkdir %s" % ( feature_prot_path ) )  # creating directory
    logging.debug( "done" )

    i = 0
    length = len( glob.glob( '%s/*.gb' % ( dir ) ) )
    for fname in glob.glob( '%s/*.gb' % ( dir ) ):
        i += 1
        logging.debug( "%d/%d" % ( i, length ) )

        gbdata = gbfromfile( fname )

        # build fasta file for genbank file
        acc = gbdata.accession
        name = gbdata.name
#        sequence = str(gbdata.sequence)
#        output = ">%s %s\n%s" % ( acc, name, sequence )
#        out_file = "%s/%s.fas" % ( dir, acc )
#
#        try:
#            f = open( out_file, "w" )
#            f.write( output )
#            f.close()
#        except:
#            logging.warning( "error: could not write to file %s" % out_file )
#            sys.exit()

        # formatdb fastafile
#        os.system( "formatdb -i %s -o -p F" % ( out_file ) )

        # prepare featurefiles - all sequences for one gene gathered in one multifasta file
        features = gbdata.getfeatures()
        for feature in features:
            fname = feature.name
            fstart = feature.start
            fstop = feature.stop
            fstrand = feature.strand
            feature_nuc_file = feature_nuc_path + fname + ".fas"

            seq = gbdata.sequence.subseq( fstart, fstop, fstrand )
            output = ">%s:%d-%d %s\n%s\n" % ( acc, fstart, fstop, name, str( seq ) )

            fh = open( feature_nuc_file, "a" )
            fh.write( output )
            fh.close

            # prepare fastafiles with proteins
            if feature.translation != None:
                feature_prot_file = feature_prot_path + fname + ".fas"
                prot_output = ">%s:%d-%d %s\n%s\n" % ( acc, fstart, fstop, name, str( feature.translation ) )
                fh = open( feature_prot_file, "a" )
                fh.write( prot_output )
                fh.close


    # formatdb new created fastafiles

    # featureNuc
    os.system( "for i in %s*.fas; do formatdb -i $i -o -p F; done" % feature_nuc_path )
    logging.debug( "formatdb for feature nucs done" )

    # featureProt
    os.system( "for i in %s*.fas; do formatdb -i $i -o -p T; done" % feature_prot_path )
    logging.debug( "formatdb for feature prots done" )


def refseqsplit( fname, dname, prefix = None, atax = None, ftax = None, maxentries = False ):
    """
    split a given genbank file containing multiple genbank records into single files
    @param fname input multi genbank file
    @param dname directory for writing the output
    @param prefix only accession numbers with this prefix (e.g. NC) are allowed
          (default: None, i.e. allow all prefixes)  
    @param atax a list of taxonomic entities, only species belonging to one of 
           the taxonomix groups are accepted (default: None, i.e. allow everything) 
    @param ftax a list of taxonomic entities, reject species belonging to one of 
           the taxonomix groups (default: None, i.e. reject nothing)
    @param maxentries  maximum number of genbank files to write
    """
    n = 0
    N = 0

    try:
        fhandle = open( fname, 'r' )
    except:
        logging.error( "error: could not open %s for reading\n" % ( fname ) )
        sys.exit( 1 )

    cgb = ""
    # read line by line
    while 1:
        nxt = fhandle.readline()  # read a one-line string
        if not nxt:  # or an empty string at EOF
            break

        cgb += nxt
        if re.match( "^//$", nxt ) != None:
            gb_iterator = GenBank.Iterator( StringIO( cgb ), GenBank.FeatureParser() )

            try:
                cur_record = gb_iterator.next()
            except Exception, instance:
                logging.error( "parser error: %s" % cgb.split()[1] )

                stream = StringIO()
                exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
                traceback.print_exception( exceptionType, exceptionValue, exceptionTraceback, file = stream )
                logging.error( stream.getvalue() )
                stream.close()

                cgb = ""
                N += 1
                continue

# #            print cur_record
#            print "ann", cur_record.annotations
#            print "dbx", cur_record.dbxrefs
#            print "des", cur_record.description
# #            print "fea", cur_record.features
#            print "fmt", cur_record.format
#            print "id ", cur_record.id
#            print "lan", cur_record.letter_annotations
# #            print "low", cur_record.lower
# #            print "nam", cur_record.name
# #            print "rev", cur_record.reverse_complement
# #            print "seq", cur_record.seq
# #            print "upp", cur_record.upper
#            sys.exit()


            tax = cur_record.annotations['taxonomy']
#            print tax
#            print atax
#            if atax != None:
#                print filter( lambda x:x in tax, atax )
#            print ftax
#            if ftax != None:
#                print filter( lambda x:x in tax, ftax )

            skip = False
            if prefix != None and not cur_record.name.startswith( prefix ):
                logging.debug( "%s prefix skip" % cur_record.name )
                skip = True
            if atax != None and len( filter( lambda x:x in tax, atax ) ) == 0:
                logging.debug( "%s allowed tax skip (%s)" % ( cur_record.name, str( tax ) ) )
                skip = True
            if ftax != None and len( filter( lambda x:x in tax, ftax ) ) > 0:
                logging.debug( "%s forbidden tax skip (%s)" % ( cur_record.name, str( tax ) ) )
                skip = True

            if not skip:
                logging.debug( '%s writing entry' % cur_record.name )
                ofile = dname + "/" + cur_record.name + ".gb"
                try:
                    ohandle = open( ofile, "w" )
                except:
                    logging.error( "error: could not write to %s\n" % ofile )
                    sys.exit()

                ohandle.write( cgb )
                ohandle.close()
                n += 1


            cgb = ""
            N += 1
            # break
            if maxentries and maxentries <= n:
                logging.info( 'Max entries found' )
                break

    logging.info( "%d gb entries found %d written" % ( N, n ) )


def singleblastx( sequenzfile, code, outputdir, refdir ):
    """
    run blastall blastx 
    store results in OUTPUTDIR/blast/prot/(absname of sequenzfile)
    @param sequenzfile a (single) fasta sequenz file
    @param code genetic code 
    @param outputdir directory for writing the results
    @param[in] refseqver version of refseq to use
    @param[in] refdir directory containing reference data
    @return path where the result files can be found
    """

#    print "singleblastx", sequenzfile, code, outputdir
#    try:
    if 1:
        # file = open(sequenzfile,"r")
        # file.readlines()[1]
        # file.close()

        prot_path = "%s/refseq39/featureProt/" % ( refdir )
        prot_files = glob.glob( prot_path + "*.fas" )
        maxint = 2147483647  # realy big number to make sure blast reports all results

        acc = splitext( basename( sequenzfile ) )[0]

        # create directories
        if not os.path.exists( '%s/blast' % ( outputdir ) ):
            os.mkdir( '%s/blast' % ( outputdir ) )
        if not os.path.exists( '%s/blast/prot' % ( outputdir ) ):
            os.mkdir( '%s/blast/prot' % ( outputdir ) )

        # blasts
        for file in prot_files:
            # check if outfile already exists
            if os.path.exists( '%s/blast/prot/%s.%s.blast' % ( outputdir, acc, os.path.basename( file )[:-4] ) ):
                continue

            cmd = 'blastall -p blastx -Q %d -d %s -i %s -F "m S" -m 8 -f 12 -b %d -e 1e-1 -o %s/blast/prot/%s.%s.blast' % \
            ( code, file, sequenzfile, maxint / 2, outputdir, acc, os.path.basename( file )[:-4] )
            logging.debug( "blastx\n%s" % cmd )
            os.system( cmd )
#    except:
#        # TODO zumindest warnung ausgeben
#        pass

    return '%s/blast/prot/' % ( outputdir )

def singleblastn( sequenzfile, outputdir, refseqver, refdir ):
    """
    @param[in] refseqver version of refseq to use
    @param[in] refdir directory containing reference data
    """
    nuc_path = "%s/refseq/featureNuc/" % ( refdir )
    nuc_files = glob.glob( nuc_path + "*.fas" )
    maxint = 2147483647  # realy big number to make sure blast reports all results
    acc = sequenzfile.split( '/' )[-1][:-4]

    # Creat Dirs
    if not os.path.exists( '%s/blast' % ( outputdir ) ):
        os.mkdir( '%s/blast' % ( outputdir ) )
    if not os.path.exists( '%s/blast/nuc' % ( outputdir ) ):
        os.mkdir( '%s/blast/nuc' % ( outputdir ) )
#    if not os.path.exists( '%s/blast/nuc/%s' % ( outputdir, acc ) ):
#        os.mkdir( '%s/blast/nuc/%s' % ( outputdir, acc ) )

    # blast
    for file in nuc_files:
        if os.path.exists( "%s/blast/nuc/%s.%s.blast" % ( outputdir, acc , os.path.basename( file )[:-4] ) ):
            continue

        cmd = 'blastall -p blastn -i %s -d %s -m 8 -r 1 -q -1 -G 1 -E 2 -W 9 -F "m D" -o %s/blast/nuc/%s.%s.blast' % \
        ( sequenzfile, file, outputdir, acc , os.path.basename( file )[:-4] )
#        print cmd
        os.system( cmd )

def singletrnascan( sequenzfile, code, outdir ):
    # make trnascan folder
    if not os.path.exists( outdir + '/tRNAScan' ):
        os.mkdir( outdir + '/tRNAScan' )

    outfile = outdir + '/tRNAScan/' + os.path.basename( sequenzfile ) + '.ss'
    # Start scan
    try:
        gencode = trnascan.getGencodeFromTranl_tableNumber( str( code ) )
    except:
        logging.debug( "Could not determine genetic code for %s" % ( sequenzfile ) )
        gencode = None

    if gencode != None:
        trnascan.singletrnascan( sequenzfile, Q = True, O = True, b = True, X = 5, q = True, f = outfile, g = gencode )
    else:
        trnascan.singletrnascan( sequenzfile, Q = True, O = True, b = True, X = 5, q = True, f = outfile )

