#!/usr/bin/python3
from olctools.accessoryFunctions.accessoryFunctions import make_path, MetadataObject, SetupLogging
from argparse import ArgumentParser
from glob import glob
import logging
import pandas
import shutil
import time
import os
__author__ = 'adamkoziol'


class Renamer(object):

    def excelparse(self):
        """
        Parses input excel file, and creates objects with headers as keys, and cell data as values for each row
        """
        logging.info('Loading excel file')
        # A dictionary to store the parsed excel file in a more readable format
        nesteddictionary = dict()
        # Use pandas to read in the excel file, and subsequently convert the pandas data frame to a dictionary
        # (.to_dict()). Only read the first fourteen columns (parse_cols=range(14)), as later columns are not
        # relevant to this script
        dictionary = pandas.read_excel(self.file, usecols=range(14)).to_dict()
        # Iterate through the dictionary - each header from the excel file
        for header in dictionary:
            # Sample is the primary key, and value is the value of the cell for that primary key + header combination
            for sample, value in dictionary[header].items():
                # Update the dictionary with the new data
                try:
                    nesteddictionary[sample].update({header: value})
                # Create the nested dictionary if it hasn't been created yet
                except KeyError:
                    nesteddictionary[sample] = dict()
                    nesteddictionary[sample].update({header: value})
        # Create objects for each of the samples, rather than using a nested dictionary. It may have been possible to
        # skip the creation of the nested dictionary, and create the objects from the original dictionary, but there
        # seemed to be too many possible places for something to go wrong
        for line in nesteddictionary:
            # Create an object for each sample
            metadata = MetadataObject()
            # Set the name of the metadata to be the primary key for the sample from the excel file
            metadata.name = line
            # Find the headers and values for every sample
            for header, value in nesteddictionary[line].items():
                # Try/except for value.encode() - some of the value are type int, so they cannot be encoded
                try:
                    # Create each attribute - use the header (in lowercase, and spaces removed) as the attribute name,
                    # and the value as the attribute value
                    setattr(metadata, str(header).replace(' ', '').lower(), str(value))
                except TypeError:
                    setattr(metadata, str(header).replace(' ', '').lower(), value)
            # Append the object to the list of objects
            self.metadata.append(metadata)
        # Run the filer method
        self.filer()

    def filer(self):
        """
        Match the files to the spreadsheet. Rename and copy the files as required.
        """
        logging.info('Renaming files')
        for sample in self.metadata:
            # Use the FTIR id and replicate from the spreadsheet as part of the pattern to match to find the
            # appropriate files e.g. FTIR0018 replicate 3 will match self.spectra_path/FTIR0018-3*
            try:
                sample.originalfile = glob(os.path.join(self.spectra_path,
                                                        ('{id}-{rep}*'.format(id=sample.ftirid,
                                                                              rep=sample.replicate))))[0]
                sample.datetime = os.path.basename(sample.originalfile).split('_')[1]
                # Rename the file using values from the spreadsheet
                if self.classic:
                    # Original File Name: FTIR0182-1_2017-05-26T11-13-47.spc
                    # New File Name:
                    # GN_Klebsiella_BHI_AN_CFIA_FTIR0182_C2_2017_May_26_CA01_OLC0027_2017-05-26T11-13-47.spc
                    sample.renamedfile = '{}'.format('_'.join([sample.gramstain,
                                                               sample.genus,
                                                               sample.species,
                                                               sample.media,
                                                               sample.respiration,
                                                               sample.location,
                                                               sample.ftirid,
                                                               sample.machine,
                                                               sample.yyyy,
                                                               sample.mmm,
                                                               sample.dd,
                                                               '{}{:02d}'.format(sample.user, int(sample.replicate)),
                                                               sample.strainid,
                                                               sample.datetime
                                                               ]))
                else:
                    # Original File Name: FTIR0182-1_2017-05-26T11-13-47.spc
                    # New File Name: Salmonella_Thompson_OLC2596_TSA_FTIR1859_R01.spc
                    sample.renamedfile = '{sn}.spc'\
                        .format(sn='_'.join([sample.genus,
                                             sample.species,
                                             sample.strainid,
                                             sample.media,
                                             sample.ftirid,
                                             'R{:02d}'.format(int(sample.replicate))]))
                # If the species is not provided, remove the 'nan' placeholder used e.g.
                # Enterobacter_nan_OLC3318_TSA_FTIR1943_R01
                # Enterobacter_cloacae_OLC3318_TSA_FTIR1943_R01
                if sample.species == 'nan':
                    sample.renamedfile = sample.renamedfile.replace('nan_', '')
                # The output file will be the the renamed file in the output path
                sample.outputfile = os.path.join(self.outputpath, sample.renamedfile)
                # Do not copy the file if it already exists
                if not os.path.isfile(sample.outputfile):
                    shutil.copyfile(sample.originalfile, sample.outputfile)
            # Print a message warning that certain files specified in the spreadsheet were not found in the file path
            except IndexError:
                logging.warning('Missing file for {sid}'.format(sid=sample.ftirid))

    def __init__(self, spectra_path, filename, start_time, outputpath, classic):
        """
        :param spectra_path: Path to .spc files
        :param filename: Path to .xls(x) file with renaming information.
        :param start_time: Time the analyses started
        :param outputpath: Path to folder in which the renamed files are to be stored
        :param classic: BOOL whether to use the "classic" method of file renaming.
        """
        SetupLogging()
        # Define variables based on supplied arguments
        if spectra_path.startswith('~'):
            self.spectra_path = os.path.abspath(os.path.expanduser(os.path.join(spectra_path)))
        else:
            self.spectra_path = self.file = os.path.abspath(os.path.join(spectra_path))
        assert os.path.isdir(self.spectra_path), 'Supplied sequence path is not a valid directory {0!r:s}'\
            .format(self.spectra_path)
        if filename.startswith('~'):
            self.file = os.path.abspath(os.path.expanduser(os.path.join(filename)))
        else:
            self.file = os.path.abspath(os.path.join(filename))
        # If the path to the file wasn't provided, check the spectra folder
        if not os.path.isfile(self.file):
            self.file = os.path.join(self.spectra_path, filename)
        # If the file still can't be found, check the parental folder of the spectra folder
        if not os.path.isfile(self.file):
            self.file = os.path.join(os.path.dirname(self.spectra_path), filename)
        self.start = start_time
        assert os.path.isfile(self.file), 'Cannot find the supplied Excel file ({0!r:s}) with the file information. ' \
                                          'Please ensure that this file is in the path, and there\'s no spelling ' \
                                          'mistakes'.format(self.file)
        # Set the output path
        self.outputpath = os.path.join(outputpath)
        # Create the output path as required
        make_path(self.outputpath)
        # Determine the naming scheme
        self.classic = classic
        # Create class variable
        self.metadata = list()


