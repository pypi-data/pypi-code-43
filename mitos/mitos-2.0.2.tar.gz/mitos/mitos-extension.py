import re
import sys
import os
import logging
from os.path import splitext
from Bio import GenBank
from Bio import SeqIO
from Bio.Alphabet import IUPAC
from Bio import Seq
from Bio import Data
import argparse
import glob
from Bio.Blast import NCBIXML
from Queue import *
import sequence
from Bio.Seq import Seq
import time

import cPickle as pickle

from feature import feature
import mito
from sequence import sequence
from trna import codon, CodonError, L1, L2, S1, S2
blast_dbs_path = "/Users/Abdullah/blast/db/"


def bidirectional_best_hit( data, nmap_dict ):

    """
    cluster the bidirectional best hits genes together

    @param[in] data the dictionary resulted from blast_xml_handle
    @param[in]  nmap the dictionaty which maps accession,position -> name
    @return the array of sets which contains the bidirectional best hit genes
    """

    arr = {}  # map of qacc, sacc, qpos, spos to evalue
    qmap = {}  # map of qacc,qpos to spos
    smap = {}  # map of sacc,spos to qpos
    q = Queue()  # queue


    for q in data:
        for s in data[q]:
            qacc = q[0]
            qstart = q[1][0]
            qend = q[1][1]
            sacc = s[0]
            sstart = s[1][0]
            send = s[1][1]
            eval = data[q][s]


            qpos = ( qstart, qend )
            spos = ( sstart, send )
            # print q, s

            # filling the minimum evalue dict (arr)
            if not qacc in arr:
                arr[qacc] = {}

            if not sacc in arr[qacc]:
                arr[qacc][sacc] = {}

            if not qpos in arr[qacc][sacc]:
                arr[qacc][sacc][qpos] = {}

            if not spos in arr[qacc][sacc][qpos]:
                arr[qacc][sacc][qpos][spos] = 0

            try:
                if eval < arr[qacc][sacc][qpos][spos]:
                    arr[qacc][sacc][qpos][spos] = eval
            except:
                arr[qacc][sacc][qpos][spos] = eval

    # looping through the minimum evalue dictionary to find the bidirectional best hit genes

    sets = []
    for qacc in arr:
        for sacc in arr[qacc]:

            if not qacc in qmap:
                qmap[qacc] = {}
            if not sacc in qmap[qacc]:
                qmap[qacc][sacc] = {}

            if not sacc in smap:
                smap[sacc] = {}

            if not qacc in smap[sacc]:
                smap[sacc][qacc] = {}
                # print "1"

            for qpos in arr[qacc][sacc]:  # determine best subject of each query and best query of each subject
                for spos in arr[qacc][sacc][qpos]:
                    if not qpos in qmap[qacc][sacc]:
                        qmap[qacc][sacc][qpos] = spos

                    elif arr[qacc][sacc][qpos][qmap[qacc][sacc][qpos]] < arr[qacc][sacc][qpos][spos]:
                        qmap[qacc][sacc][qpos] = spos

                    if not spos in smap[sacc][qacc]:
                        smap[sacc][qacc][spos] = qpos

                    elif arr[qacc][sacc][smap[sacc][qacc][spos]][spos] < arr[qacc][sacc][qpos][spos]:
                        smap[sacc][qacc][spos] = qpos



    # Cluster the bidirectional best hits entries
    print "something"
    # print len(qmap),len(smap)
    # print qmap
    j = 0
    tt = 0
    for qacc in qmap:
        j += 1
        # print j
        for sacc in qmap[qacc]:
            for qpos in qmap[qacc][sacc]:

                for ssacc in smap:
                    for sqacc in smap[ssacc]:
                        for sspos in smap[ssacc][sqacc]:

                            if qmap[qacc][sacc][qpos] == sspos and smap[ssacc][sqacc][sspos] == qpos:
                                # print nmap_dict[qacc][qpos], "\t",nmap_dict[ssacc][sspos]
                                qtuple = tuple( nmap_dict[qacc][qpos] )
                                stuple = tuple( nmap_dict[ssacc][sspos] )
                                if "ATP" in nmap_dict[qacc][qpos] or "ATP" in nmap_dict[ssacc][sspos]:
                                    print nmap_dict[qacc][qpos], nmap_dict[ssacc][sspos]
                                qind = None
                                sind = None
                                # find the index in sets which contains q,qp and the index which contains s,sp => a number from 0 to len(sets)-1 or
                                # when there is no index, i do index = none or any value
                                # 2 indices which tells us if q,qp are found and if s,sp or if its not found
                                # for loop on the set of sets and get the indexes needed

                                for i in range( len( sets ) ):
                                    # print len(sets)
                                    if qtuple in sets[i]:
                                        qind = i

                                    if stuple in sets[i]:
                                        sind = i

                                # print sets
                                # case 1:    [q,qp] and [s,sp] are not found => start a new set to the array of sets and fill [q,qp] and [s,sp]

                                if qind is None and sind is None:
                                    sets.append( set( [qtuple, stuple] ) )
                                    # print qacc, qpos, ssacc, sspos


                                # case 2:    [q,qp] are found and [s,sp] are not found => add [s,sp] to the set where [q,qp] are
                                if not qind is None and sind is None:
                                    sets[qind].add( stuple )

                                # case3: [q,qp] are not found and [s,sp] are found => add [q,qp] to the set where [s,sp] are
                                if qind is None and not sind is None:
                                    sets[sind].add( qtuple )

                                # case4: both are found in different sets => we need to combine them and delete the other two
                                if not qind is None and not sind is None and qind != sind:
                                    sets[qind].add( stuple )
                                    del sets[sind]

                                # case5: both are found in the same set => we do nothing
                                if not qind is None and not sind is None and qind == sind:
                                    continue


    # for i in range(len(sets)):
    #    print sets[i],"\n"
    print len( sets )
    return sets

