#!/usr/bin/env python2.7
'''
Command-line execution of annonex2embl
'''

#####################
# IMPORT OPERATIONS #
#####################

import sys
import os

# Add specific directory to sys.path in order to import its modules
# NOTE: THIS RELATIVE IMPORTING IS AMATEURISH.
# NOTE: COULD THE FOLLOWING IMPORT BE REPLACED WITH 'import annonex2embl'?
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'annonex2embl'))

# IMPORTANT: TFL must be after "sys.path.append"
import Annonex2emblMain
import argparse

###############
# AUTHOR INFO #
###############

__author__ = 'Michael Gruenstaeudl <m.gruenstaeudl@fu-berlin.de>'
__copyright__ = 'Copyright (C) 2016-2019 Michael Gruenstaeudl'
__info__ = 'annonex2embl'
__version__ = '2019.10.16.1700'

#############
# DEBUGGING #
#############

#import ipdb
#ipdb.set_trace()

############
# ARGPARSE #
############

class CLI():

    def __init__(self):
        self.client()

    def client(self):

        parser = argparse.ArgumentParser(description="  --  ".join([__author__, __copyright__, __info__, __version__]))

        ### REQUIRED ###
        parser.add_argument('-n',
                            '--nexus',
                            help='absolute path to infile; infile in NEXUS format; Example: /path_to_input/test.nex',
                            default='/home/username/Desktop/test.nex',
                            required=True)

        parser.add_argument('-c',
                            '--csv',
                            help='absolute path to infile; infile in CSV format; Example: /path_to_input/test.csv',
                            default='/home/username/Desktop/test.csv',
                            required=True)

        parser.add_argument('-d',
                            '--descr',
                            help='text string characterizing the multiple sequence alignment contained in the NEXUS file; Example: "chloroplast trnR-atpA intergenic spacer"',
                            default='a_description_here',
                            required=True)

        parser.add_argument('-e',
                            '--email',
                            help='email address of submitter; Example: "your_email_here@yourmailserver.com"',
                            default='your_email_here@yourmailserver.com',
                            required=True)

        parser.add_argument('-a',
                            '--authors',
                            help='Author names; Example: "LastName1 A.; LastName2 B."',
                            default='LastName1 A.; LastName2 B.',
                            required=True)

        parser.add_argument('-o',
                            '--outfile',
                            help='absolute path to outfile; outfile in EMBL format; Example: /path_to_output/test.embl',
                            default='/home/username/Desktop/test.embl',
                            required=True)

        ### OPTIONAL ###
        parser.add_argument('--manifeststudy',
                            help='the study accession number for the manifest file that the submission shall be linked to; Example: PRJEB00000',
                            default='',
                            required=False)

        parser.add_argument('--manifestdescr',
                            help='a unique, non-interrupted text string for the manifest file characterizing the input alignment; Example: a_unique_description_here',
                            default='',
                            required=False)

        parser.add_argument('--productlookup',
                            help='a logical; shall gene products be looked up via NCBI and their names added to the output flatfile?',
                            default='False',
                            required=False)

        parser.add_argument('--taxonomycheck',
                            help='a logical; shall scientific taxon names be confirmed via the ENA taxonomy service?',
                            default='False',
                            required=False)

        parser.add_argument('--linemask',
                            help='a logical; shall the ID and the AC lines of the output flatfile be masked?',
                            default='False',
                            required=False)

        parser.add_argument('--seqtopol',
                            help='topology of the input sequences; available options: circular or linear',
                            default='linear',
                            required=False)

        parser.add_argument('--taxdivision',
                            help='any of the three letter codes indicating the taxonomic division of the sequences; '\
                            'for details, see: section 3.2 of the EMBL user manual',
                            default='PLN',
                            required=False)

        parser.add_argument('--collabel',
                            #metavar='column specifying sequence names',
                            help='name of the metadata (i.e., CSV file) column that specifies the sequence names',
                            default='isolate',
                            required=False)

        parser.add_argument('--transltable',
                            #metavar='translation table',
                            help='ID number of the translation table used for translating coding regions; '\
                            'for details, see: http://www.ncbi.nlm.nih.gov/Taxonomy/Utils/wprintgc.cgi',
                            default='11',
                            required=False)

        parser.add_argument('--organelle',
                            #metavar='translation table',
                            help='type of membrane-bound intracellular structure, if any, from which the sequence was obtained; '\
                            'for details, see: http://www.insdc.org/files/feature_table.html',
                            default='plastid',
                            required=False)

        parser.add_argument('--seqvers',
                            #metavar='sequence version',
                            help='an integer',
                            default='1',
                            required=False)

        parser.add_argument('--compress',
                            #metavar='sequence version',
                            help='a logical; shall the output flatfile be compressed (.gz) upon generation?',
                            default='False',
                            required=False)

        parser.add_argument('--version',
                            help='print version number and exit',
                            action='version',
                            version='%(prog)s ' + __version__)

        args = parser.parse_args()

        Annonex2emblMain.annonex2embl(   args.nexus,
                                         args.csv,
                                         args.descr,
                                         args.email,
                                         args.authors,
                                         args.outfile,

                                         args.manifeststudy,
                                         args.manifestdescr,
                                         args.productlookup,
                                         args.taxonomycheck,
                                         args.linemask,
                                         args.seqtopol,
                                         args.taxdivision,
                                         args.collabel,
                                         args.transltable,
                                         args.organelle,
                                         args.seqvers,
                                         args.compress )

########
# MAIN #
########

def start_annonex2embl():
    CLI()
