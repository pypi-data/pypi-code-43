'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).
'''

import re

import mitos.mito as mito

def unify_name_origin( name, strand ):
    """
    try to get a unified name for the origins
    """

    nm = name.upper()

    m = re.search( "([HL])[ -]STRAND", nm )
    if m != None:
        if m.group( 1 ) == 'H':
            return "OH"
        elif m.group( 1 ) == 'L':
            return "OL"
    m = re.search( "(LIGHT|HEAVY)", nm )
    if m != None:
        if m.group( 1 ) == 'HEAVY':
            return "OH"
        elif m.group( 1 ) == 'LIGHT':
            return "OL"

    m = re.search( "ORI[ -]*(L|H)", nm )
    if m != None:
        if m.group( 1 ) == 'H':
            return "OH"
        elif m.group( 1 ) == 'L':
            return "OL"

    m = re.search( "^O[ -]*(L|H)$", nm )
    if m != None:
        if m.group( 1 ) == 'H':
            return "OH"
        elif m.group( 1 ) == 'L':
            return "OL"

    m = re.search( "D-LOOP", nm )
    if m != None:
        return "OH"

    m = re.search( "ORIGIN|CONTR?OL", nm )
    if m != None:
        return "OH"

    return None

def unify_name_protein( name ):
    """
    get a unified name for rRNAs if possible 
    \param name a gbfile gene name
    """

    nm = name.lower().strip()

    # ATP
    m = re.match( "^atp.*(\d+$)", nm )
    if m != None:
        # print "^ATP.*(\d+$)"
        return "atp" + m.group( 1 )

    # COX
#    COI CO1
#    COII CO2
#    COIII CO3
#    COX1 CO1
#    COX2 CO2
#    COX3 CO3
#    cytochrome c oxidase subunit 1 CO1
#    cytochrome c oxidase subunit 2 CO2
#    cytochrome c oxidase subunit 3 CO3
#    cytochrome c oxidase subunit I CO1
#    cytochrome c oxidase subunit II CO2
#    cytochrome c oxidase subunit III CO3
#    cytochrome c subunit I CO1
#    cytochrome c subunit II CO2
#    cytochrome c subunit III CO3
#    cytochrome c subunit subunit I CO1
#    cytochrome c subunit subunit II CO2
#    cytochrome c subunit subunit III CO3
#    cytochrome oxidase 1 CO1
#    cytochrome oxidase 2 CO2
#    cytochrome oxidase 3 CO3
#    cytochrome oxidase I CO1
#    cytochrome oxidase II CO2
#    cytochrome oxidase III CO3
#    cytochrome oxidase subunit 1 CO1
#    cytochrome oxidase subunit 2 CO2
#    cytochrome oxidase subunit 3 CO3
#    cytochrome oxidase subunit I CO1
#    cytochrome oxidase subunit II CO2
#    cytochrome oxidase subunit III CO3

    m = re.search( "cox?([i]+|[123])$", nm )
    if m != None:
#        print "COX?([I]+|[123])", nm, m.group( 1 )
        if m.group( 1 )[0] == 'i':
            return "cox" + str( len( m.group( 1 ) ) )
        else:
            return "cox" + m.group( 1 )

    m = re.match( "^c.*[ -]([i]+|[123])$", nm )
    if m != None:
#        print "^C.*([I]+|[123]).*$", nm, m.group( 1 )
        if m.group( 1 )[0] == 'i':
            return "cox" + str( len( m.group( 1 ) ) )
        else:
            return "cox" + m.group( 1 )

#    cytochome b CYTB
#    cytochrome b CYTB
#    cob CYTB
#    Cyt b CYTB
#    CYTB CYTB
    m = re.match( "^[cyt]{3}|[cob]{3}$", nm )
    if m != None:
        # print "^[CYT]{3}|[COB]{3}.*$"
        return "cob"

    # NAD
    m = re.match( "[nad]{2,3}.*([123456][l]*)$", nm )
    if m != None:
        # print "[NAD]{2,3}.*([123456][L]*)$"
        return "nad" + str( m.group( 1 ) )

    return None

def unify_name_rrna( name ):
    """
    get a unified name for rRNAs if possible 
    \param name a gbfile gene name
    """
# @todo: strip()
# @todo: allow 15S 21S etcpp???
    nm = name.upper()

    # RRNA
    m = re.match( ".*(1[26]S).*", nm )
    if m != None:
        if m.group( 1 ) == "12S":
            return "rrnS"
        elif m.group( 1 ) == "16S":
            return "rrnL"
#        return m.group( 1 )

    m = re.match( "([SL]{1})-?R?RNA", nm )
    if m != None:
        # print "^([SL]{1})-?RRNA$"
        if m.group( 1 ) == 'S':
            return "rrnS"
        elif m.group( 1 ) == 'L':
            return "rrnL"

    m = re.match( "R?RNR?([LS12]{1})", nm )
    if m != None:
        # print "R?RNR?([LS12]{1})$"
        if m.group( 1 ) == 'S' or m.group( 1 ) == '1':
            return "rrnS"
        elif m.group( 1 ) == 'L' or m.group( 1 ) == '2':
            return "rrnL"

    m = re.match( "(SMALL|LARGE).*RNA.*", nm )
    if m != None:
        # print "^(SMALL|LARGE).*RNA.*$"
        if m.group( 1 ) == "SMALL":
            return "rrnS"
        elif m.group( 1 ) == "LARGE":
            return "rrnL"

    m = re.match( "(L|S)SU", nm )
    if m != None:
        # print "^(SMALL|LARGE).*RNA.*$"
        if m.group( 1 ) == "S":
            return "rrnS"
        elif m.group( 1 ) == "L":
            return "rrnL"

    return None

def unify_name_trna( name ):
    """
    get a unified name for rRNAs if possible 
    \param name a gbfile gene name
    """
    nm = name.upper().strip()

    if nm in mito.trnamap.keys():
        return mito.trnamap[nm]

#    print "->", nm
    # tRNA specified with 3 letter aa code (e.g. Ser)
    m = re.match( "^TRNA[ -]{0,1}(?P<trna>\w{3})(?P<number>\d{0,1})", nm )
    if m != None:
        d = m.groupdict()
#        print "a", d
        if d["trna"] + d["number"] in mito.trnamap:
#            print "Ax", nm
            return mito.trnamap[ d["trna"] + d["number"] ]
        elif d["trna"] in mito.trnamap:
#            print "A", nm
            return mito.trnamap[ d["trna"] ]

    # tRNA specified with 1 letter aa code (e.g. S)
    m = re.match( "^T[RN]{2}A[ -]{0,1}(?P<trna>\w)(?P<number>\d{0,1})", nm )
    if m != None:
        d = m.groupdict()
#        print "b", d
        if ( ( "trn" + d["trna"] + d["number"] ) in mito.trna ):
#            print "B", nm, m.group( 1 )
            return "trn" + d["trna"] + d["number"]
        elif ( ( "trn" + d["trna"] ) in mito.trna ):
            return "trn" + d["trna"]
    # tRNA specified with 1 letter aa code (e.g. S)
    m = re.match( "^T[RN]{2}[ -]{0,1}(?P<trna>\w)(?P<number>\d{0,1})", nm )
    if m != None:
        d = m.groupdict()
#        print "c", d,
        if ( ( "trn" + d["trna"] + d["number"] ) in mito.trna ):
#            print "Cx", nm
            return "trn" + d["trna"] + d["number"]
        elif ( ( "trn" + d["trna"] ) in mito.trna ):
#            print "C", nm
            return "trn" + d["trna"]


    # m = re.match("^TRNA?[ -]*([A-Z]{3})(\d*)$", nm)
    # if m != None and m.group(1) in trnamap:
    #    ret = trnamap[m.group(1)]
    #    if dsl == True and m.group(2) != None:
    #        ret += str(m.group(2))
    #    return ret

    # m = re.match("^T[RN]{2}([\w]{1})([\d]{0,1})", nm)
    # if m != None:
    #    ret = m.group(1)
    #    if dsl == True and m.group(2) != None:
    #        ret += str(m.group(2))
    #    return ret
    return None

def feature_type( name ):
    """
    determine the type of a feature given its unified name
    \param name the unified name
    \return "gene" (for proteins), "rRNA", "tRNA", "rep_origin", or None if unknown
    """

    if name == None:
        return None

    try:
        return mito.types[name]
    except:
        return None

#    elif name.startswith( "ATP" ) or name.startswith( "COX" ) or name.startswith( "ND" ) or name == "CYTB":
#        return "gene"
#    elif name == "12S" or name == "16S":
#        return "rRNA"
#    elif name == "OL" or name == "OH":
#        return "rep_origin"
#    elif name in trnamap.values():
#        return "tRNA"
#    else:
#        return None
