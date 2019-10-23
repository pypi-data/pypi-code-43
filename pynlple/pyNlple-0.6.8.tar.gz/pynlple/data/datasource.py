# -*- coding: utf-8 -*-
import io
import json

from pynlple.data.jsonsource import FileJsonDataSource

from pandas import DataFrame
from pandas import read_csv, read_json
from pynlple.data.source import Source

import logging
logger = logging.getLogger(__file__)


class DataframeSource(Source):

    def __init__(self, dataframe):
        self.dataframe = dataframe

    def get_dataframe(self):
        return self.dataframe

    def set_dataframe(self, dataframe):
        self.dataframe = dataframe


class TsvDataframeSource(Source):

    def __init__(self, dataframe_path, separator='\t', quote=0, escape_char='\\', column_names=None, index_column_names=None, fill_na_map=None, encoding='utf-8', index_columns=None):
        self.path = dataframe_path
        self.separator = separator
        self.column_names = column_names
        self.na_map = fill_na_map
        self.encoding = encoding
        self.index_columns = index_columns
        self.index_column_names = index_column_names
        self.quote = quote
        self.escape_char = escape_char

    def get_dataframe(self):
        #TODO: Eats \r\n and spits sole \n in literal value strings instead
        if self.column_names:
            header = None
            names = self.column_names
        else:
            header = 'infer'
            names = None

        dataframe = read_csv(self.path,
                             sep=self.separator,
                             header=header,
                             names=names,
                             quoting=self.quote,
                             escapechar=self.escape_char,
                             encoding=self.encoding)
        if self.index_columns:
            dataframe.set_index(keys=self.index_columns, inplace=True)
        if self.na_map:
            for key, value in self.na_map.items():
                dataframe[key].fillna(value, inplace=True)
        logger.debug('Read: {} rows from {}'.format(str(len(dataframe.index)), self.path))
        return dataframe

    def set_dataframe(self, dataframe):
        if self.column_names:
            names = self.column_names
        else:
            names = True

        if self.index_column_names:
            include_index = True
            index_names = self.index_column_names
        else:
            include_index = False
            index_names = None

        dataframe.to_csv(self.path,
                         sep=self.separator,
                         header=names,
                         index=include_index,
                         index_label=index_names,
                         quoting=self.quote,
                         escapechar=self.escape_char,
                         encoding=self.encoding)
        logger.debug('Written: {} rows from {}'.format(str(len(dataframe.index)), self.path))


class JsonFileDataframeSource(Source):

    FILE_READ_METHOD = 'rt'
    FILE_WRITE_METHOD = 'wt'
    DEFAULT_ORIENT = 'records'
    DEFAULT_ENCODING = 'utf-8'

    def __init__(self, json_file_path, fill_na_map=None, index_columns=None,
                 encoding=DEFAULT_ENCODING, orient=DEFAULT_ORIENT):
        self.json_file_path = json_file_path
        self.na_map = fill_na_map
        self.index_columns = index_columns
        self.encoding = encoding
        self.orient = orient

    def get_dataframe(self):
        with io.open(self.json_file_path, JsonFileDataframeSource.FILE_READ_METHOD, encoding=self.encoding) as data_file:
            #TODO: implement fill_na_map
            df = read_json(data_file, orient=self.orient, encoding=JsonFileDataframeSource.DEFAULT_ENCODING)
        return df

    def set_dataframe(self, dataframe):
        with io.open(self.json_file_path, JsonFileDataframeSource.FILE_WRITE_METHOD, encoding=self.encoding) as data_file:
            #TODO: implement fill_na_map
            json.dump(dataframe.reset_index().to_dict(orient=self.orient), data_file, ensure_ascii=False, indent=1)


class JsonNullableFileDataframeSource(Source):

    DEFAULT_ENCODING = 'utf-8'

    def __init__(self, json_file_path, keys=None, fill_na_map=None, index_columns=None,
                 encoding=DEFAULT_ENCODING):
        self.__source = JsonDataframeSource(FileJsonDataSource(file_path=json_file_path, encoding_str=encoding),
                                            keys=keys, fill_na_map=fill_na_map,
                                            index_columns=index_columns)

    def get_dataframe(self):
        return self.__source.get_dataframe()

    def set_dataframe(self, dataframe):
        self.__source.set_dataframe(dataframe)


class JsonDataframeSource(Source):

    def __init__(self, json_source, keys=None, fill_na_map=None, index_columns=None):
        self.json_source = json_source
        self.keys = keys
        self.na_map = fill_na_map
        self.index_columns = index_columns

    def get_dataframe(self):
        extracted_entries = list()
        for json_object in self.json_source.get_data():
            entry = dict()
            if self.keys:
                for key in self.keys:
                    if key not in json_object:
                        entry[key] = self.na_map[key]
                    else:
                        entry[key] = json_object[key]
            else:
                for key in json_object:
                    entry[key] = json_object[key]
                if self.na_map:
                    for key, value in self.na_map:
                        if key not in entry:
                            entry[key] = value
            extracted_entries.append(entry)
        dataframe = DataFrame(extracted_entries)
        if self.index_columns:
            dataframe.set_index(keys=self.index_columns, inplace=True)
        if self.na_map:
            for key, value in self.na_map.items():
                dataframe.loc[:,key].fillna(value, inplace=True)
        logger.debug('Read: {} rows from {}'.format(str(len(dataframe.index)), repr(self.json_source)))
        return dataframe

    def set_dataframe(self, dataframe):
        entries = dataframe.reset_index().to_dict(orient='records')
        for entry in entries:
            if self.keys:
                for key in list(entry.keys()):
                    if key not in self.keys:
                        entry.pop(key, None)
            if self.na_map:
                for key, value in self.na_map:
                    if key not in entry:
                        entry[key] = value
        self.json_source.set_data(entries)
