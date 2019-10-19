import os, sys, datetime
import argparse
import deepcon
from deepcon import deepconcovariance

################################################################################
def main(aln, file_rr, png=None):
    if not png:
      print ('Start 2 arg deepcon')
      deepcon.main(aln,file_rr)
      print ('Done 2 arg deepcon')
    
    else:
      print ('Start 3 arg deepcon')
      deepcon.main(aln,file_rr,png)
      print ('Done 3 arg deepcon')
      
################################################################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--aln'
        , help = 'Input Alignment file'
        , required = True
    )
    parser.add_argument('--rr'
        , help = 'Output RR file (CASP format)'
        , required = True
    )
    parser.add_argument('--png'
        , help = 'Output PNG graph'
        , required = False
    )
    args = parser.parse_args()
    arguments = args.__dict__
    main(arguments['aln'], arguments['rr'], arguments['png'])
