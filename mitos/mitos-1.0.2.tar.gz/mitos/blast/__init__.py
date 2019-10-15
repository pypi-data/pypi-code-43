'''
@author: maze

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).
'''

from Bio.Data import CodonTable
import Bio.Blast.NCBIXML
import glob
import logging
from math import log10
import os
import sys

from .. import bedfile
from .. import codon
from ..feature import blasthit_feature, blast_feature, capcup, length
from ..gb import gbfromfile
from ..mito import types
from ..sequence import sequences_fromfile




class position_values():
    """
    data structure to store the values to be stored for a position. i.e.
    - its position (nucleotide position) 
    - height 
    - sum of evalues 
    - sum of bitscores 
    - query relative query position
    """
    def __init__( self, pos ):
        """
        initialise everything to 0 and the position to the given value
        @param pos: the position 
        """
        self._position = pos
        self._height = 0
        self._evalue = 0
        self._bitscore = 0
        self._query = 0

    def add( self, evalue, bitscore, relquery ):
        """
        add values of a given blast hit and increase height by one
        @param evalue: the evalue of the blast hit
        @param bitscore:  the evalue of the blast hit
        @param relquery: the relative query of the position in the blast hit
        """

        self._height += 1
        self._evalue += evalue
        self._bitscore += bitscore
        self._query += relquery

    def get_bitscore( self, avg ):
        """
        get the (average) bitscore
        @param avg: if true return avg, else return sum
        @return the desired value  
        """
        if avg:
            return float( self._bitscore ) / self._height
        else:
            return self._bitscore

    def get_height( self ):
        """
        get the height
        @return the desired value  
        """
        return self._height

    def get_evalue( self, avg ):
        """
        get the (average) evalue
        @param avg: if true return avg, else return sum
        @return the desired value  
        """
        if avg:
            return self._evalue / self._height
        else:
            return self._evalue

    def get_position( self ):
        """
        just get the position
        @return: the position 
        """
        return self._position

    def get_query( self ):
        """
        get the average relative query position
        @return the desired value  
        """

        return self._query


    def get_score( self, sel, avg ):
        """
        get one of the three values
        @param sel: selector 'e': get evalue, 'b': get bitscore, 'h': get height
        @param avg: get the average value (useless for height)  
        """
        if sel == 'e':
            return self.get_evalue( avg )
        elif sel == 'b':
            return self.get_bitscore( avg )
        elif sel == 'h':
            return self.get_height()
        else:
            raise Exception( "unknown selector" + repr( sel ) )

    def finalize( self ):
        """
        finalize the position, i.e. avarage the query
        """
        self._query /= float( self._height )


def _apply_cutoff( idx, values, scoresel, pavg, cutoff, percent ):
    """
    apply cutoff in order to make the hills steep. 
    remove positions with less than (maxhits in the reading frame)*cutoff
    from the index and invalidate the corresponding entries in the   
    three arrays (not deleted there because the mapping would become invalid)
    currently the cutoff is computed relative to the maximum number of hits in the rf
    
    TODO(later) do this per 'hit-component' otherwise pseudo genes with to few hits 
    are removed
    
    @param idx an mapping from positions in the genome to an index for one of the genes
    @param values list of values per position (access via idx)
    @param scoresel what should be the basis of the score at a position. 'e':evalue, 
           'b':bitscore, 'h':height
    @param pavg score at a position is the average if true, othewise the sum
    @param cutoff cutoff cutoff value  
    @param percent determine cutoff and if relative
    
    @return Nothing, idx and values is modiified 
    """
    for rf in idx.keys():
        mx = 0
        for i in idx[rf].keys():
            mx = max( mx, values[idx[rf][i]].get_score( scoresel, pavg ) )
        endcut = mx * cutoff

#            print name, rf, mx,

        for i in idx[rf].keys():
            p = idx[rf][i]
#                print p, posgenes[p]
            if ( percent and values[p].get_score( scoresel, pavg ) < endcut ) or \
                ( not percent and values[p].get_score( scoresel, pavg ) < cutoff ):
                values[p] = None
                del idx[rf][i]

        if len( idx[rf] ) == 0:
            del idx[rf]


