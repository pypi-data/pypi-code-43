"""
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).

Module that provides the diferent methods to merge featurelist.
"""

import logging

from ..mitfi import cmrealign
from ..feature import capcup, mitfifeature

def mergefeaturelist01( protlist, trnalist, rrnalist ):
    """
    This method implements the simpel way to belife all prots, rrna and trna's whit a score higher 40.
    """
    # Remove trna that colidate
    for trna in [x for x in trnalist if x.score < 40]:
        for featuer in rrnalist + protlist:
            if trna.start < featuer.stop and trna.start > featuer.start:
                trnalist.remove( trna )
                break
            elif trna.stop < featuer.stop and trna.stop > featuer.start:
                trnalist.remove( trna )
                break

    return protlist, trnalist, rrnalist

def mergefeaturelist( protlist, trnalist, rrnalist, parms, size = 0, circular = False ):
    """
    This method implements a way with most freedom to say what to for margin.
    
    tRNA_rRNA:40  -> trna raus schmeisen mit ueberlapung von 40 nuc zu irgend einer rrna
    gene_tRNA%10  -> gene raus schmeisen mit ueberlapung von 10 % (des genes) zu einer trna
    """
    for parm in parms:
        flist = []
        slist = []
        percent = False
        if parm[9] == "%":
            percent = True
        cutoff = int( parm[10:] )

        if parm[0:4] == "gene":
            flist = protlist
        elif parm[0:4] == "tRNA":
            flist = trnalist
        elif parm[0:4] == "rRNA":
            flist = rrnalist

        if parm[5:9] == "gene":
            slist = protlist
        elif parm[5:9] == "tRNA":
            slist = trnalist
        elif parm[5:9] == "rRNA":
            slist = rrnalist

        if percent:
            for ffeat in flist:
                for sfeat in slist:
                    if ffeat.overlap( sfeat, circular, size ) > cutoff:
                        flist.remove( ffeat )
                        break
        else:
            for ffeat in flist:
                for sfeat in slist:
                    if ( min( ffeat.stop, sfeat.stop ) - max( ffeat.start, sfeat.start ) + 1 ) > cutoff:
                        flist.remove( ffeat )
                        break

    return protlist, trnalist, rrnalist

def featureappend( appendList, featurelist, overlap = 35 , rnd = False ):
    """
    append a given list of features to an existing list of features such that
    no conflict emerges
    
    conflict: overlap is larger than the maximum, i.e. >overlap or >len(tRNA)-1 
    for tRNA rRNA overlaps
    
    if the rnd flag is set to True: 
    if tRNA-rRNA overlap with tRNA e-value > 10^-3 and tRNA included in rRNA
    the tRNA is removed 
    
    @param[in,out] appendList the list of new features to be checked for insertion
    @param[in,out] featurelist the list where the new features should be appended
    @param[in] overlap maximum allowed overlap of two features
    @param[in] rnd remove "low quality" tRNAs that overlap a rRNA 
    """

    # for tRNA check
    mintRNAscore = 1E-3

    # over new features
    for ffeat in appendList:

        # the tRNA that have to less score
        delettRNA = []
        # set put it in feature list default True
        conflict = False
        # over the old featurelist
        for sfeat in featurelist:
            # if sfeat.strand != ffeat.strand and (sfeat.type == "gene" and ffeat.type == "rRNA" or ffeat.type == "gene" and sfeat.type == "rRNA"):
            #    continue

            # set overlap to default
            maxoverlap = overlap
            # calculate the overlap
            cap = capcup( ffeat.start, ffeat.stop, sfeat.start, sfeat.stop, False, 0 )[0]

            # tRNA/rRNA compare the overlap ist len(tRNA) -1
            if ( sfeat.type == "tRNA" and ffeat.type == "rRNA" ) or \
                ( ffeat.type == "tRNA" and sfeat.type == "rRNA" ):

                if sfeat.type == "tRNA":
                    tr = sfeat
                    rr = ffeat
                else:
                    tr = ffeat
                    rr = sfeat

                maxoverlap = max( overlap, tr.length( False, 0 ) - 1 )
                # delete only in the first rnd
                if rnd:
                    # if the tRNAs evalue is insufficient AND
                    # the overlap is too large or the tRNA is included in the rRNA
                    # then the tRNA is marked to be removed
                    if tr.evalue > mintRNAscore and\
                        ( cap > maxoverlap or ( rr.start <= tr.start \
                                                and tr.stop <= rr.stop ) ):
                        delettRNA.append( tr )
                        continue

            # if overlap is > maximum allowed OR if one feature is included
            # in the other then the feature can not be included -> set the
            # conflict flag and stop search for another conflicting feature
            if cap > maxoverlap or \
                ( ffeat.start <= sfeat.start and sfeat.stop <= ffeat.stop ) or \
                ( sfeat.start <= ffeat.start and ffeat.stop <= sfeat.stop ):

                conflict = True
                break

        # if no conflicting feature is already in the list -> add it
        if not conflict:
            featurelist.append( ffeat )

            # over the tRNa to delet
            for delfeat in delettRNA:
                logging.debug( "featureappend: remove %s %d %d for %s %d %d" % ( delfeat.name, delfeat.start, delfeat.stop, ffeat.name, ffeat.start, ffeat.stop ) )
                featurelist.remove( delfeat )
        else:
            logging.debug( "featureappend: not adding %s %d %d" % ( ffeat.name, ffeat.start, ffeat.stop ) )

    featurelist.sort( key = lambda x:x.start )

    return featurelist

