'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).
'''

from sys import stdout


def sequinwriter(featurelist, acc, outfile=None, mode="w"):
    out = ">Feature %s\n" % acc
    featurelist.sort(key=lambda x: x.start)
    for feature in featurelist:
        out += feature.sequinstr()

    if isinstance(outfile, str):
        with open(outfile, mode) as f:
            f.write(out)
    elif outfile == None:
        stdout.write(out)
    else:
        outfile.write(out)