def blast_xml_handle( blastfile, features_map_dict ):

    """
     get the needed data from the blast xml file
    
     @param[in] blastfile, the file generated from the blast all vs all run
     @param[in]  features_map_dict, map of feature_id -> feature_name, feature_accession, feature_start, feature_end
     @return the dictionary of the blast reads, the nmap dict which maps (accession,position) -> name
     """

    blasthandle = open( blastfile, 'r' )

    infile = ""
    data = {}
    subjects = []


    nmap = {}

    i = 0
    blast_records = NCBIXML.parse( blasthandle )
    for record in blast_records:

        query_record = str( record.query )
        i += 1


        query_accession = features_map_dict[query_record]['accession']
        # print "query", query_record
        query_name = features_map_dict[query_record]['name']


        query_location_start = features_map_dict[query_record]['start']
        query_location_end = features_map_dict[query_record]['end']


        query_pos = ( query_location_start, query_location_end )
        if not query_accession in nmap:
            nmap[query_accession] = {}
        if not query_pos in nmap[query_accession]:
            nmap[query_accession][query_pos] = list( query_name )

        if not ( query_accession, ( query_location_start, query_location_end ) ) in data:
                data[( query_accession, ( query_location_start, query_location_end ) )] = {}
        min = 0
        for alignment in record.alignments:
            for hsp in alignment.hsps:
                subject_record = str( alignment.hit_def ).strip( ' ' )

                subject_accession = features_map_dict[subject_record]['accession']

                subject_name = features_map_dict[subject_record]['name']

                subject_location_start = features_map_dict[subject_record]['start']
                subject_location_end = features_map_dict[subject_record]['end']

                try:
                    if hsp.expect < data[( query_accession, ( query_location_start, query_location_end ) )][( subject_accession, subject_name )]:
                        data[( query_accession, ( query_location_start, query_location_end ) )][( subject_accession, ( subject_location_start, subject_location_end ) )] = hsp.expect
                except:
                    data[( query_accession, ( query_location_start, query_location_end ) )][( subject_accession, ( subject_location_start, subject_location_end ) )] = hsp.expect


    return data, nmap


def get_features( gbfile ):

        gbhandle = open( gbfile, "r" )
        record = SeqIO.read( gbhandle, "gb" )
        gbhandle.close()

        return record.features, record.seq



def get_sequences( gbfiles ):
    """
    MB comment the functions: should contain: 
    1) what the function does : get all sequences, and features of a specific type from all the genbank files
    2) the input parameters : gb files
    3) the output : array which contains all features of the chosen types taken from the genbank files
    """
    all_seq_features = []
    for fl in args.gbfiles:
        seq = ""
        # MB: Get the accession from the gb file    ####    done
        record = SeqIO.read( fl, "genbank" )
        accession = record.name

        all_features, gbseq = get_features( fl )

        seq = sequence( str( gbseq ) )

        for feature in all_features:
            if feature.type in ["rRNA", "CDS"]:
                log_features_locations = _parse_feature_locations( feature )

                # MB you do not need to call it in a loop
                # (log_features_name is overwritten all the time anyway)

                log_features_name = _parse_feature_name( feature )

                # MB: Why do you only use the first location?        ### check if this deals with the split features location

                # concatenate subsequences and do no take the full ones --not done
                if len( log_features_locations ) > 1:
                    for li in range( len( log_features_locations ) ):
                        start = log_features_locations[li][0]
                        end = log_features_locations[li][1]
                        strand = log_features_locations[li][2]
                        fseq += str( seq.subseq( start, end, strand ) )
                else:
                    start = log_features_locations[0][0]
                    end = log_features_locations[0][1]
                    strand = log_features_locations[0][2]
                    fseq = str( seq.subseq( start, end, strand ) )

                # print accession, set(log_features_name),log_features_locations
                # MB: you always use the forward strand. this is wrong if you have a feature with strand -1
                # solution: -> use the sequence.subseq() method [therefore you need to create a sequence object first]    ### done
                all_seq_features.append( ( accession, set( log_features_name ), fseq, start, end ) )
    return all_seq_features