def appendlokalfeature( lokalHits, lname, rrnafeat, featurelist, seqlen, \
                        allowoverlap = 35, circular = True, debug = False ):
    """
    tries to fit in possible local hits. 
    
    A) a gap is searched, i.e. a region between two genes 
    1 if there is a global hit (which did not fit in) then a gap is searched
      only in the region covered by the best global hit. except if there 
      is no gap in this region, then the mode 2 is employed
      larger gaps are prefered.
    2 if there is no global hit the complete genome is considered. 
    
    In both modes the the gap that can take the best hit is searched, 
    i.e. good hits are prefered.

    B) When the gap was found all local hits are removed that do not fit 
    in the gap. Thus, also more than the best lokal hit can be chosen. 
    
    C) Finally the chosen local hits are checked if they overlap each other. 
    Good ones are prefered.
    
    @param[in] lokalHits the local hits for the rRNA with name lname
        - inluded features that overlap features in featurelist are removed
        - but the remaining list is not the same as the features that are 
          appended to featurelist! 
    @param[] lname the name of the rRNA
    @param[] rrnafeat the global hits (to check if there is any. even 
             if it is not inluded in the featurelist [due to overlap])
    @param[in,out] featurelist the current list of features predicted by mitos
    @param[in] seqlen length of the sequenc
        - features from lokalHits are included if not in conflict
    @param[] allowoverlap max allowed overlap with features in featurelist 
             (for tRNAs len-1 is allowed)  
    @param[] circular 
    """

    # sort local hits by evalue. determines potential insertion order
    lokalHits.sort( key = lambda x:( -x.mito, x.evalue ) )

    # sort features by start position for efficient overlap check
    featurelist.sort( key = lambda x:x.start )

    # get the hits of the global search for the considered RNA
    globalhit = [x for x in rrnafeat if x.name == lname]
    globalhit.sort( key = lambda x:( -x.mito, x.evalue ) )

    # set for global
    anfang = 0
    ende = 0
    localgap = False
    overORI = False

#     print "append local features"
#     print "local"
#     for l in lokalHits:
#         print l.name, l.start, l.stop
#     print "into"
#     for f in featurelist:
#         print f.name, f.start, f.stop
#     print "global"
#     for g in globalhit:
#         print g.name, g.start, g.stop, g.mito, g.evalue
#     print "-----"

    # if there is a global hit then the only consider the region covered by the
    # best global hit, i.e. the local features are fitted in the gaps between
    # the features in/overlapping this region. the largest gap where a local
    # feature fits perfectly is chosen if no such gap exists the largest is taken
    if len( globalhit ) > 0:
        logging.debug( "globalhit" )



#        print "GLOBALHIT"

        # get the start and end position of the global hit
        # TODO only the first???
        globalanfang = globalhit[0].start
        globalende = globalhit[0].stop

        # get all features which are within the range covered by the global hit
        # or overlap with the global hit,
        splitfeature = [feat for feat in featurelist if feat.start <= globalende and feat.stop >= globalanfang]


        # get the gaps (i.e. start stop of these gaps) between the features
        # included/overlapping the global hit -> globaleparts
        # - set i to the position where the first gap starts, i.e. the stop of a feature
        #   overlapping the globalstart of the globalstart itself
        # - append gaps betwen consecutive included features
        # - append a final feature if we are not already over the globalend
        #   (if the last included feature overlaps globalende)
        globaleparts = []
        if splitfeature[0].start < globalanfang:
            i = splitfeature[0].stop
        else:
            i = globalanfang
        for feat in splitfeature:
            if feat.start > i:
                globaleparts.append( ( i, feat.start ) )
                i = feat.stop
        if i < globalende:
            globaleparts.append( ( i, globalende ) )

        # sort the gaps in decreasing by their length (large first)
        globaleparts.sort( key = lambda x:-( x[1] - x[0] ) )