def blastx( filepath, cutoff = 0, minevalue = 0, acc = None, code = None, \
            fastafile = None, sqn = None, circular = True, plot = False, \
            scoresel = 'e', pavg = False, havg = False, \
            prntih = False, maxovl = 0.2, clipfac = 10, fragovl = 0.2, \
            fragfac = 10.0, ststrange = 6, cr = False ):

    """
    TODO description
    
    @param filepath path containing the blast results 
        (prot/gen_name.blast and nuc/gen_name.blast files)

    @param cutoff cutoff value 2 possibilities 
        - a number > 0: then the cutoff specifies the (absolute) number of hits
          necessary to accept
        - a string "%xxx" where xxx is a percentage [0:100]: per reading frame 
          only hits with more BLAST hits than the maximum * xxx 
    @param minevalue
    @param acc accession/name of species (only used for determining plot path)
    @param code
    @param fastafile a the name of the file where the sequence can be found 
           that generated the BLAST results
    @param sqn accession of the species if known, blast hits with equal query 
           name (i.e. self hit) will be discarded;
        None: nothing is discarded
    @param circular assume that the sequence in fasta file is circular (True)
           or not (False)  
    @param plot 
    @param scoresel: what should be the basis of the score at a position. 
           'e':evalue, 'b':bitscore, 'h':height
    @param pavg: score at a position is the average if true, othewise the sum
    @param havg: score of an initial hit is the average score of the position's
           scores if true, else: sum
    @param prntih: print the names of the initial hits and their score and 
           return afterwards
    @param maxovl maximum overlap between initial predictions;
    @param clipfac of overlapping prediction of the same name differ by less 
           than factor X than clipping is started 
    @param fragovl max fraction allowed that two hits overlap to be counted as 
           fragments
    @param fragfac max factor by which fragments may differ in their score
    @param ststrange # aa that should be searched up/downstream for a more precise
           start or stop position
    @param cr predict control region based on blastn
    @return 
    """

#    print cutoff, minevalue, maxovl, clipfac, fragovl, fragfac, ststrange

#    print filepath, cutoff, minevalue, acc, code, fastafile, sqn, circular, plot, debug, scoresel, pavg, havg, prntih

    # TODO remove acc (only used for determining the plot path -> store plots in blast dir? )
    if acc == None:
        acc = fastafile.split( "/" )[-1]

    # determine cutoff and if relative
    percent = False
    try:
        if cutoff[0] == "%":
            percent = True
            cutoff = float( cutoff[1:] ) / 100
        else:
            cutoff = int( cutoff )
    except:
        # if not percent the cutoff is an int, thus cutoff[0] will raise an exception
        cutoff = int( cutoff )

    # if the code is given the algorithm searches for nearby start and stop codons
    # thus, the sequence has to be read in this case
    if code != None:
        # TODO circular should not be True default
        sequenz = sequences_fromfile( fastafile, circular = circular )[0]

    # an mapping from positions in the genome to an index in the following
    # arrays. seperately for each gene and reading frame. idx[name][rf][i]
    # gives the position in the arrays for position i for hits of gene with
    # name in the specified reading frame
    idx = dict()

#    posgenes = []   # number of blast hits per position
#    query = []      # avg. query position that matched here
#    value = []      # avg. evalue

    # list of values per position (access via idx), i.e. height, evalue, bitscore
    values = []
    predictions = dict()

    # list of the blast table files
    protfiles = glob.glob( "%s/prot/*.blast" % filepath )
    # iterate ove all blast tables
    for file in protfiles:
        # get name of gene (file name is xxx.GEN.blast)
        name = file.split( '.' )[-2]
        name = name.lower()

        # read blast output
        idx[name] = _blasthandle_table( file, minevalue, values, sqn, True )
#        idx[name] = blasthandle_xml( file, minevalue, posgenes, value, query, sqn )

        _apply_cutoff( idx[name], values, scoresel, pavg, cutoff, percent )

    if cr:
        # list of the blast table files
        nucfiles = glob.glob( "%s/nuc/*.blast" % filepath )
        # iterate ove all blast tables
        for file in nucfiles:
            # get name of gene (file name is xxx.GEN.blast)
            name = file.split( '.' )[-2]

            # read blast output
            idx[name] = _blasthandle_table( file, minevalue, values, sqn, False )
    #        idx[name] = blasthandle_xml( file, minevalue, posgenes, value, query, sqn )

            _apply_cutoff( idx[name], values, scoresel, pavg, cutoff, percent )

    # END OF ITERATION OVER ALL blast files

    # output for plot histograms
    if plot and ( not os.path.exists( "%s/blast.dat" % ( filepath ) ) ):
        file = open( "%s/blast.dat" % ( filepath ), "w" )
        for name in idx:

            tab = []

            for rf in idx[name]:
                for i in idx[name][rf].keys():
                    p = idx[name][rf][i]

                    tab.append( ( values[p].get_position(), \
                                 values[p].get_score( scoresel, pavg ), \
                                 values[p].get_query() ) )

            # sort by position (and reverse score)
            tab.sort( key = lambda a:( a[0], -a[1] ) )

            # remove entries at the same position with smaller score
            for i in reversed( xrange( 1, len( tab ) ) ):
                if( tab[i][0] == tab[i - 1][0] and tab[i][1] <= tab[i - 1][1] ):
                    del tab[i]

            if len( tab ) > 0:

                file.write( "%d %s %d %f %f\n" % ( tab[0][0] - 1, name, rf, 0, 0 ) )
                li = tab[0][0] - 1
                for i in xrange( len( tab ) ):
                    if li != tab[i][0] - 1:
                        file.write( "%d %s %d %f %f\n" % ( li + 1, name, rf, 0, 0 ) )
                        file.write( "%d %s %d %f %f\n" % ( tab[i][0] - 1, name, rf, 0, 0 ) )

                    file.write( "%d %s %d %f %f\n" % ( tab[i][0], name, rf, tab[i][1], tab[i][2] ) )
                    li = tab[i][0]

                file.write( "%d %s %d %f %f\n" % ( tab[-1][0] + 1, name, rf, 0, 0 ) )
            del tab

        file.close()