if __name__ == '__main__':
    # Parser for arguments
    parser = ArgumentParser(description='Rename files for FTIR experiments using strict naming scheme')
    parser.add_argument('-s', '--spectra_path',
                        required=True,
                        help='Path of .spc files')
    parser.add_argument('-f', '--filename',
                        required=True,
                        help='Absolute path to .xls(x) file with renaming information. Must conform to required format '
                             '(see README for additional information)')
    parser.add_argument('-o', '--outputpath',
                        required=True,
                        help='Specify the folder in which the renamed files are to be stored. Provide the '
                             'full path e.g. /path/to/output/files')
    parser.add_argument('-c', '--classic',
                        action='store_true',
                        help='Use the "classic" method of file renaming. '
                             'Original File Name: FTIR0182-1_2017-05-26T11-13-47.spc, renamed file: '
                             'GN_Klebsiella_BHI_AN_CFIA_FTIR0182_C2_2017_May_26_CA01_OLC0027_2017-05-26T11-13-47.spc')
    # Get the arguments into an object
    arguments = parser.parse_args()
    # Define the start time
    start = time.time()

    # Run the script
    renamer = Renamer(spectra_path=arguments.spectra_path,
                      filename=arguments.filename,
                      start_time=start,
                      outputpath=arguments.outputpath,
                      classic=arguments.classic)
    renamer.excelparse()

    # Print a bold, blue exit statement
    logging.info('Analyses complete!')