#        print globaleparts
        # if there are gaps .. fit it in
        # otherwise if there is no gap inbeween the features in the global hit then fit the
        # feature between any two features (i.e. not necessarily in the region of
        # the globalhit) -> localgap = True
        if len( globaleparts ) > 0:

            # check if any local feature fits perfectly in on of the gaps
            # starting with good hits and large gaps
            hitit = False
            for feat in lokalHits:
                for gap in globaleparts:
                    if feat.start > gap[0] and feat.stop < gap[1]:
                        globalanfang = gap[0]
                        globalende = gap[1]
                        hitit = True
                        break
                if hitit:
                    break

            # if there is no such perfect match take the largest gap
            if not hitit:
#                print "not hitit"
                globalanfang = globaleparts[0][0]
                globalende = globaleparts[0][1]
#            else:
#                print "hitit"
#            print "ganfang", globalanfang, "gende", globalende


            for feat in featurelist:
                if feat.type == "tRNA":
                    maxoverlap = max( allowoverlap, feat.length( False, 0 ) - 1 )
                else:
                    maxoverlap = allowoverlap

                if feat.stop - maxoverlap <= globalanfang:
                    anfang = feat.stop - maxoverlap
                elif feat.start + maxoverlap >= globalende:
                    ende = feat.start + maxoverlap
                    break

#            print "anfang", anfang, "ende", ende

            if ende == 0:
                overORI = True
                if circular:
                    if featurelist[0].type == "tRNA":
                        ende = featurelist[0].start + featurelist[0].length( False, 0 ) - 1
                    else:
                        ende = featurelist[0].start + allowoverlap
            # Sort after if it is in the global hit then sort after mitos and then sort after evalue
            lokalHits.sort( key = lambda x:( not ( x.start > globalanfang and x.stop < globalende ), -x.mito, x.evalue ) )
        else:
            localgap = True

    # if there is no global hit
    else:
        localgap = True

    if localgap:
        logging.debug( "localgap" )
#        print "LOCAL GAP"
        # get the gap with the best lokal feature (i.e. best evalue)
        i = 0

        # determine anfang and ende (i.e. start and stop of the gap where the best
        # local feature is fits in)
        # therefore loop over all local features (starting with the best)
        # and check if it does not overlap with any feature in featurelist
        overlap = False
        while i < len( lokalHits ):
#             print "check for", lokalHits[i].name, lokalHits[i].start, lokalHits[i].stop

            # default no overlap
            overlap = False
            # over all feature in featurelist
            for feat in featurelist:
                # determine max allowed overlap
                # - tRNA: max(allowoverlap, length of the tRNA - 1)
                # - else: allowoverlap
                if feat.type == "tRNA":
                    maxoverlap = max( allowoverlap, feat.length( False, 0 ) - 1 )
                else:
                    maxoverlap = allowoverlap

                # get the overlap
                cap = capcup( feat.start, feat.stop, lokalHits[i].start, lokalHits[i].stop, False, 0 )[0]

                # check if:
                # - overlap is greater that max allowed overlap
                # - one feature is included in the other
                # if so then the local feature cant be included and we can stop here
                if cap > maxoverlap or \
                    ( feat.start <= lokalHits[i].start and lokalHits[i].stop <= feat.stop ) or \
                    ( lokalHits[i].start <= feat.start and feat.stop <= lokalHits[i].stop ):
                    overlap = True
                    break

                # update anfang if this non overlapping feature is left of
                # the current local feature. thereby at the end anfang will
                # be the largest stop position of a non overlapping feature.
                # TODO not feature - maxoverlap (in if and equation)
                if feat.stop - maxoverlap < lokalHits[i].start:
                    anfang = feat.stop - maxoverlap

                # update ende and break loop when features right of the local
                # feature are found
                # TODO see above
                elif feat.start + maxoverlap > lokalHits[i].stop:
                    ende = feat.start + maxoverlap
                    break

            if len( featurelist ) == 0:
                ende = seqlen

            # if there is no overlap then the gap is found and the iteration can stop
            if not overlap:
                if ende == 0:
                    overORI = True
                    if circular:
                        if featurelist[0].type == "tRNA":
                            ende = featurelist[0].start + featurelist[0].length( False, 0 ) - 1
                        else:
                            ende = featurelist[0].start + allowoverlap
                break
            # else next feature check for overlap
            else:
                i += 1

    logging.debug( "anfang %d ende %d" % ( anfang, ende ) )

    # remove all local features that do not fit in the gap
    # i.e. between anfang and ende
    # TODO should we check for overlap, i.e. if overlap is false
    i = 0
    while i < len( lokalHits ):
        logging.debug( "check %s %d %d" % ( lokalHits[i].name, lokalHits[i].start, lokalHits[i].stop ) )
        # if the gap over the ORI
        if overORI:
            # if start befor the gap begin and stop after the end
            if lokalHits[i].start < anfang and lokalHits[i].stop > ende:
                lokalHits.remove( lokalHits[i] )
                logging.debug( "\tremove" )
            # else look at next feature
            else:
#                print "KEEP"
                i += 1

        # if its a normal gap
        else:

            # if start befor the gap begin and stop after the end
            if lokalHits[i].start < anfang or lokalHits[i].stop > ende:
                lokalHits.remove( lokalHits[i] )
                logging.debug( "\tremove" )
            # else look at next feature
            else:
#                print "KEEP"
                i += 1

    # insert the remaining local features in the feature list
    # but only if they do not overlap with local features
    # of higher quality (i.e. inserted earlier)
    query = set()
    for feat in lokalHits:
        fqset = set( range( feat.qstart, feat.qstop ) )
        if len( query.intersection( fqset ) ) <= allowoverlap:
            query |= fqset  # append fqset positions

            logging.debug( "final %s %d %d" % ( feat.name, feat.start, feat.stop ) )
            featurelist.append( feat )
#            print "APPEND", feat

    # return feature list
    return featurelist

def checklokalfeature( localcheck, featurelist, sequence, refdir ):
    """
    - remove single local feature <= 55 nt 
    
    - check and combine local features if they can be merged: 
      * same strand 
      * difference of the distance in sequence and query by factor < 1.5
    
    @param localcheck the name of the rRNA to check 
    @param featurelist the list of features
    @param sequence the sequence of the genome
    """

    # over all lokal append rRNA's
    for lname in localcheck:

        # get all features in the feature list which are due to local features
        localfeats = [x for x in featurelist if x.name == lname]