#               -param  muh.par
#                cmd = "gracebat -nxy %s/plot/%s/%d  -printfile %s/plot/%s_%d.ps -pexec \"g0.s2.y = g0.s2.y*10\"" % ( filepath, name, rf, filepath, name, rf )
#                os.system( cmd )

    featurelist = []
    hits = _create_initial_predictions( idx, values, scoresel, pavg, havg )

    logging.debug( "initial hits" )
    for h in hits:
        logging.debug( "%s" % str( h ) )
    logging.debug( "============" )

    if prntih:
        for h in hits:
            sys.stdout.write( "%s %f\n" % ( h.name, h.score ) )

    hits = _nonoverlapping_greedy( hits, idx, values, scoresel, pavg, havg, maxovl, clipfac )
#    hits = _nonoverlapping_greedy_sorted( hits, debug )

    # join hits that with query ranges that overlap by less than 20% (of the length of one of the query ranges)
    hits.sort( key = lambda x:[x.name, x.score], reverse = True )

    fragfaclb = 1.0 / float( fragfac )
    fragfacub = 1.0 * float( fragfac )

    for h in hits:
        logging.debug( "check %s" % str( h ) )

        if not h.name in predictions:
            predictions[h.name] = []


        # check for each of the already determined copies if the current prediction fits in
        newhit = True
        for j in range( len( predictions[h.name] ) ):

            logging.debug( "check against" )
            for x in predictions[h.name][j]:
                logging.debug( "\t %s" % str( x ) )
#                    print "\t", x
            # now check for each part of the current "copy" if the height
            # and query overlap is appropriate
            appropriate = True
            for k in range( len( predictions[h.name][j] ) ):
                # combine only if in the same league wrt. the height
                if not fragfaclb <= ( float( h.score ) / predictions[h.name][j][0].score ) <= fragfacub:
                    logging.debug( "! high enough %f" % ( ( float( h.score ) / predictions[h.name][j][0].score ) ) )
                    appropriate = False
                    break

                start = predictions[h.name][j][k].qstart
                stop = predictions[h.name][j][k].qstop
                cap, cup = capcup( h.qstart, h.qstop, start, stop, circular = False, size = 0 )
                logging.debug( "cap %d cup %d len %d %d" % ( cap, cup, length( h.start, h.stop, False, 0 ), length( start, stop, False, 0 ) ) )

                if cap / float( length( h.start, h.stop, False, 0 ) ) > fragovl or cap / float( length( start, stop, False, 0 ) ) > fragovl:
                    logging.debug( "too much overlap %f %f" % ( cap / float( length( h.start, h.stop, False, 0 ) ) , cap / float( length( start, stop, False, 0 ) ) ) )
                    appropriate = False
                    break

            # if the currently considered prediction fits in this copy
            # 1) append it, mark that it was inserted into an existing copy, and do not check other copies
            if appropriate:
                predictions[h.name][j].append( h )
                # sort by query position
                predictions[h.name][j].sort( key = lambda k: k.qstart )
                newhit = False
                break

        if newhit:
            logging.debug( "new hit" )
            predictions[h.name].append( [h] )

    if code != None:
        for name in predictions.keys():
            if name in ["OH", "OL"]:
                continue

            i = 0
            while i < len( predictions[name] ):
                while len( predictions[name][i] ) > 0:
                    if predictions[name][i][0].strand == 1:
                        predictions[name][i][0].start = findstart( int( predictions[name][i][0].start ), code, sequenz, predictions[name][i][0].strand, ststrange )
                    else:
                        predictions[name][i][0].stop = findstart( int( predictions[name][i][0].stop ), code, sequenz, predictions[name][i][0].strand, ststrange )

                    if predictions[name][i][0].stop < predictions[name][i][0].start:
                        logging.debug( "empty" )
                        del predictions[name][i][0]
                    else:
                        break

                    # 0 == -1
                    if len( predictions[name][i] ) <= 1:
                        continue

                    if predictions[name][i][-1].strand == 1:
                        predictions[name][i][-1].stop = findstop( int( predictions[name][i][-1].stop ), code, sequenz, predictions[name][i][-1].strand, ststrange )
                    else:
                        predictions[name][i][-1].start = findstop( int( predictions[name][i][-1].start ), code, sequenz, predictions[name][i][-1].strand, ststrange )

                    if predictions[name][i][-1].stop < predictions[name][i][-1].start:
                        logging.debug( "empty" )
                        del predictions[name][i][-1]
                    else:
                        break

                if len( predictions[name][i] ) == 0:
                    del predictions[name][i]
                else:
                    i += 1

            logging.debug( "=> %s" % ( str( predictions[name] ) ) )
            if len( predictions[name] ) == 0:
                del predictions[name]



    for name in predictions.keys():
        k = 0
        for hits in predictions[name]:
            for i in range( len( hits ) ):
                # TODO copy numbers should be sorted by the score
                if len( predictions[name] ) > 1:
                    hits[i].copy = k
                if len( hits ) > 1:
                    hits[i].part = i
                featurelist.append( hits[i] )

            if len( predictions[name] ) > 1:
                k += 1

    return featurelist

