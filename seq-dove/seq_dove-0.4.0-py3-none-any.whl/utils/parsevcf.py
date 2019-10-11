# -*- coding: utf-8 -*-
__author__ = 'bars'

from collections import defaultdict
import pandas as pd
import gzip
import sys


class ParseVcf():
    '''
    Main class for parsing vcf and its columns like sample format and variant info.
    '''

    def __init__(self, vcfpath, compression='infer', chunksize=None):
        self.vcfpath = vcfpath
        self.compression = compression
        # Chunksize not used right now.
        self.chunksize = chunksize
        # Generic VCF header without samplenames.
        # Mainly used for getting the samplenames.
        self.generic_header = ['CHROM',
                               'POS',
                               'ID',
                               'REF',
                               'ALT',
                               'QUAL',
                               'FILTER',
                               'INFO',
                               'FORMAT']
        self.get_header_n_comments()
        self.read_vcf()

    def __repr__(self):
        '''Samplenames and number of variants'''
        return '{} {}'.format(' '.join(self.samplenames), len(self.vdf))

    def __len__(self):
        '''Number of variants'''
        return len(self.vdf)

    @property
    def samplenames(self):
        '''Samplenames is header - generic_header'''
        return [colname for colname in self.header if colname not in self.generic_header]

    @property
    def vdf(self):
        '''These functions for setting vdf attribute.'''
        return self.variant_df

    @vdf.setter
    def vdf(self, new_df):
        '''These functions for setting vdf attribute.'''
        self.variant_df = new_df

    def get_header_n_comments(self):
        '''Get comments and header from vcf file.
           This function returns a dictionary.'''
        # Open file
        if self.vcfpath.endswith('.vcf.gz'):
            with gzip.open(self.vcfpath, 'rb') as f:
                lines = f.readlines()
            # If gzip already pass as an argument pass
            # else set it to gzip
            if self.compression != 'infer':
                pass
            else:
                self.compression = 'gzip'
        elif self.vcfpath.endswith('.vcf'):
            with open(self.vcfpath, 'r') as f:
                lines = f.readlines()
        else:
            sys.stderr.write('Are you sure this is a vcf file??')
            sys.exit()
        # comments dict
        comments = defaultdict(list)
        # Loop over lines
        for line in lines:
            if self.compression == 'gzip':
                line = line.decode('utf-8')
            # When it reaches the header break
            if '#CHROM' in line:
                self.header = [colname for colname in line.strip('#').replace(
                    '\n', '').split('\t')]
                break
            # Remove the pound and new line.  Split by equal sign.
            k, v = line.strip('#').replace('\n', '').split('=', 1)
            # add it to dictionary
            comments[k].append(v)
        self.comments = comments

    def read_vcf(self):
        '''Reads the table. vdf stands for Variant Data Frame.
        comment='#' passes meta info and header.
        header is parsed from the file with header() function
        low_memory=False reads columns as object
        compression for gzip vcf files.
        chunksize pass'''
        self.variant_df = pd.read_table(self.vcfpath,
                                        comment='#',
                                        names=self.header,
                                        low_memory=False,
                                        compression=self.compression)
        # chunks WIP
        # if self.chunksize is not None:
        #     for vdf_chunk in pd.read_table(self.vcfpath,
        #                                    comment='#',
        #                                    names=self.header,
        #                                    low_memory=False,
        #                                    compression=compression,
        #                                    chunksize=self.chunksize):
        #         yield vdf_chunk

    def get_variant_info(self, concat=False, drop=False):
        # Create key set from all rows
        all_key_set = set()
        for info_row in self.vdf['INFO']:
            # This line checks if the row is empty.
            # Fix for test vcf 'string_as_flag.vcf'
            if info_row == info_row:
                for variant_info in info_row.split(';'):
                    all_key_set.add(variant_info.split('=')[0])

        # Create info_dict that will be use to create info_df
        variant_info_dict = defaultdict(list)
        for index, info_row in zip(self.vdf.index, self.vdf['INFO']):
            variant_info_dict['index'].append(index)

            # If row is empty add NA to all keys and continue with the loop.
            if not info_row == info_row:
                for key in all_key_set:
                    variant_info_dict[key].append('NA')
                continue

            # If row is not empty collect its keys to another set.
            row_key_set = set()
            for variant_info in info_row.split(';'):
                row_key_set.add(variant_info.split('=')[0])

            # Add NA to missing keys.
            for key in all_key_set - row_key_set:
                variant_info_dict[key].append('NA')

            # Add values to dict
            for variant_info in info_row.split(';'):
                try:
                    row_key, v = variant_info.split('=')
                # If Its only a flag just add 1. E.g. ;NegativeTrainError;
                except ValueError:
                    row_key = variant_info.split('=')[0]
                    v = 1
                variant_info_dict[row_key].append(v)

        variant_info_df = pd.DataFrame.from_dict(variant_info_dict)
        variant_info_df.set_index('index', inplace=True)

        if concat == True:
            new_df = pd.concat([self.vdf, variant_info_df], axis=1)
            if drop == True:
                new_df.drop('INFO', axis=1, inplace=True)
            return new_df
        else:
            return variant_info_df

    def get_sample_format(self, samplenames=None, concat=False, drop=False):
        # If sample names is None self.samplenames is used.
        if samplenames is None:
            samplenames = self.samplenames
        else:
            samplenames = samplenames

        samples_df_dict = {}
        for sample in samplenames:

            all_key_set = set()
            for format_row in self.vdf['FORMAT']:
                if format_row == format_row:
                    for sample_format in format_row.split(':'):
                        all_key_set.add(sample_format)

            sample_format_dict = defaultdict(list)
            for index, format_row, sample_row in zip(self.vdf.index, self.vdf['FORMAT'], self.vdf[sample]):
                sample_format_dict['index'].append(index)

                row_key_set = set()
                for sample_format in format_row.split(':'):
                    row_key_set.add(sample_format)

                for key in all_key_set - row_key_set:
                    sample_format_dict[key].append('NA')

                # Whole sample row missing. Fix for test vcf "strelka.vcf"
                if not sample_row == sample_row:
                    sample_row = 'NA'

                # Sample missing format. Fix for test vcf "example-4.1.vcf"
                while len(format_row.split(':')) > len(sample_row.split(':')):
                    sample_row += ':NA'

                for sample_format, sample_info in zip(format_row.split(':'), sample_row.split(':')):
                    sample_format_dict[sample_format].append(sample_info)

            sample_format_df = pd.DataFrame.from_dict(sample_format_dict)
            sample_format_df.set_index('index', inplace=True)
            samples_df_dict[sample] = sample_format_df

        if concat == True:
            for sample in samples_df_dict.keys():
                samples_df_dict[sample] = pd.concat(
                    [self.vdf, samples_df_dict[sample]], axis=1)

            if drop == True:
                if len(samples_df_dict) == 1:
                    samples_df_dict[samplenames[0]] = samples_df_dict[sample].drop(
                        samplenames[0], axis=1)
                else:
                    for sample in samplenames:
                        samples_df_dict[sample] = samples_df_dict[sample].drop(
                            samplenames, axis=1)

            if len(samples_df_dict) == 1:
                return samples_df_dict[list(samples_df_dict.keys())[0]]
            else:
                return samples_df_dict
        else:
            if len(samples_df_dict) == 1:
                return samples_df_dict[list(samples_df_dict.keys())[0]]
            else:
                return samples_df_dict