#        print localfeats

        # remove if single feature shorter 56
        if len( localfeats ) == 1 and localfeats[0].length( False, 0 ) <= 55:
            logging.debug( "remove %s %d %d (single & <55)" % ( localfeats[0].name, localfeats[0].start, localfeats[0].stop ) )
            featurelist.remove( localfeats[0] )
            continue

        # TODO why sort by evalue, its already clear that all features fit.
        localfeats.sort( key = lambda x:x.evalue )

        for feat in localfeats:
            logging.debug( "%s %d %d %d query %d %d %g" % ( feat.name, \
                        feat.start, feat.stop, feat.strand, feat.qstart, feat.qstop, feat.evalue ) )

        featurelist.sort( key = lambda x:x.start )
        i = 0
        while i < len( localfeats ):
            j = i + 1
            newround = False

            logging.debug( "i %d %d %d query %d %d " % ( localfeats[i].strand, \
                localfeats[i].start, localfeats[i].stop, localfeats[i].qstart, localfeats[i].qstop ) )
            while j < len( localfeats ):

                logging.debug( "j %d %d %d query %d %d " % ( localfeats[j].strand, \
                    localfeats[j].start, localfeats[j].stop, localfeats[j].qstart, localfeats[j].qstop ) )

                if localfeats[i].strand != localfeats[j].strand:
                    j += 1

                    logging.debug( "different strand" )
                    continue

                # compute distance of the mid points of the features (i and j) in sequence and query
                genomdist = abs( ( localfeats[i].stop - localfeats[i].start ) / 2.0 + localfeats[i].start - \
                                    ( ( localfeats[j].stop - localfeats[j].start ) / 2.0 + localfeats[j].start ) )
                querydist = abs( ( localfeats[i].qstop - localfeats[i].qstart ) / 2.0 + localfeats[i].qstart - \
                                    ( ( localfeats[j].qstop - localfeats[j].qstart ) / 2.0 + localfeats[j].qstart ) )

                logging.debug( "genomdist = %d" % ( genomdist ) )
                logging.debug( "querydist = %d" % ( querydist ) )

                if genomdist == 0 or querydist == 0:
                    j += 1
                    continue

                faktor = genomdist / querydist

                if faktor <= 2 / 3.0 or faktor >= 1.5 :
                    j += 1

                    logging.debug( "faktor >= 1,5" )
                    continue

                # check if the two features are in correct order and
                # if another feature is in between
                together = True
                # feature i left of j
                if localfeats[i].start < localfeats[j].start:
                    # if strand == 1 quer_i  < query_j or strand == -1 query_i > quer_j
                    if ( localfeats[i].strand == 1 and localfeats[i].qstart < localfeats[j].qstart ) or \
                       ( localfeats[i].strand == -1 and localfeats[i].qstart > localfeats[j].qstart ):

                        # check if a feature is between the two rRNA's
                        for feat in featurelist:
                            # with +1 and -1 we allow overlap (that its not to much is already clear )
                            # if we would not add the feature i and j would match the expression
                            if localfeats[i].start + 1 < feat.start and feat.stop < localfeats[j].stop - 1:

                                logging.debug( "%s %d %d in between" % ( feat.name, feat.start, feat.stop ) )
                                together = False
                                break
                            elif localfeats[j].start < feat.start:
                                break
                    else:
                        together = False

                        logging.debug( "query and genom in diferrent orientation" )
                else:
                    # if strand == -1 quer_i  < query_j or strand == 1 query_i > quer_j
                    if ( localfeats[i].strand == -1 and localfeats[i].qstart < localfeats[j].qstart ) or \
                       ( localfeats[i].strand == 1 and localfeats[i].qstart > localfeats[j].qstart ):
                        # check if a feature is between the to rRNA's
                        for feat in featurelist:
                            if localfeats[j].start + 1 < feat.start and feat.stop < localfeats[i].stop - 1 :
                                logging.debug( "%s %d %d in between" % ( feat.name, feat.start, feat.stop ) )
                                together = False
                                break
                            elif localfeats[i].start < feat.start:
                                break
                    else:
                        together = False

                        logging.debug( "query and genom in difernt orientation" )


                if together:

                    logging.debug( "merge %s %d %d with %s %d %d" % ( localfeats[i].name, localfeats[i].start, localfeats[i].stop, localfeats[j].name, localfeats[j].start, localfeats[j].stop ) )
                    # get start and stop position, sequence, and a structure (from cmrealign)
                    start = min( localfeats[i].start, localfeats[j].start )
                    stop = max( localfeats[i].stop, localfeats[j].stop )
                    sseq = str( sequence.subseq( start, stop, localfeats[i].strand ) )
                    struct = cmrealign( sseq, lname, refdir )

                    newfeat = mitfifeature( name = lname, type = "rRNA", start = start, stop = stop, \
                                            strand = localfeats[i].strand, method = "mitfi", \
                                            score = ( localfeats[i].score + localfeats[j].score ) / 2.0, \
                                            sequence = sseq, struct = struct, \
                                            anticodonpos = None, anticodon = None, \
                                            qstart = min( localfeats[i].qstart, localfeats[j].qstart ), \
                                            qstop = max( localfeats[i].qstop, localfeats[j].qstop ), \
                                            evalue = ( localfeats[i].evalue + localfeats[j].evalue ) / 2.0, \
                                            pvalue = ( localfeats[i].pvalue + localfeats[j].pvalue ) / 2.0, \
                                            model = lname, local = True, \
                                            mito = ( localfeats[i].mito + localfeats[j].mito + 1 ) / 2.0, \
                                            evalscore = ( localfeats[i].evalscore + localfeats[j].evalscore ) / 2.0 )

                    featurelist.remove( localfeats[i] )
                    featurelist.remove( localfeats[j] )
                    featurelist.append( newfeat )


                    localfeats[i] = newfeat
                    localfeats.remove( localfeats[j] )

#                    localfeats.sort( key = lambda x:x.evalue )
                    featurelist.sort( key = lambda x:x.start )
                    newround = True

                    logging.debug( "new feature" )
                    break
                else:
                    j += 1

                    logging.debug( "don't put together" )

            if not newround:
                i += 1

                logging.debug( "next feature" )
    return featurelist