def blastn( filepath, cutoff = 0, minevalue = 0, acc = None ):
    if acc == None:
        acc = filepath.split( "/" )[-1]

    # Check if it is in %
    percent = False
    try:
        if cutoff[0] == "%":
            percent = True
            cutoff = float( cutoff[1:] ) / 100
    except:
        # if not percent the Cutoff ist a Int
        cutoff = int( cutoff )

    # list of the Posibel Gene
    posgenes = dict()
    strand = dict()
    # List of the Blasttable-Files
    protfiles = glob.glob( "%s/*.blast" % filepath )
    # Overall blast Tables
    for file in protfiles:
        try:
            # Get name of Gene
            name = file.split( '.' )[-2]
            # Read file
            blasthandle = open( file, 'r' )
            # Get Hits form the Table
            lines = blasthandle.readlines()
            # close File
            blasthandle.close()
            # Preper ReadingFreams
            posgenes[name] = {-1:dict(), 1:dict()}
            hits = {-1:0, 1:0}
            # For every Blast-Hit from the Gene
            for line in lines:
                # Splite the Table in the single Information
                cols = line.split()

                start = int( cols[6] )
                stop = int( cols[7] )
                # gettin evalue for the cut of evalue
                evalue = cols[10].split( "-" )[-1]
                if evalue == "0.0":
                    evalue = 100
                else:
                    evalue = float( evalue )

                # get strand
                if start < stop:
                    strand[name] = 1
                elif start > stop:
                    helpstart = start
                    start = stop
                    stop = helpstart
                    strand[name] = -1
                else:
                    logging.warning( "[Blast] error: start = stop" )
                    sys.exit()

                #####
                # check whether hit is identity, if so continue with next hit
                #####
                id = False

                if cols[0] == cols[1].split( ':' )[0]:  # identical accession number
                    id = True
                    if not cols[2] == "100.00":
                        idstart = int( cols[1].split( ':' )[1].split( '-' )[0] ) + 1
                        idstop = int( cols[1].split( ':' )[1].split( '-' )[1] )
                        if idstop < idstart:
                            helpstop = idstart
                            idstart = idstop
                            idstop = helpstop
                        x = y = 0
                        for i in range( idstart, idstop ):
                            y += 1
                            if i > start and i < stop:
                                x += 1  # count same positions
                        if float( x ) / y < 0.8:
                            id = False

                if not id and evalue >= minevalue:
                    # get reading frame
                    hits[strand[name]] += 1
                    # poscount[rf] = poscount[rf].union(set(range(start,stop)))
                    for i in range( start, stop ):
                        if not i in posgenes[name][strand[name]]:
                            posgenes[name][strand[name]][i] = 1
                        else:
                            posgenes[name][strand[name]][i] += 1

            # geting best rf
            strandmax = -1

            for strandx in hits:
                if hits[strandx] > hits[strandmax]:
                    strandmax = strandx
            strand[name] = strandmax
            posgenes[name] = posgenes[name][strandmax]

            todel = []
            # Cut the hits
            if percent:
                endcut = hits[strandmax] * cutoff
                for i in posgenes[name]:
                    if posgenes[name][i] < endcut:
                        todel.append( i )
            else:
                for i in posgenes[name]:
                    if posgenes[name][i] < cutoff:
                        todel.append( i )
            for i in todel:
                del posgenes[name][i]
            # geting list of the Hits
            posgenes[name] = [i for i in posgenes[name]]
            posgenes[name].sort()

        except:
            logging.warning( "blastfile error: could not open file %s\n" % file )

    featurelist = []
    # For every Gene
    for name in posgenes:
        if len( posgenes[name] ) > 0:
            hits = []
            start = posgenes[name][0]
            lasti = posgenes[name][0] - 1
            # get singele hits for one gene
            for i in posgenes[name]:
                if lasti != i - 1:
                    hits.append( [start, lasti] )
                    start = i
                lasti = i
            hits.append( [start, lasti] )

            for hit in hits:
                featurelist.append( feature( name, types[name], int( hit[0] ), int( hit[1] ), int( strand[name] ), "blastn" ) )

    return featurelist

