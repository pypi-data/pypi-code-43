'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).
'''


__all__ = ["genom"]

# import genom

def construct_genomes( g, g2 = None, circular = 1 ):
    """
    construct genomes and a name map given either a list of genomes or two genomes
    - only genes which occur exactly once per genome are accepted
    \param g a list of genomes or a single genome .. see g2
    \param g2 a nother single genome
    \param circular 1/0 determining if the genomes should be handled as circular
    \return (genomes, nmap) ! attantion: pair ! 
    """

    if g2 == None:
        genomes = g
    else:
        genomes = [g, g2]

    # print genomes

    # remove duplicates
    gcnt = {}
    for i in xrange( len( genomes ) ):
        cnt = {}
        for j in xrange( len( genomes[i] ) ):
            s, g = split_sign_gene( genomes[i][j] )
            if not g in cnt:
                cnt[g] = 0
            cnt[g] += 1
        tmpg = []
        for j in xrange( len( genomes[i] ) ):
            s, g = split_sign_gene( genomes[i][j] )
            if cnt[g] != 1:
                continue
            tmpg.append( genomes[i][j] )
            if not g in gcnt:
                gcnt[g] = 0
            gcnt[g] += 1
        genomes[i] = tmpg

    rgenomes = []
    simap = {}
    idx = 1
    for i in xrange( len( genomes ) ):
        rgenomes.append( [] )
        for j in xrange( len( genomes[i] ) ):
            s, g = split_sign_gene( genomes[i][j] )
            if gcnt[g] != len( genomes ):
                continue
            if not g in simap:
                simap[g] = idx
                idx += 1
            rgenomes[-1].append( s * simap[g] )

    nmap = [ "" for i in range( len( simap ) + 1 ) ]
    # print nmap
    # print simap
    for s in simap:
        nmap[ simap[s] ] = s
#    nmap = genom.vstring(nmap)

    genomes = []
#    for g in rgenomes:
#        vg = genom.vint(g)
#        genomes.append( genom.genom(vg, circular, nmap) )
#    return genomes,nmap



def split_sign_gene( sgene ):
    """
    helper funtion to split a signed gene in sign (+1/-1) and the name
    \param sgene signed gene (string)
    \return (name, sign)
    """

    if sgene.startswith( '-' ):
        gene = sgene[1:]
        sign = -1
    else:
        gene = sgene
        sign = 1
    return ( sign, gene )
