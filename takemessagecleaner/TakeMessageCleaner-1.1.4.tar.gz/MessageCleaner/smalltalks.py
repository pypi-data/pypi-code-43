import logging
import numpy as np
import pandas as pd
from time import time
from requests import post

class SmallTalks:
    
    def set_data(self, data: pd.core.frame.Series):
        self.data = data
        
    def remove(self, config_file: str, use_placeholder: bool):
        self.__set_small_talks_information(config_file)
        if self.__small_talks and self.__endpoint is not None:
            logging.info('Small talks processing {} messages'.format(self.data.shape[0]))
            responses = self.__smalltalk_requests()
            processed_content = []
            for response in responses:
                processed_content.extend(self.__converting_response_from_api(response.json(), use_placeholder, self.__relevant))
            return pd.Series(processed_content)
        
    def __set_small_talks_information(self, config_file: str):
        try:
            small_talks_api = config_file['small_talks_api']
            self.__small_talks = small_talks_api.get('small_talks', False)
            self.__endpoint = small_talks_api.get('endpoint')
            self.__number_of_batches = small_talks_api.get('number_of_batches', 4)
            self.__relevant = small_talks_api.get('relevant', False)
        except (KeyError, AttributeError):
            small_talks_api = {'small_talks': False, 'endpoint': None}
            logging.warning('Missing small_talks_api field. Setting default values small talks.')
    
    def __get_json(self , data):
        items_list = []
        for message in data['Processed Content']:  
            obj = {}
            obj['configuration'] = {
                'unicodeNormalization': True,
                'toLower': False,
                'informationLevel': 3
            }
            obj['text'] = message
            obj['dateCheck'] = False
            items_list.append(obj)        
        return items_list
    
    def __smalltalk_requests(self):
        number_of_batches = self.__get_batch_size(self.data.shape[0])
        data_splitted = np.array_split(self.data, number_of_batches)
    
        json_lst = []
        for idx, dataframe in enumerate(data_splitted):
            dataframe = dataframe.reset_index()
            items_list = self.__get_json(dataframe)
    
            begin = time()
            obj = {'id': str(idx), 'items': items_list}
            
            r = post(self.__endpoint, json=obj)
            
            if r.ok:
                json_lst.append(r)
            else:
                logging.error('Small talks error')
                r.raise_for_status()
    
            end = time()
            logging.info('Small Talks process finished! Time elapsed = ' + str((end - begin)) +' seconds')
        return json_lst
    
    def __get_batch_size(self, length):
        if length < self.__number_of_batches:
            batch = int(length / 100 + 1)
            logging.warning('Invalid number of batches. Setting number of batches to {}'.format(batch))
        else:
            batch = self.__number_of_batches
        return batch
    
    def __converting_response_from_api(self, response, use_tagging, relevant):
        
        if use_tagging == True: cleaned_type = 'markedInput'
        elif relevant == True: cleaned_type = 'relevantInput'
        else: cleaned_type = 'cleanedInput'
        
        if cleaned_type == 'markedInput':
            cleaned_output = self.__insert_placeholder(response, cleaned_type)
        else:
            cleaned_output = [message['analysis'][cleaned_type] if message['analysis']['matchesCount'] > 0 else message['analysis']['input'] for message in response['items']]
        return cleaned_output
    
    def __insert_placeholder(self, response, cleaned_type: str):
        cleaned_output = []
        for message in response['items']:   
            matches = message['analysis']['matches']
            if len(matches) > 0:
                sorted_matches = sorted(matches, key=lambda dct: dct['index'])
                MarkedInput = message['analysis'][cleaned_type]
                size_diff = 0
                st_type_length = 0
                for match in sorted_matches:
                    st_length = match['length']
                    index = match['index'] + size_diff
                    
                    begin_string = MarkedInput[:index]
                    end_string = MarkedInput[index + st_length:]
                    MarkedInput = begin_string + match['smallTalk'].upper() + end_string
                    st_type_length = len(match['smallTalk'])
                    size_diff +=  st_type_length - st_length
                cleaned_output.append(MarkedInput)
            else:
                cleaned_output.append(message['analysis']['input'])
        return cleaned_output