def _clip_predictions( h1, h2, idx, values, scoresel, pavg, havg ):
    """
    function for clipping two overlapping predictions
    intended use: predictions with same name and reasonable height difference
    
    @param[in] h1 a prediction 
    @param[in] h2 another prediction
    @param[in] idx position index for the following three arrays id[rf][p] gives the array position for hit at p in rf 
    @param[in] posgenes the number of hits at a position
    @param[in] value    the average evalue at a position
    @param[in] query    the relative query position at a position
    @param scoresel: what should be the basis of the score at a position. 'e':evalue, 'b':bitscore, 'h':height
    @param pavg: score at a position is the average if true, othewise the sum
    @param havg: score of an initial hit is the average score of the position's scores if true, else: sum  
    @return if one hit is inlcuded in the other then then (None, hit2),  
        otherwise (hit1,hit2). Thus it has to be taken care that the prefered hit is hit1!
    """
    swap = False

    if h1.start <= h2.start <= h1.stop <= h2.stop:
        swap = False
        hit1, hit2 = h1, h2
    elif h2.start <= h1.start <= h2.stop <= h1.stop:
        swap = True
        hit1, hit2 = h2, h1
    else:
#        sys.stderr.write( "clip predictions: got strange predictions\n %s %s" % ( str( h1 ), str( h2 ) ) )
        return None, h2

#    print "clip", hit1, hit2

    rf1 = ( hit1.start % 3 + 1 ) * hit1.strand
    rf2 = ( hit2.start % 3 + 1 ) * hit2.strand
#    print rf1, rf2

    i = hit2.start
    while i <= hit1.stop:
        if values[ idx[rf2][i] ].get_score( 'e', True ) < values[ idx[rf1][i] ].get_score( 'e', True ):
            i += 3
        else:
            break

    j = hit1.stop
    while j >= hit2.start:
        if values[ idx[rf1][j] ].get_score( 'e', True ) < values[ idx[rf2][j] ].get_score( 'e', True ):
            j -= 3
        else:
            break

    hit2.start = i
    hit1.stop = j

#    print "cliped", hit1, hit2

    # recalculate the hits, i.e. get new position sets and re-initialize
    positions = []
    for i in range( hit1.start, hit1.stop + 1 ):
        positions.append( values[idx[rf1][i]] )
    if positions == []:
        hit1 = None
    else:
        hit1 = blast_feature( hit1.name, hit1.type, hit1.strand, positions, scoresel, havg, pavg )

    positions = []
    for i in range( hit2.start, hit2.stop + 1 ):
        positions.append( values[idx[rf2][i]] )
    if positions == []:
        hit2 = None
    else:
        hit2 = blast_feature( hit2.name, hit2.type, hit2.strand, positions, scoresel, havg, pavg )

    if hit1 == None:
        pass
    elif hit2 == None:
        hit1, hit2 = hit2, hit1
    elif hit1 == None and hit2 == None:
        logging.error( "clip predictions yielded 2 None features" )
        raise Exception( "clip predictions yielded 2 None features" )
    elif swap:
        hit1, hit2 = hit2, hit1

    return hit1, hit2

def _create_initial_predictions( idx, values, scoresel, pavg, havg ):
    """
    determine features, i.e. consecutive stretches of positions (in the  
    same reading frame) which have blast hits
    this is done separately per gene and reading frame
    for every hit the average (over the length of the feature) 
    evalue and height (number of hits) is computed  
    furthermore the average query start and stop position is stored.query,
    @param idx: ???
    @param scoresel: what should be the basis of the score at a position. 'e':evalue, 'b':bitscore, 'h':height
    @param pavg: score at a position is the average if true, othewise the sum
    @param havg: score of an initial hit is the average score of the position's scores if true, else: sum  

    @return: a list of (blast_)features
    """

    hits = []  # the list of features for each gene

    conspos = []  # a list of consecutive positions

    for name in idx:
        for rf in idx[name]:
            positionlist = sorted( idx[name][rf].keys() )

            if rf > 0:
                strand = 1
            else:
                strand = -1

            p = idx[name][rf][ positionlist[0] ]
            conspos.append( values[p] )
            lastpos = positionlist[0] - 1
#            nfeat = blast_feature( name, types[name], \
#                        positionlist[0], positionlist[0] - 1, \
#                        strand, "mitos", rf = rf,
#                        qstart = values[p].query, qstop = 0, score = 0 )

            for i in positionlist:
                # if disrupted:
                # - finish old feature
                # - start a new one

                p = idx[name][rf][i]

                if lastpos != i - 1:
#                    if nfeat.start != nfeat.stop:
# #                        nfeat.evalue /= ( nfeat.stop - nfeat.start )
# #                        nfeat.height /= float( nfeat.stop - nfeat.start )
#
#                        pstart = idx[name][rf][nfeat.start]
#                        pstop = idx[name][rf][nfeat.stop]
#                        nfeat.qstop = values[pstop].query
#                        if values[pstart].query > values[pstop].query:
#                            nfeat.qstart, nfeat.qstop = nfeat.qstop, nfeat.qstart
#                        hits.append( nfeat )
                    hits.append( blast_feature( name, types[name], strand, conspos, scoresel, havg, pavg, mito = 1 ) )
                    conspos = []

