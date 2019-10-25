import os
import re
import json
import emoji
import string
import unidecode
import functools
import pandas as pd

class PreProcessor:
    
    def __init__(self):
        self.__compile_regex()
        self.__set_pt_dictionary()
        self.__set_associate_dic()
    
    def set_data(self, data: pd.core.frame.Series):
        self.data = data.astype(str)
    
    def remove(self, config_information: dict, use_placeholder: bool):
        self.__set_processing_dict(config_information)
        
        if use_placeholder == True:
            for key, value in self.enabled_processing_dict.items():
                 self.data = map(self.enabled_processing_dict[key], self.data)
        else:
            for key, value in self.enabled_processing_dict.items():
                self.data = list(map(functools.partial(self.enabled_processing_dict[key], tag_name = ''), self.data))
        return pd.Series(self.data)
    
    def to_lower(self, message: str, tag_name = ''):
        return message.lower()
    
    def remove_whatsapp_emoji(self, message: str, tag_name = 'WA_EMOJI'):
        new_message = [word if word not in emoji.EMOJI_UNICODE.values() else tag_name for word in message]
        return ''.join(new_message)
            
    def remove_emoji(self, message: str, tag_name = 'EMOJI'):
        return self.EMOJI_REGEX.sub(tag_name, message)    
    
    def remove_accentuation(self, message: str, tag_name = ''):
        return unidecode.unidecode(message)
    
    def remove_space(self, message: str, tag_name = ''):
        return self.SPACE_REGEX.sub(tag_name, message)
    
    def remove_punctuation(self, message: str, tag_name = ''):
        return self.PUNCTUATION_REGEX.sub(tag_name, message)
    
    def remove_number(self, message: str, tag_name = 'NUMBER'):
        return self.NUMBER_REGEX.sub(tag_name, message)
    
    def remove_code(self, message: str, tag_name = 'CODE'):
        return self.CODE_REGEX.sub(tag_name, message)

    def remove_date(self, message: str, tag_name = 'DATE'):
        return self.DATE_REGEX.sub(tag_name, message)

    def remove_cpf(self, message: str, tag_name = 'CPF'):
        return self.CPF_REGEX.sub(tag_name, message)

    def remove_time(self, message: str, tag_name = 'TIME'):
        return self.TIME_REGEX.sub(tag_name, message)
  
    def remove_email(self, message: str, tag_name = 'EMAIL'):
        return self.EMAIL_REGEX.sub(tag_name, message)

    def remove_money(self, message: str, tag_name = 'MONEY'):
        return self.MONEY_REGEX.sub(tag_name, message)

    def remove_url(self, message: str, tag_name = 'URL'):
        return self.URL_REGEX.sub(tag_name, message)
    
    def correct_spelling(self, message: str, tag_name = ''):
        correct_message = [self.__pt_dict[word] if word in self.__pt_dict.keys() else word for word in message.split()] 
        return ' '.join(correct_message)
    
    def __compile_regex(self):
        self.SPACE_REGEX = re.compile(r'\s\s+')
        self.PUNCTUATION_REGEX = re.compile('[{}]'.format(string.punctuation))
        self.NUMBER_REGEX = re.compile(r'[-+]?\d*\.\d+|\d+')
        self.CODE_REGEX = re.compile(r'[A-Za-z]+\d+\w*|[\d@]+[A-Za-z]+[\w@]*')
        self.DATE_REGEX = re.compile(r'(\d{1,2}[/-//]\d{1,2})([/-//]\d{2,4})?')
        self.CPF_REGEX = re.compile(r'\d{3}\.\d{3}\.\d{3}-\d{2}')
        self.TIME_REGEX = re.compile(r'\d{1,2}(:|h(rs)?)(\d{1,2}(min)?)?')
        self.EMAIL_REGEX = re.compile(r'[^\s]+@[^\s]+')
        self.MONEY_REGEX = re.compile(r'(R[S$])\d+(\.\d{3})*(,\d{2})?')
        self.URL_REGEX = re.compile(r'(http|https)://[^\s]+')
        self.EMOJI_REGEX = re.compile('['
                                    u'\U0001f600-\U0001f64f'  # emoticons
                                    u'\U0001f300-\U0001f5ff'  # symbols & pictographs
                                    u'\U0001f680-\U0001f6ff'  # transport & map symbols
                                    u'\U0001f1e0-\U0001f1ff'  # flags (iOS)
                                                       ']+', flags=re.UNICODE)
    def __set_pt_dictionary(self):
        dir_path = os.path.dirname(__file__)
        full_path_error = os.path.join(dir_path, 'dictionaries', 'portuguese_errors.json')
        full_path_abbreviation = os.path.join(dir_path, 'dictionaries', 'abbreviations.json')
        self.__pt_dict = self.__read_dictionary(full_path_error)
        self.__pt_dict.update(self.__read_dictionary(full_path_abbreviation))

    def __read_dictionary(self, file_name: str):
        with open(file_name, 'r', encoding = 'utf-8') as handle:
            return json.loads(handle.read())
    
    def __set_associate_dic(self):
        self.__associate_dic = {
                          'wa_emoji': self.remove_whatsapp_emoji,
                          'emoji': self.remove_emoji,
                          'lower': self.to_lower,
                          'cpf': self.remove_cpf,
                          'time': self.remove_time,
                          'date': self.remove_date,
                          'email': self.remove_email,
                          'money': self.remove_money,
                          'url': self.remove_url,
                          'code': self.remove_code,
                          'number': self.remove_number,
                          'accentuation': self.remove_accentuation,
                          'space': self.remove_space,
                          'punctuation': self.remove_punctuation,
                          'spelling': self.correct_spelling
                         }
        
    def __set_processing_dict(self, config_information: dict):
        try:
            processing = config_information['processing']
        except KeyError:
            print('Configuration file missing processing field.')
            raise KeyError
        else:
            wa_emoji = processing.get('wa_emoji', False)
            emoji = processing.get('emoji', False)
            lower = processing.get('lower', False)
            spelling = processing.get('spelling', False)
            cpf = processing.get('cpf', False)
            time = processing.get('time', False)
            date = processing.get('date', False)
            email = processing.get('email', False)
            money = processing.get('money', False)
            url = processing.get('url', False)
            code = processing.get('code', False)
            number = processing.get('number', False)
            accentuation = processing.get('accentuation', False)
            stop_words = processing.get('stop_words', False)
            punctuation = processing.get('punctuation', False)
        
        processing_lst = [
                ('wa_emoji', wa_emoji),
                ('emoji', emoji),
                ('lower', lower),
                ('spelling', spelling),
                ('cpf', cpf),
                ('time', time),
                ('date', date),
                ('email', email),
                ('money', money),
                ('url', url),
                ('code', code),
                ('number', number),
                ('accentuation', accentuation),
                ('stop_words', stop_words),
                ('punctuation', punctuation)
                ]
        
        enabled_processing_lst = [tupl[0] for tupl in processing_lst if tupl[1] == True] 
        self.enabled_processing_dict = {processing: self.__associate_dic[processing] for processing in self.__associate_dic if processing in enabled_processing_lst}