def _parse_feature_name( f ):
        """
        try to determine the name of a feature
        for trna, rrna, and genes try to guess the name from the gene or product qualifier

        MB remove the strand parameter if not used
        @param[in] f the feature
        @param[in] strand the strand of the feature
        @return the name of None (if could not be determined)
        """

        features_arr = []
        for q in f.qualifiers:
            for x in f.qualifiers[q]:
                if q in ["gene", "product"]:
                    # save them into file
                    features_arr.append( x )
                    # print x
                if q in ["standard_name", "note", "direction", "product", "gene"]:
                    # save them file
                    features_arr.append( x )
                    # print x
        return features_arr

def _parse_feature_locations( feature ):
        """
        parse location(s) from subfeatures 
        @return list of locations, i.e. list of triples (start, stop, strand)
        """

#        print feature, dir( feature )
        loc = []
        if len( feature.sub_features ) > 0:
            for f in feature.sub_features:
                loc += _parse_feature_locations( f )
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

def save_to_fasta( all_features_arr, fasta_file_path, blast_db_name, xml_file_path ):
    global blast_dbs_path
    """
    1) what the function does : takes the features array generated from get_sequences and transfrom it to fasta file and from the fasta it creates a blast db and do the blast all vs all and returns the xml file
    2) the input parameters : 
    all_features_arr: feature array taken from get_sequence
    fasta_file_path : path of the output fasta file of the features with their sequences
    blast_db_path: path of the output blast data base
    xml_file_path: path of the output xml from blast all vs all run
    3) the output : 
    fasta file for all the features for all the gb files
    blast data base file
    xml file generated from blast run
    """
    # MB you do not need the out variable
    # write to the file directly        ###    done

    features_map = {}
    f = open( fasta_file_path, "w" )
    for i in range( len( all_features_arr ) ):
        f.write( "> " + str( i ) + "\n" + all_features_arr[i][2] + "\n" )
        if not str( i ) in features_map:
            features_map[str( i )] = {'name':all_features_arr[i][1], 'start':all_features_arr[i][3], 'end':all_features_arr[i][4], 'accession':all_features_arr[i][0]}
            # ## i can only make an id for each feature which will map to name, location (start and end) and accession

    f.close()

    print "\n creating blast data base  ...\n"
    # os.system( "makeblastdb -in " + fasta_file_path + " -dbtype nucl -out " + blast_dbs_path + blast_db_name )
    print "\n blast data base created from " + fasta_file_path + "\n"

    print "\n Blast all vs all is running ...\n"
    # os.system( "blastn -db " + blast_dbs_path + blast_db_name + " -num_threads 3 -evalue 1e-10 -outfmt 5 -query " + fasta_file_path + " -out " + xml_file_path )
    print "\n blast run done and xml file created \n"

    return features_map

def uniq( inlist ):
    uniques = []
    for item in inlist:
        if item not in uniques:
            uniques.append( item )
    return uniques
def uniq_col_list( list, col ):
    un = []
    for val in range( len( list ) ):
        un.append( list[val][col] )
    return uniq( un )










if __name__ == '__main__':
    usage = "usage: %prog dirs"
    parser = argparse.ArgumentParser( description = usage )
    parser.add_argument( 'gbfiles', metavar = 'DIRS', nargs = '+', help = 'gb files' )
    parser.add_argument( 'fastafile', help = 'output file' )
    args = parser.parse_args()

    start = time.time()
    allgbfiles = list( f for arg in args.gbfiles for f in glob.glob( arg ) )



    print "loading sequences and features ... \n"
    # to_fasta_features=get_sequences(allgbfiles)
    print "sequences and features successfully loaded \n"

    # all_feat_map = save_to_fasta(to_fasta_features, args.fastafile, "Mammalia56_blast_db", "/Users/Abdullah/Documents/PhD/work/mitos-extension/Mammalia_blast56.xml")




    # blast_parsing_result, nmap = blast_xml_handle("/Users/Abdullah/Documents/PhD/work/mitos-extension/Mammalia_blast56.xml",all_feat_map )

     # just for testing purposes
#    output = open('mammalia_blast_res.pkl', 'wb')
#    pickle.dump(blast_parsing_result, output)
#    output.close()
#
#    output = open('mammalia_nmap.pkl', 'wb')
#    pickle.dump(nmap, output)
#    output.close()

# #
    pkl_file = open( 'mammalia_blast_res.pkl', 'rb' )
    blast_dict = pickle.load( pkl_file )
    pkl_file.close()

    pkl_file = open( 'mammalia_nmap.pkl', 'rb' )
    nmap_dict = pickle.load( pkl_file )
    pkl_file.close()

    bidirectional_best_hit( blast_dict, nmap_dict )


end = time.time()
print "elapsed time", end - start






