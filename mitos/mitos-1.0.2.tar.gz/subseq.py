#!/usr/bin/venv python

'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).

Get subsequences of a sequence given in a fasta or genebank file
@todo: add possibility to get a subsequence from a species in the database 
'''


# from optparse import OptionParser, OptionGroup

from os.path import exists, splitext
import re
from string import split
from sys import stdout, stderr, exit

from mitos.gb import gbfromfile, feature
from mitos.sequence import sequences_fromfile, sequence_info_fromfile
from mitos.bedfile import bedfromfile

features = []
defaultfmt = "> %%a,%%strand,%%start-%%stop,%%name\n%%s"
usage = """
Get a subsequence or subsequences from a genome in a fasta or genbank file"""

try:
    import argparse
    parser = argparse.ArgumentParser( description = usage )

    group = parser.add_argument_group( "fasta/gb Input Options" )
    group.add_argument( "-f", "--infile", action = "append", metavar = "FILE", help = "input FILE (fas,gb,embl,bed)" )
    group.add_argument( "-l", "--linear", action = "store_false", dest = "circular", default = True, help = "treat sequence as linear" )

    group = parser.add_argument_group( "Output Options" )
    group.add_argument( "-o", "--outfile", action = "store", metavar = "FILE", help = "write subsequences to FILE (default: stdout)" )
    group.add_argument( "-m", dest = "format", action = "store", metavar = "FORMAT", \
                      default = defaultfmt.replace( "%%", "%" ), help = "output format: %%name=feature name, %%type=feature type, %%start=feature start, %%stop=feature end, %%strand=feature strand, %%s=sequence, %%a=accession, %%n=name (default: '" + defaultfmt + "'" )


    group = parser.add_argument_group( title = "Explicit position specification",
                                       description = "Specify subsequences for cutting directly. Each position must be given as a triple start, stop, strand. Start and stop are integers, the strand must be 1/-1. To specify more then one position there are two possibilities: 1) -p can be used more than once, 2) just give more positions, e.h. start1,end1,strand1,start2,end2,strand2,... . Note: instead of specifying the position a file may be given that contains the positions (newlines are OK)." )
    group.add_argument( "-p", "--position", action = "append", metavar = "POS", help = "get subsequence specified by POS or in file POS" )

    group = parser.add_argument_group( title = "position specification from genbank features",
                    description = "select a subset of the features in the genbank file for cutting. (type can be tRNA, rRNA, and gene) Note: -y,-Y,-n,-N can be specified more than once, combinations are possible." )
    group.add_argument( "-y", "--atype", action = "append", metavar = "TYPE", help = "get all features of type TYPE" )
    group.add_argument( "-Y", "--ftype", action = "append", metavar = "TYPE", help = "get all features except features of type TYPE" )
    group.add_argument( "-n", "--aname", action = "append", metavar = "NAME", help = "get all features with name NAME" )
    group.add_argument( "-N", "--fname", action = "append", metavar = "NAME", help = "get all features except features with name NAME" )

    args = parser.parse_args()
except ImportError:
    import optparse
    parser = optparse.OptionParser( usage = usage )

    group = optparse.OptionGroup( parser, "fasta/gb Input Options",
                    ""
                    "" )
    group.add_option( "-f", "--infile", action = "append", type = "string", metavar = "FILE", help = "input FILE" )
    group.add_option( "-l", "--linear", action = "store_false", dest = "circular", default = True, help = "treat sequence as linear" )
    parser.add_option_group( group )

    group = optparse.OptionGroup( parser, "Output Options",
                    ""
                    "" )
    group.add_option( "-o", "--outfile", action = "store", type = "string", metavar = "FILE", help = "write subsequences to FILE (default: stdout)" )
    group.add_option( "-m", dest = "format", action = "store", type = "string", metavar = "FORMAT", \
                      default = defaultfmt, help = "output format: %name=feature name, %type=feature type, %start=feature start, %stop=feature end, %strand=feature strand, %s=sequence, %a=accession, %n=name (default: '" + defaultfmt + "')" )

    parser.add_option_group( group )

    group = optparse.OptionGroup( parser, "Explicit position specification",
                    "Specify subsequences for cutting directly. Each position must be given as a triple start, stop, strand. "
                    "Start and stop are integers, the strand must be 1/-1. "
                    "To specify more then one position there are two possibilities: 1) -p can be used more than once, 2) just give more positions, e.h. start1,end1,strand1,start2,end2,strand2,... . "
                    "Note: instead of specifying the position a file may be given that contains the positions (newlines are OK)." )
    group.add_option( "-p", "--position", action = "append", type = "string", metavar = "POS", help = "get subsequence specified by POS or in file POS" )
    parser.add_option_group( group )

    group = optparse.OptionGroup( parser, "position specification from genbank features",
                    "select a subset of the features in the genbank file for cutting. "
                    "(type can be tRNA, rRNA, and gene) "
                    "Note: -y,-Y,-n,-N can be specified more than once, combinations are possible." )
    group.add_option( "-y", "--atype", action = "append", type = "string", metavar = "TYPE", help = "get all features of type TYPE" )
    group.add_option( "-Y", "--ftype", action = "append", type = "string", metavar = "TYPE", help = "get all features except features of type TYPE" )

    group.add_option( "-n", "--aname", action = "append", type = "string", metavar = "NAME", help = "get all features with name NAME" )
    group.add_option( "-N", "--fname", action = "append", type = "string", metavar = "NAME", help = "get all features except features with name NAME" )
    parser.add_option_group( group )

    args = parser.parse_args()[0]

if args.infile == None:
    stderr.write( "Error: no input given\n" )
    exit()

for infile in args.infile:

    if( not exists( infile ) ):
        stderr.write( "Error: no such file or directory %s\n" % ( infile ) )
        exit()

    root, ext = splitext( infile )
    if ext == ".fas" or ext == ".fa":
    #        sequence = sequences_fromfile( options.infile, options.circular )
        seq = sequence_info_fromfile( infile, circular = args.circular )
        if len( seq ) == 0:
            stderr.write( "Error: no sequence found in %s\n" % ( infile ) )
            exit()
        if len( seq ) > 1:
            stderr.write( "Error: more than one sequence found in %s -> taking the first\n" % ( infile ) )
        sequence = seq[0]['sequence']
        name = seq[0]['name']
        accession = seq[0]['name']
    elif ext == ".gb" or  ext == ".embl":
        gb = gbfromfile( infile )
        accession = gb.accession
        name = gb.name
        sequence = gb.sequence
    elif ext == ".bed":
        gb = bedfromfile( infile )
        accession = gb.accession
        name = gb.name
    else:
        stderr.write( "Error: invalid file type\n" )
        exit()

# outfile given ?
if args.outfile == None:
    ohandle = stdout
else:
    ohandle = open( args.outfile, "w" )

# if nothing is specified return complete sequence
if args.position == None and args.aname == None and args.fname == None and args.atype == None and args.ftype == None:
    features.append( feature( "", "", 0, len( sequence ), 1, "" ) )

if args.position == None:
    args.position = []

for p in args.position:
    if exists( p ):
        pfile = open( p, 'r' )
        posstr = ",".join( [ x.strip() for x in pfile.readlines() ] )
        pfile.close()
    else:
        posstr = p

    poslist = re.split( '[^-+\d]+', posstr )
    if len( poslist ) < 3:
        stderr.write( "Error: positions defined with(in) %s are < 3\n" % ( p ) )
        stderr.write( "   ->  skipping\n" )
        continue

    if poslist[-1] == '':
        poslist.pop()

    try:
        poslist = [ int( x ) for x in poslist ]
    except:
        stderr.write( "Error: positions defined with(in) %s are not all integers\n" % ( p ) )
        stderr.write( "   ->  skipping\n" )
        continue

    if len( poslist ) % 3 != 0:
        stderr.write( "Error: positions defined with(in) %s are not in triples\n" % ( p ) )
        stderr.write( "   ->  skipping\n" )
        continue

    for i in range( 0, len( poslist ), 3 ):
        poslist[i] -= 1
        poslist[i + 1] -= 1
        features.append( feature( "", "", poslist[i], poslist[i + 1], poslist[i + 2], "" ) )

if args.aname != None or args.fname != None or args.atype != None or args.ftype != None:
    features += gb.getfeatures( args.aname, args.fname, args.atype, args.ftype )

for f in features:
    #        print f
    out = args.format
    out = out.replace( "%name", f.outputname( anticodon = True ) )
    out = out.replace( "%type", f.type )
    out = out.replace( "%start", str( f.start ) )
    out = out.replace( "%stop", str( f.stop ) )
    out = out.replace( "%strand", str( f.strand ) )
    out = out.replace( "%a", accession )
    out = out.replace( "%n", name )
    out = out.replace( "%s", str( sequence.subseq( f.start, f.stop, f.strand ) ) )
    ohandle.write( "%s\n" % out )


ohandle.close()

