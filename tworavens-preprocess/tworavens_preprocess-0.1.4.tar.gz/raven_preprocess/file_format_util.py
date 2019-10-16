import os

import pandas as pd
from os.path import basename, isfile, splitext

from raven_preprocess.data_source_info import DataSourceInfo, SOURCE_TYPE_FILE
from raven_preprocess.msg_util import msg, msgt
from raven_preprocess.file_format_constants import \
    (CSV_FILE_EXT, TAB_FILE_EXT,
     XLS_FILE_EXT, XLSX_FILE_EXT,
     ACCEPTABLE_EXT_LIST,
     get_mime_type)


class FileFormatUtil(object):
    def __init__(self, input_file, **kwargs):
        """Identify file type: csv, tab, etc"""

        self.input_file = input_file

        self.job_id = kwargs.get('job_id')

        self.dataframe = None
        self.data_source_info = None

        self.file_basename = None
        self.fname_ext_check = None

        #
        self.has_error = False
        self.error_message = None

        self.check_basic_file_info()
        self.load_dataframe()

    def add_error(self, err):
        self.has_error = True
        self.error_message = err

    def check_basic_file_info(self):
        """split the filename"""
        if self.has_error:
            return

        # Is the file specified?
        #
        if not self.input_file:
            self.add_error('The "input_file" was %s' % self.input_file)
            return

        # Does the file exist?
        #
        if isinstance(self.input_file, str):
            # "self.input_file" is file path
            if not isfile(self.input_file):
                self.add_error('The file was not found: [%s]' % self.input_file)
                return

            self.filesize = os.stat(self.input_file).st_size
            # print('filesize ', self.filesize)
            self.file_basename = basename(self.input_file)
            # print('file basename ', self.file_basename)

        else:
            # "self.input_file" is Django FileField
            self.filesize = self.input_file.size
            # print('filesize ', self.filesize)
            self.file_basename = basename(self.input_file.name)
            # print('file basename ', self.file_basename)

        if self.filesize == 0:
            self.add_error('The file size is zero: [%s]' % self.input_file)
            return

        # file basename with extension
        #

        # file extension
        #
        _fname_base, fname_ext = splitext(self.file_basename)

        if fname_ext:
            self.fname_ext_check = fname_ext.lower()
        else:
            self.add_error(\
                ('The "input_file" did not have an extension: %s') % \
                self.input_file)
            return


        # Is this a known/accepted extension
        #
        if self.fname_ext_check not in ACCEPTABLE_EXT_LIST:
            self.add_error(self.get_unaccepted_file_err())
            return

        # Set the mimetype based on the extension
        #
        source_format = get_mime_type(self.fname_ext_check)

        # Create the informational DataSourceInfo object
        #
        self.data_source_info = DataSourceInfo(name=self.file_basename,
                                               source_type=SOURCE_TYPE_FILE,
                                               source_format=source_format,
                                               filesize=self.filesize)


    def load_dataframe(self):
        """Load the file to a dataframe"""
        if self.has_error:
            return

        if self.fname_ext_check == TAB_FILE_EXT:
            self.set_dataframe('\t')

        elif self.fname_ext_check == CSV_FILE_EXT:
            self.set_dataframe()

        elif self.fname_ext_check == XLS_FILE_EXT:
            self.set_dataframe(is_excel=True)

        elif self.fname_ext_check == XLSX_FILE_EXT:
            self.set_dataframe(is_excel=True)

        else:
            self.add_error(self.get_unaccepted_file_err())


    def get_unaccepted_file_err(self):
        """Error message used multiple times"""
        name_for_err = self.input_file
        if self.file_basename:
            name_for_err = self.file_basename

        return ('We currently do not process this file type.'
                ' Please use a file with one of the following'
                ' extensions: %s'
                '\nFile name: %s') % \
                (ACCEPTABLE_EXT_LIST, name_for_err)


    def set_dataframe(self, delimiter=None, is_excel=False):
        """Retrieve a pandas dataframe based on format"""
        try:
            if is_excel:
                self.dataframe = pd.read_excel(self.input_file)
            else:
                self.dataframe = pd.read_csv(self.input_file,
                                             delimiter=delimiter)

        except pd.errors.ParserError as err_obj:
            err_msg = ('Failed to load csv file (pandas ParserError).'
                       '\n- File: %s'
                       '\n- %s') % \
                      (self.input_file, err_obj)
            self.add_error(err_msg)

        except PermissionError as err_obj:
            err_msg = ('No read prermission on this file:'
                       '\n- File: %s'
                       '\n- %s') % \
                      (self.input_file, err_obj)
            self.add_error(err_msg)

        except Exception as err_obj:
            err_msg = ('Failed to load file.'
                       '\n- File: %s'
                       '\n- %s') % \
                      (self.input_file, err_obj)
            self.add_error(err_msg)
