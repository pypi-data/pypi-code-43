import json
import logging
import pandas as pd
from .preprocessor import PreProcessor
from .smalltalks import SmallTalks

class MessageCleaner:
    
    def __init__(self, data: pd.core.frame.DataFrame, content_column: str, config_file_path: str):
        self.data = data
        self.preprocessor = PreProcessor()
        self.small_talks = SmallTalks()
        self.__content_column = content_column
        self.__set_config_information(config_file_path)
        self.__set_output_information()
        self.__set_filter_information()
        self.__set_logging_level()
        self.__use_placeholder = self.__config_information.get('use_placeholder', False)
        
    @classmethod
    def from_dataframe(cls, config_file_path: str, dataframe: pd.core.frame.DataFrame, content_column : str, read_all: bool = True):
        if read_all == False:
            dataframe = pd.DataFrame(dataframe[content_column])
        return cls(dataframe, content_column, config_file_path)
    
    @classmethod
    def from_series(cls, config_file_path: str, series: pd.core.frame.Series):
        dataframe = pd.DataFrame(series)
        dataframe.columns = ['Content']
        return cls(dataframe, 'Content', config_file_path)
    
    @classmethod
    def from_list(cls, config_file_path: str, lst: list):
        dataframe = pd.DataFrame(lst)
        dataframe.columns = ['Content']
        return cls(dataframe, 'Content', config_file_path)
        
    @classmethod
    def from_file(cls, config_file_path: str, file_path : str, content_column : str, encoding: str = 'utf-8', sep: str = ';', read_all: bool = True):
        dataframe = pd.read_csv(file_path, sep = sep, encoding = encoding)
        #from_dataframe(cls, config_file_path, dataframe, content_column, read_all)
        if read_all == False:
            dataframe = pd.DataFrame(dataframe[content_column])
        return cls(dataframe, content_column, config_file_path)
    
    def clean(self, output_file_path: str = None):
        self.processed_df = self.data.copy()
        self.processed_df['Processed Content'] = self.data[self.__content_column].copy()
        logging.info('Pre processing {} messages'.format(self.data.shape[0]))
        self.__remove_unimportant_data()
        if self.__column_name is not None:
            self.__filter_column()
        self.preprocessor.set_data(self.processed_df['Processed Content'])
        self.processed_df['Processed Content'] = self.preprocessor.remove(self.__config_information, self.__use_placeholder)
        self.small_talks.set_data(self.processed_df['Processed Content'])
        result = self.small_talks.remove(self.__config_information, self.__use_placeholder)
        if result is not None:
            self.processed_df['Processed Content'] = result
        logging.info('Finished pre processing')
        self.__save_file(output_file_path)
        return self.processed_df
    
    def __set_config_information(self, config_file):
        try:
            with open(config_file, 'r') as f:
                self.__config_information = json.load(f)
        except:
            logging.error('Error reading json configuration file')
    
    def __set_logging_level(self):
        if self.__config_information.get('verbose', False):
            logging.basicConfig(level=logging.INFO)
        else:
            logging.basicConfig(level=logging.WARNING)
            
    def __set_filter_information(self):
        try:
            filters = self.__config_information['filters']
            self.__column_name = filters['column_name']
            if self.__column_name not in self.data:
                raise AttributeError
            self.__contional_value = filters['conditional_value']
            if (filters['remove_if_operation'] != 'different') and (filters['remove_if_operation'] != 'equal'):
                raise KeyError
            else:
                self.__remove_if_operation = filters['remove_if_operation']
        except (KeyError, AttributeError):
            self.__column_name = None
            logging.warning('Missing or invalid filters fields. Filter operation won\'t be executed')
            
    def __set_output_information(self):
        try:
            output_file = self.__config_information['output']
        except (KeyError, AttributeError):
            self.__output_file_name = 'output_processed_content.csv'
            self.__output_file_encoding = 'utf-8'
            self.__output_file_sep = ';'
            self.__remove_duplicates = False
            self.__remove_empty = False
            self.__sort_by_length = False
            logging.warning('Missing output_file field. Setting default values to output variables.')
        else:
            self.__output_file_name = output_file.get('file_name', 'output_processed_content.csv')
            self.__output_file_encoding = output_file.get('file_encoding', 'utf-8')
            self.__output_file_sep = output_file.get('file_sep', ';')
            self.__remove_duplicates = output_file.get('remove_duplicates', False)
            self.__remove_empty = output_file.get('remove_empty', False)
            self.__sort_by_length = output_file.get('sort_by_length', False)
                   
    def __save_file(self, output_file_path: str = None):
        self.__remove_unimportant_data()
        if self.__sort_by_length:
            self.processed_df['Length'] = self.processed_df['Processed Content'].str.len()
            self.processed_df = self.processed_df.sort_values(by=['Length']).reset_index(drop=True)
            self.processed_df.drop(['Length'], axis=1, inplace = True)
        if output_file_path:
            self.processed_df.to_csv(output_file_path, sep= self.__output_file_sep , encoding= self.__output_file_encoding ,index= False)
        else:
            self.processed_df.to_csv(self.__output_file_name, sep= self.__output_file_sep , encoding= self.__output_file_encoding ,index= False)
    
    def __filter_column(self):
        if self.__remove_if_operation == 'different':
            self.processed_df = self.processed_df[self.processed_df[self.__column_name] == self.__contional_value].reset_index(drop=True)
        else:
            self.processed_df = self.processed_df[self.processed_df[self.__column_name] != self.__contional_value].reset_index(drop=True)
    
    def __remove_unimportant_data(self):
        if self.__remove_empty:
            self.processed_df = self.processed_df.dropna(subset = ['Processed Content']).reset_index(drop=True)
        if self.__remove_duplicates:
            self.processed_df = self.processed_df.drop_duplicates(subset= ['Processed Content'], keep= 'first', inplace = False).reset_index(drop=True)