'''
@author: M. Bernt

This is a confidential release. Do not redistribute without 
permission of the author (bernt@informatik.uni-leipzig.de).

Generate the files needed for blasting
'''

from update import prepareFiles
import argparse

usage = "generate blast data bases from the genbank files in a directory"

parser = argparse.ArgumentParser( description = usage )

parser.add_argument( "--dir", action = "store", required = True, metavar = "DIR", help = "output directory" )
args = parser.parse_args()

prepareFiles( args.dir )