#                    nfeat = blast_feature( name, types[name], i, i, \
#                                strand, "mitos", rf = rf, evalue = 0,
#                                qstart = values[p].query, qstop = 0, height = 0 )

                # continue counting
                conspos.append( values[p] )
#                nfeat.bitscore += values[p].bitscore
#                nfeat.evalue += values[p].evalue
#                nfeat.height += values[p].height
                lastpos = i

            # finish last feature
            hits.append( blast_feature( name, types[name], strand, conspos, scoresel, havg, pavg ) )
            conspos = []
#                nfeat.evalue /= ( nfeat.length( False, 0 ) )
#                nfeat.height /= float( nfeat.length( False, 0 ) )
#                pstart = idx[name][rf][nfeat.start]
#                pstop = idx[name][rf][nfeat.stop]
#                nfeat.qstop = values[pstop].query
#                if values[pstart].query > values[pstop].query:
#                    nfeat.qstart, nfeat.qstop = nfeat.qstop, nfeat.qstart
#                hits.append( nfeat )
    return hits

def findstart( posi, code, sequence, strand, aarng ):
    """
    search a position in the close neighbourhood of posi
    that is a start position 

    @param posi current start position
    @param code genetic code id
    @param sequence sequence
    @param strand strand
    @param aarng how many aminoacids before and after a start should be searched  
    @return a better position or the original one
    """

    start, stop = codon.parsecodon( code )
#     print "find_start", posi, strand, start

    # search from the inside of the gene to the outside for a stop codon
    # if one is found then start the search for a start codon behind this
    # stop codon
    if strand == 1:
        frm = posi - aarng * 3
        rng = range( posi + aarng * 3, posi - aarng * 3 - 1, -3 )
    else:
        frm = posi + aarng * 3
        rng = range( posi - aarng * 3, posi + aarng * 3 + 1, 3 )

#     print "from", frm, "rng", rng

    for i in rng:
        if not sequence.circular and ( i <= 0 or i >= len( sequence ) ):
            continue

        if strand == 1:
            cdn = sequence.subseq( i, i + 2, strand )
        else:
            cdn = sequence.subseq( i - 2, i, strand )

        if str( cdn ) in stop:
            if strand == 1:
                frm = i + 3
            else:
                frm = i - 3
#             break

    if strand == 1:
        rng = range( frm, posi + aarng * 3 + 1, 3 )
    else:
        rng = range( frm, posi - aarng * 3 - 1, -3 )

    rng.sort( key = lambda x: ( abs( x - posi ) ) )

#     print "rng", rng

    for i in rng:
        if not sequence.circular and ( i <= 0 or i >= len( sequence ) ):
            continue
        if strand == 1:
            cdn = sequence.subseq( i, i + 2, strand )
        else:
            cdn = sequence.subseq( i - 2, i, strand )
#         print i, cdn
        if str( cdn ) in start:
            return i

    if strand == 1:
        return max( frm, posi )
    else:
        return min( frm, posi )

def findstop( posi, code, sequence, strand, aarng ):
    """
    search a position in the close neighbourhood of posi
    that is a stop position 

    @param posi current stop position
    @param code genetic code id
    @param sequence sequence
    @param strand strand
    @param aarng how many aminoacids before and after a start should be searched
    @return a better position or the original one
    """

#    print "find_stop", posi, strand
    start, stop = codon.parsecodon( code )

    if strand == 1:
        rng = range( posi - aarng * 3, posi + aarng * 3 + 1, 3 )
    else:
        rng = range( posi + aarng * 3, posi - aarng * 3 - 1, -3 )

#    print "rng", rng

    for i in rng:
        if not sequence.circular and ( i <= 0 or i >= len( sequence ) ):
            continue

        if strand == 1:
            cdn = sequence.subseq( i - 2, i, strand )
        else:
            cdn = sequence.subseq( i, i + 2, strand )

        if str( cdn ) in stop:
            return i

    return posi

def _blasthandle_table( blastfile, minevalue, values, sqn = None, prot = True ):
    """
    read a blast file
    
    for each position the following values are determined: 
    - the number of blast hist including the position
    - the average e-value of these blast hits and
    - the average relative query position of these hits 
    
    @param[in] blastfile a file name of a tabular blast output (-m 8) 
    @param[in] minevalue e-value threshold to be applied, i.e. smaller evalues 
        are discarded
    @param[out] posgenes number of hits for the position 
    @param[out] value average of the e-value for the position
    @param[out] query average of the relative query positions for the position
    @param[in] sqn a name of hits to be discarded (for discarding the self hit)
        None will discard nothing 
    @paramp[in] prot 
        true: the blast results are for proteins -> will be assigned to reading frames [-3,-2,-1,1,2,3]
        false: nucleotide matches -> reading frames 4, -4 depending on the strand

    @return a mapping from genomic positions to the index in posgenes, value, and query 
    i.e. idx[rf][i] gives the index for genomic position i in reading frame i   
    """

    blasthandle = open( blastfile, 'r' )

    idx = {  1:dict(), 2:dict(), 3:dict(), 4:dict(), \
           - 1:dict(), -2:dict(), -3:dict(), -4:dict()}

