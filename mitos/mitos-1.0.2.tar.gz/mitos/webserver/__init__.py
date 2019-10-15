'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).
'''


from mitos.bedfile import bedwriter
from mitos.gfffile import gffwriter
from mitos.tbl import tblwriter
from mitos.sequence import fastawriter
from mitos.feature import genorderwriter

import mitos.CONFIG as CONFIG

import re

def makeMitos( content, phase, titlesfx = "", news = "", track = CONFIG.MITOS_TRACKING_CODE ):
    """
    create the mitos website header and footer
    and set the given content inside
    @param[in] content the content to write in between head and foot
    @param[in] phase integer 1,2,... determining the image in the right top corner
    @param[in] titlesfx suffix to append to the title
    @param[in] track set tracking code to use, i.e. set empty if no tracking. default is taken from CONFIG 
    """

    if phase == 1:
        imgidx = ""
    elif phase == 2:
        imgidx = "_2"
    else:
        imgidx = "_3"

    ret = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html><head>
<title>MITOS Web Server {tsfx}</title>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">

<link rel="icon" href="favicon.ico" type="image/x-icon">
<link rel="apple-touch-icon" href="icon-57.png" />
<link rel="apple-touch-icon" sizes="72x72" href="icon-72.png" />
<link rel="apple-touch-icon" sizes="114x114" href="icon-114.png" />
<link rel="apple-touch-icon" sizes="144x144" href="icon-144.png" />


<link rel="stylesheet" href="mito/main.css" type="text/css">
<script src="mito/jquery-1.10.0.min.js" type="text/javascript"></script>
<script src="mito/main.js" type="text/javascript"></script>
</head>
<body>
<div id="container">
<div id="header">
    <div id="headerleft">
        <img src="mito/header_left.gif" alt="head left">
    </div>
    <div id="headerright">
        <img src="mito/header_right{imgidx}.gif" alt="head right">
    </div>
    <div id="headermain"><div onmouseover='this.style.cursor="pointer"' onclick ='window.location = "http://{mitosurl}";' style="display: inline-block;"><b>MITOS</b> WebServer</div></div>
</div>
<div id="column2">
    <div id="contentmain">
        <div style="float:right;">
            <a href="http://{mitosurl}">new job</a> |
            <a href="http://pacosy.informatik.uni-leipzig.de/crex">CREx</a> |  
            <a href="http://trnadb.bioinf.uni-leipzig.de">tRNAdb</a> | 
            <a href="http://www.bioinf.uni-leipzig.de">Bioinformatik</a>
        </div><br>
{content}
    </div>
    <div id="newsmain">
{news}
    </div>
</div>
<div id="footer" style="clear:both;">
    <div id="footerleft"></div>
    <div id="footerright"></div>
    <div id="footermain">
        <div style="float:left;">Contact:&nbsp;{mail}
        </div>
        <div style="float:right;">
            <a href="help.py" style="text-decoration:none;"><img src="mito/help-icon.gif" alt="help"></a>
        </div>
        <div>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="history.py">history</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="stats.py">Status & Statistics</a>
        </div>
    </div>
</div>
</div>
{trackcode}
</body>
</html>""".format( imgidx = imgidx, content = content, news = news, \
                   trackcode = track, tsfx = titlesfx, mitosurl = CONFIG.WEBPATH, \
                   mail = CONFIG.MITOS_CONTACTMAILCRYPT )

    return ret



def makeDBserv( contend, search = False, liste = [], spliter = 10, resultspliter = 3 ):
    ret = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">\n'
    ret += '<html><head>\n\n'
    ret += '<title>Mitos DB server</title>\n'
    ret += '<meta http-equiv="content-type" content="text/html; charset=UTF-8">\n'
    ret += '<link rel="stylesheet" href="dbserv/main.css" type="text/css">\n'
    ret += '<script src="dbserv/main.js" type="text/javascript"></script>\n'
    ret += '<script src="dbserv/jquery-1.5.1.js"></script>\n'
    if search:
        ret += '<script>\n'
        ret += 'var results = new Array();\n'
        ret += 'var Sides = new Array();\n'
        ret += 'var spliter = %d;\n' % ( resultspliter )

        k = 0
        for i in range( len( liste ) ):
            if i % spliter == 0:
                ret += 'Sides[%d] = "' % ( k )
            if i % spliter == ( spliter - 1 ) or i == len( liste ) - 1:
                ret += '%s";\n' % ( liste[i] )
                k += 1
            else:
                ret += "%s," % ( liste[i] )

        ret += '</script>\n'
        ret += '<script src="dbserv/search.js"></script>\n'
    ret += '<div id="container">\n'
    ret += '<div id="header">\n'
    ret += '<div id="headerleft"><img src="dbserv/header_left.gif">\n'
    ret += '</div>\n\n'
    ret += '<div id="headerright">'
    ret += '<img src="dbserv/header_right.gif">\n'
    ret += '</div>\n'
    ret += '<div id="headermain"><div style="float: left;font-size:2.3em;"><b>MITOS</b> DBServer <b> BETA</b></div>\n'
    ret += '<div id="search"><form name="mtdb" action="search.py" method="POST"><input id = "searchIn" type="text" name="name" value="" style="width: 200px;"><input type = "submit" value="Search"></form></div>\n'
    ret += '</div>\n'
    ret += '</div>\n'
    ret += '<div id="column2" align="center">\n'
    ret += '<div id="contentmain" width="300">\n'
    ret += '<div id ="headmenu" style="float:right;">\n'
    ret += '<a href="http://mitos.bioinf.uni-leipzig.de">MITOS Webserver</a> | \n'
    ret += '<a href="http://trnadb.bioinf.uni-leipzig.de">tRNAdb</a> | \n'
    ret += '<a href="http://www.bioinf.uni-leipzig.de">Bioinformatik</a>\n'
    ret += '</div><br>\n'
    ret += contend
    ret += '</div>\n'
    ret += '</div>\n'
    ret += '<div id="footer">\n'
    ret += '<div id="footerleft">&nbsp;</div>\n'
    ret += '<div id="footerright">&nbsp;</div>\n'
    ret += '<div id="footermain"><div style="float:right;"><a href="help.py" style="text-decoration:none;"><img src="dbserv/help-icon.gif"></a></div><div style="float:left;">Contact: <script type=\'text/javascript\'>\n'
    ret += 'var pref = \'&#109;a\' + \'i&#108;\' + \'&#116;o\';\n'
    ret += "var attribut = 'hr' + 'ef' + '='; var first = '%6D%69%74%6F'; var at = '%40'; var last = '&#x62;&#x69;&#x6F;&#x69;&#x6E;&#x66;&#x2E;&#x75;&#x6E;&#x69;&#x2D;&#x6C;&#x65;&#x69;&#x70;&#x7A;&#x69;&#x67;&#x2E;&#x64;&#x65;';\n"
    ret += "var first2 = '&#x6D;&#x69;&#x74;&#x6F;'; var at2 = '&#x40;'; var last2 = '&#98;&#105;&#111;&#105;&#110;&#102;&#46;&#117;&#110;&#105;&#45;&#108;&#101;&#105;&#112;&#122;&#105;&#103;&#46;&#100;&#101;';\n"
    ret += "document.write( '<a ' + attribut + '\\'' + pref + ':' + first + at + last + '\\'>' );\n"
    ret += "document.write( first2 + at2 + last2 ); document.write( '<\/a>' ); </script> <noscript>\n"
    ret += "<div style='display:none; '>are-</div><div style='display:inline; '>&#x6D;&#x69;&#x74;&#x6F;</div><div style='display:none; '>-xya34</div><div style='display:inline; '>[at]</div><div style='display:none; '>ddks-</div><div style='display:inline; '>&#98;&#105;&#111;&#105;&#110;&#102;&#46;&#117;&#110;&#105;&#45;&#108;&#101;&#105;&#112;&#122;&#105;&#103;&#46;&#100;&#101;</div> </noscript></div></div>\n"
    ret += '</div>\n'
    ret += '</div>\n'
    ret += '</body></html>\n'

    return ret

def genoutput( featurelist, acc, outputtype, request, sequence = None, code = None ):
    """
    generate an output of specified type into the request 
    @param[in] featurelist the list of features
    @param[in] acc the sting to describe the species
    @param[in] outputtype the type to generate (bed,gff,tbl,txt,fas)
        txt gives gene order
        fas gives the sequences of the features in fasta
    @param[in,out] request the request to write into
    @param[in] sequence the sequence 
    """

    if outputtype == "bed":
        bedwriter( featurelist, acc, request )
    elif outputtype == "gff":
        gffwriter( featurelist, acc, request )
    elif outputtype == "tbl":
        tblwriter( featurelist, acc, request )
    elif outputtype == "txt":
        genorderwriter( featurelist, acc, request )
    elif outputtype == "fas" or outputtype == "faa":
        if outputtype == "fas":
            code = None
        fastawriter( featurelist, sequence, code, acc, outputtype, outfile = request )
    else:
        request.write( "Error unknown output-type" )


# def parsepostreq( lines ):
#    """
#
#    """
#
#    d = dict()
#    name = ""
#    wert = ""
#    file = []
#    filename = ""
#    for i in range( len( lines ) ):
#        line = lines[i]
#        if line.startswith( "Content-Disposition" ):
#            if name != "":
#                if name != "myFile":
#                    d[name] = wert.replace( "\n", "" ).replace( "\r", "" )
#                else:
#                    header, seq = fastareader( file )
#                    d[name] = [filename, header, seq]
#                name = ""
#                wert = ""
#                file = []
#            x = re.search( "name=\"(.*?)\"", line )
#            if x != None:
#                name = x.group( 1 )
#            if name == "myFile":
#                x = re.search( "filename=\"(.*?)\"", line )
#                if x != None:
#                    filename = x.group( 1 )
#
#        elif  line.startswith( "Content" ) or line == "":
#            continue
#
#        elif line.startswith( "---" ):
#            if name != "":
#                if name != "myFile":
#                    d[name] = wert.replace( "\n", "" ).replace( "\r", "" )
#                else:
#                    header, seq = fastareader( file )
#                    d[name] = [filename, header, seq]
#                name = ""
#                wert = ""
#                file = []
#        else:
#            if name != "myFile":
#                wert += line
#            else:
#                file.append( line )
#
#
#    return d



