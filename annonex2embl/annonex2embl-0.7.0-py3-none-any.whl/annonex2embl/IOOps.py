#!/usr/bin/env python
'''
Custom operations input and output processes
'''

#####################
# IMPORT OPERATIONS #
#####################

import os
import datetime

from csv import DictReader
from Bio.Nexus import Nexus
from Bio import SeqIO

try:
    from StringIO import StringIO ## for Python 2
except ImportError:
    from io import StringIO ## for Python 3

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

###########
# CLASSES #
###########

class Inp:
    ''' This class contains functions to conduct miscellaneous input
        operations.
    Args:
        [specific to function]
    Returns:
        [specific to function]
    Raises:
        -
    '''

    def __init__(self):
        pass

    def extract_fn(self, in_path):
        ''' This function splits a the path from path+filename. '''
        path, fn = os.path.split(in_path)
        return fn

    def repl_fileend(self, fn, new_end):
        ''' This function replaces the file ending (e.g. ".csv") with a
        different ending. '''
        return fn[:fn.rfind('.')] + '.' + new_end


    def parse_csv_file(self, path_to_csv):
        ''' This function parses a csv file. '''
        try:
            reader = DictReader(open(path_to_csv, 'r'), delimiter=',',
                                quotechar='"', skipinitialspace=True)
            a_matrix = list(reader)
        except Exception as e:
            msg = 'ERROR: %s:\n %s' % ('Parsing of '
            '.csv-file unsuccessful', e)
            warnings.warn(msg)
            raise Exception
        return a_matrix

    def parse_nexus_file(self, path_to_nex):
        ''' This function parses a NEXUS file. '''
        try:
            aln = Nexus.Nexus()
            aln.read(path_to_nex)
            charsets = aln.charsets
            matrix = aln.matrix
        except Nexus.NexusError as e:
            print(e)
            raise
        except Exception as e:
            msg = 'ERROR: %s:\n %s' % ('Parsing of '
            '.nex-file unsuccessful', e)
            warnings.warn(msg)
            raise Exception
        return (charsets, matrix)


class Outp:
    ''' This class contains two functions for various output operations.
    Args:
        [specific to function]
    Returns:
        [specific to function]
    Raises:
        -
    '''

    def __init__(self):
        pass

    def write_SeqRecord(self, seq_name, seq_record, author_names, outp_handle, ENAstrict_bool):
        ''' This function writes a seqRecord in EMBL format.
            Upon request (ENAstrict_bool), it masks the ID and AC
            lines as requested by ENA for submissions.
        Args:
            seq_name (str)
            seq_record (obj)
            author_names (str)
            outp_handle (obj)
            ENAstrict_bool(bool)
        Returns:
            currently nothing
        Raises:
            -
        '''

        date_today = datetime.date.today().strftime("%d-%b-%Y").upper()
        SecRecord_handle = StringIO()
        try:
            SeqIO.write(seq_record, SecRecord_handle, 'embl')
        except Exception as e:
            msg = 'ERROR: %s: %s. Did not write to '
            'internal handle.\n %s' % ('Problem with sequence ', seq_name, e)
            warnings.warn(msg)
            raise Exception

        if ENAstrict_bool:
            SecRecord_handle_lines = SecRecord_handle.getvalue().splitlines()
            if SecRecord_handle_lines[0].split()[0] == 'ID':
                ID_line = SecRecord_handle_lines[0]
                ID_line_parts = ID_line.split('; ')
                if len(ID_line_parts) == 7:
                    ID_line_parts = ['XXX' if ID_line_parts.index(p) in
                                     [0, 1, 3, 4, 5, 6] else p for p in ID_line_parts]
                SecRecord_handle_lines[0] = 'ID   ' + '; '.join(ID_line_parts)
            if SecRecord_handle_lines[2].split()[0] == 'AC':
                SecRecord_handle_lines[2] = 'AC   XXX;'
            SecRecord_handle_new = '\n' + '\n'.join(SecRecord_handle_lines)
            SecRecord_handle.truncate(0)
            SecRecord_handle.write(SecRecord_handle_new)
        else:
            pass

        for line in SecRecord_handle.getvalue().split("\n"):
            if line[0:8] == 'FH   Key':
                outp_handle.write("RN   [1]" +
                          "\nRA   " + author_names.replace('"','') +
                          "\nRT   ;" +
                          "\nRL   Submitted (" + date_today + ") to the INSDC." +
                          "\nXX" +
                          "\n")
            outp_handle.write(line)
            if line[0:2] != '//':
                outp_handle.write("\n")
        SecRecord_handle.close()


    def create_manifest(self, path_to_outfile, manifest_study, manifest_name, manifest_flatfile):
        ''' This function writes a manifest file. '''

        manifest_fn = ''.join(path_to_outfile.split('.')[:-1]) + '.manifest'
        with open(manifest_fn, "w") as manifest:
            manifest.write(("STUDY\t %s\n") % (manifest_study))
            manifest.write(("NAME\t %s\n") % (manifest_name))
            manifest.write(("FLATFILE\t %s\n") % (manifest_flatfile))