#    # counts (for the current gene) the number of blast hits per reading frame with large enough e-value
#    hits = {1:0, 2:0, 3:0, -1:0, -2:0, -3:0}
    # iterate through the blast file lines (blast hits) for the current gene
    for line in blasthandle:
        # split the line in the single informations
        cols = line.split()

        if sqn != None and sqn == cols[1].split( ":" )[0]:
            continue

        start = int( cols[-6] ) - 1
        stop = int( cols[-5] ) - 1
        querystart = ( int( cols[-4] ) - 1 ) * 3
        querystop = ( int( cols[-3] ) - 1 ) * 3

        # getting evalue for the cut of evalue
        if cols[-2] == "0.0":
            evalue = 100
        else:
            evalue = -1 * log10( float( cols[-2] ) )

        bitscore = float( cols[-1] )

        # get strand
        if start < stop:
            strand = 1
        elif start > stop:
            start, stop = stop, start
            strand = -1
        else:
            logging.warning( "[Blast] error: start = stop %s" % blastfile )
            sys.exit()

        if evalue >= minevalue:
            # get reading frame
            # increase number of hits for the reading frame, i.e. +- 1,2,3

            if prot:
                rf = ( strand ) * ( start % 3 + 1 )
            else:
                rf = 4 * strand

            # count for every position the query position
            # count positions
            for i in range( start, stop + 1 ):
                if not i in  idx[rf]:
                    idx[rf][i] = len( values )
                    values.append( position_values( i ) )

                p = idx[rf][i]

                if strand == 1:
                    relquery = i - start + querystart
                else:
                    relquery = querystop - ( i - start )

                values[p].add( evalue, bitscore, relquery )

    blasthandle.close()

    # compute average values of query positions and e-values
    # and delete empty reading frames
    for rf in idx.keys():
        for p in idx[rf].values():
#            if posgenes[p] == None:
#                continue
            values[p].finalize()
        if len( idx[rf] ) == 0 :
            del idx[rf]

    return idx

def blasthandle_xml( blastfile, minevalue, posgenes, value, query, sqn = None ):

    blasthandle = open( blastfile, 'r' )

    idx = {1:dict(), 2:dict(), 3:dict(), -1:dict(), -2:dict(), -3:dict()}

    # counts (for the current gene) the number of blast hits per reading frame with large enough e-value
#    hits = {1:0, 2:0, 3:0, -1:0, -2:0, -3:0}

    handle = Bio.Blast.NCBIXML.parse( blasthandle )
    for file in handle:
        for alignmen in file.alignments:
#            print sqn, alignmen.accession
#            print dir( alignmen )
            if sqn != None and sqn == alignmen.accession.split( ":" )[0]:
#                print "discard", alignmen
                continue

            for hsp in alignmen.hsps:

                start = int( hsp.query_start ) - 1
                stop = int( hsp.query_end ) - 1
                querystart = ( int( hsp.sbjct_start ) - 1 ) * 3
                querystop = ( int( hsp.sbjct_end ) - 1 ) * 3

                if 0 == hsp.expect:
                    evalue = 100
                else:
                    evalue = -1 * log10( hsp.expect )
                rf = hsp.frame[0]

                if rf < 0:
                    strand = -1
                else:
                    strand = 1

                if evalue >= minevalue:
#                    hits[rf] += 1
                    for i in range( start, stop + 1 ):
                        if not i in  idx[rf]:
                            idx[rf][i] = len( posgenes )
                            posgenes.append( 0 )
                            value.append( 0 )
                            query.append( 0 )

                        p = idx[rf][i]
                        posgenes[p] += 1
                        value[p] += evalue
                        if strand == 1:
                            query[p] += i - start + querystart
                        else:
                            query[p] += querystop - ( i - start )
    blasthandle.close()

    # compute average values of query positions and e-values
    for rf in idx.keys():
        for p in idx[rf].values():
            if posgenes[p] == None:
                continue
            query[p] /= float( posgenes[p] )
            value[p] /= float( posgenes[p] )

    return idx

def _nonoverlapping_greedy( hits, idx, values, scoresel, pavg, havg, maxovl, clipfac ):
    """
    greedy determination of a non-overlapping subset of the given hits
    @param[in] hits
    @param scoresel: what should be the basis of the score at a position. 'e':evalue, 'b':bitscore, 'h':height
    @param pavg: score at a position is the average if true, othewise the sum
    @param havg: score of an initial hit is the average score of the position's scores if true, else: sum  
    @param maxovl: maximum overlap between predictions
    @param clipfac 
    @return the subset
    """

