from __future__ import print_function
from collections import OrderedDict

import raven_preprocess.col_info_constants as col_const

SOURCE_TYPE_FILE = 'File'

class DataSourceInfo(object):

    def __init__(self, name, source_type, **kwargs):
        """Set data source"""
        self.name = name
        self.source_type = source_type

        self.source_format = kwargs.get('source_format')
        self.filesize = kwargs.get('filesize')

    def as_dict(self):
        """Return DataSourceInfo as an OrderedDict()"""
        data = OrderedDict()
        data[col_const.DATA_SOURCE_NAME] = self.name
        data[col_const.DATA_SOURCE_TYPE] = self.source_type

        # may be None in final output
        data[col_const.DATA_SOURCE_FORMAT] = self.source_format

        # optional
        if self.filesize:
            data[col_const.DATA_SOURCE_FILESIZE] = self.filesize

        return data