#    pergen
#    hitspg = {}
#    for i in range( len( hits ) ):
#        try:
#            hitspg[ hits[i].name ].append( hits[i] )
#        except KeyError:
#            hitspg[ hits[i].name ] = [ hits[i] ]
#    hits = []
#    for name in hitspg.keys():
#        hitspg[ name ].sort( key = lambda x: ( x.score, x.stop - x.start ) )
#
#    while True:
#        curbest = []
#        for name in hitspg.keys():
#            if len( hitspg[name] ) > 0:
#                curbest.append( hitspg[ name ][-1] )
#                del hitspg[ name ][-1]
#            else:
#                del hitspg[ name ]
#        if len( curbest ) == 0:
#            break
#        else:
#            curbest.sort( key = lambda x: ( x.score, x.stop - x.start ), reverse = True )
#
#        hits += curbest
    cliplb = 1.0 / float( clipfac )
    clipub = 1.0 * float( clipfac )

    # determine (greedily) a set of non overlapping predictions
    hits.sort( key = lambda x: ( x.score, x.stop - x.start ), reverse = True )
    i = 0
    while i < len( hits ):
        j = 0
        while j < i:
            # compute length of intersection and determine if this makes
            # more than 20% of one of the hits
            cap, cup = hits[i].capcup( hits[j], circular = False, size = 0 )
            if cap / float( hits[i].length( False, 0 ) ) > maxovl or cap / float( hits[j].length( False, 0 ) ) > maxovl:
#                print "cap", cap, "cup", cup, "len(i)", float( hits[i].length( False, 0 ) ), "len(k)", float( hits[j].length( False, 0 ) )
#                print cap / float( hits[i].length( False, 0 ) ), cap / float( hits[j].length( False, 0 ) )
                break
            j += 1

        # overlap was detected
        # - if it is the same gene and the heights of the initial predictions
        #   are appropriately similar then the predictions are adapted accordingly
        # - otherwise the new hit (the smaller hit is deleted)
        if j < i:
            if hits[i].name == hits[j].name and \
                cliplb <= ( hits[i].score / hits[j].score ) <= clipub:

                logging.debug( "clip overlapping %s %s" % ( str( hits[i] ), str( hits[j] ) ) )
                hits[i], hits[j] = _clip_predictions( hits[i], hits[j], \
                                    idx[hits[i].name], values, scoresel, pavg, havg )
                logging.debug( "                 |%s|%s|" % ( str( hits[i] ), str( hits[j] ) ) )

                if hits[i] == None:
                    del hits[i]
                else:
                    i = i + 1
            else:
                logging.debug( "delete %s\tbecause %s" % ( str( hits[i] ), str( hits[j] ) ) )
                del hits[i]
        else:
            i = i + 1

    return hits

def _nonoverlapping_greedy_sorted( hits, maxovl ):
    """
    old version of greedy determination of non overlapping initial prediction
    subset (here the hits are traversed sorted by starting position and 
    only neigbouring pairs are checked, this is faster returns worse results 
    as conflict occur more easily)
    @param hits: a list of initial predictions
    @param maxovl: maximum overlap between predictions
    @return: a non-overlapping subset of hits 
    """

    # remove hits that overlap by more than 20% (of the length of one of the features)
    hits.sort( key = lambda x: x.start )
    i = 0
    while i < len( hits ):
        k = i + 1

        while k < len( hits ):
            # simpe check if i-1 and i can overlap
            if hits[i].stop < hits[k].start:
                break


            # compute length of intersection and determine if this makesstr
            # more than 20% of one of the hits
            cap, cup = hits[i].capcup( hits[k], circular = False, size = 0 )
            if cap / float( hits[i].length( False, 0 ) ) > maxovl or cap / float( hits[k].length( False, 0 ) ) > maxovl:
#                print "cap", cap, "cup", cup, "len(i)", float( hits[i].length( False, 0 ) ), "len(k)", float( hits[k].length( False, 0 ) )
#                print cap / float( hits[i].length( False, 0 ) ), cap / float( hits[k].length( False, 0 ) )
                scorei = ( hits[i].score, hits[i].stop - hits[i].start + 1 )
                scorek = ( hits[k].score, hits[k].stop - hits[k].start + 1 )
                if scorei > scorek:
                    logging.debug( "favour %s delete %s" % ( str( hits[i] ), str( hits[k] ) ) )
                    del hits[k]
                    k = k - 1
                elif scorek > scorei:
                    logging.debug( "favour %s delete %s" % ( str( hits[k] ), str( hits[i] ) ) )
                    del hits[i]
                    i = i - 1
                    break
                else:
                    logging.warning( "found two equaly good overlapping hits: %s %s" % ( hits[i - 1], hits[i] ) )

            k = k + 1

        i = i + 1
    return hits
