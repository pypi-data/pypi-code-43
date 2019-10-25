#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 20 12:00:00 2019

COTOHA API for Python3.8
@author: Nicolas Toba Nozomi
@id: 278mt
"""

import requests
import json
from cotohappy.reshape import Reshape
from cotohappy.error import CotohapPyError


class API(object):

    def __init__(
        self,
        access_token_publish_url: str=None,
        api_base_url            : str=None,
        client_id               : str=None,
        client_secret           : str=None,
        payload_fname           : str='payload.json'
    ):

        """
        Parameters
        ----------
        access_token_publish_url : str
            Access Token Publish URL. Specify Access Token Publish URL on the account page (default: None)
        api_base_url             : str
            API Base URL. Specify your API Base URL on the account page (default: None)
        client_id                : str
            Client ID. Specify your client id shown on the account page (default: None)
        client_secret            : str
            Client secret. Specify your client secret on the account page (default: None)
        payload_fname            : str
            payload json filename (default: 'payload.json')

        Notes
        -----
        You can choose using saved payload file, or writing 4 keys: "Access Token Publish URL", "API Base URL", "Client ID" and "Client secret".
        If you typo your key, you cannot connect to online API Cotoha.

        Examples
        --------
        >>> import cotohappy
        >>> coy = cotohappy()   # created instance of cotohappy
        """

        if None in [access_token_publish_url, api_base_url, client_id, client_secret]:

            with open(payload_fname, mode='r') as file:
                self.payload = json.load(file)

                for key in ['AccessTokenPublishURL', 'APIBaseURL', 'ClientId', 'ClientSecret']:
                    if key not in self.payload:
                        raise CotohapPyError('{} file has no attribute {}'.format(payload_fname, key))

        else:
            self.payload = {
                'AccessTokenPublishURL': access_token_publish_url,
                'APIBaseURL'           : api_base_url,
                'ClientId'             : client_id,
                'ClientSecret'         : client_secret
            }

        self.__get_access_token()
        self.api_base_url = self.payload['APIBaseURL']


    def __beta(fn):

        def inr_fn(self, *arg, **kwarg):

            print('This API is provided in Beta Version.')

            return fn(self, *arg, **kwarg)

        return inr_fn


    def __enterprise(fn):

        def inr_fn(self, *arg, **kwarg):

            print('This API is for Enterprise. Please note that this API is not available for developer accounts.')

            return fn(self, *arg, **kwarg)

        return inr_fn


    def __get_access_token(self):

        url = self.payload['AccessTokenPublishURL']
        headers = {'Content-Type': 'application/json'}
        data = json.dumps({
            'grantType'   : 'client_credentials',
            'clientId'    : self.payload['ClientId'],
            'clientSecret': self.payload['ClientSecret']
        })

        with requests.post(url, headers=headers, data=data) as req:
            if req.status_code != 201:
                raise CotohapPyError('Connection failure. Please check your payload to access COTOHA.')

            response = req.json()

        self.access_token = response['access_token']

        self.expires_in = int(response['expires_in'])
        self.issued_at = int(response['issued_at'])


    def __attributed_type(self, type_: str='default') -> str:

        if type_ not in ['default', 'kuzure']:
            raise CotohapPyError(f'type_ must be "default" or "kuzure", not "{type_}"')

        return type_


    def __get_result(self, partial_url: str, body: dict) -> dict:

        url = self.api_base_url + partial_url
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'Authorization': f'Bearer {self.access_token}'
        }
        data = json.dumps(body)

        with requests.post(url, headers=headers, data=data) as req:
            response = req.json()

            if response['status'] > 0:
                raise CotohapPyError(response['message'])

        return response['result']


    @__enterprise
    def __attributed_dic_type(self, dic_type: str or [str]) -> [str]:

        if type(dic_type) is str:
            dic_type = [dic_type]

        correct_dic_type = [
            'IT',
            'automobile',
            'chemistry',
            'company',
            'construction',
            'economy',
            'energy',
            'institution',
            'machinery',
            'medical',
            'metal'
        ]

        for part in dic_type:
            if part not in correct_dic_type:
                raise CotohapPyError(f'dic_type {part} is unusable. Please choose from {correct_dic_type}')

        return dic_type


    def parse(self, sentence: str, type_: str='default', dic_type: str or [str]=None) -> [Reshape]:

        """
        Parameters
        ----------
        sentence : str
            sentence to be analyzed
        type_    : str
            You can choose one from the following (default: 'default')
            * 'default' - normal sentence
            * 'kuzure'  - Sentence contains 'word lengthening' often found in SNSs
        dic_type : str or [str]
            Specify technical term dictionaries. Choose from ther below.(only for Enterprise user) That's too bad. I'm an university student. I want for academic.
            * 'IT'           - Computer,information,communication
            * 'automobile'   - Automobile
            * 'chemistry'    - Chemical and Petroleum Industries
            * 'company'      - Company Name
            * 'construction' - Civil engineering and construction
            * 'economy'      - Economy and laws and regulations
            * 'energy'       - Electric power and energy
            * 'institution'  - Organizations
            * 'machinery'    - Machinery
            * 'medical'      - Medical
            * 'metal'        - Metal

        See Also
        --------
        Reshape (reshape.py)

        Notes
        -----
        Parsing API receives the sentence written in Japanese as an input, parse and output its sentence structure. The input sentence is broken down into clause and morpheme, semantic relationship between clauses, dependency relationship between morphemes, and semantic information such as parts of speech information, etc.
        You may think it is more difficult declaration than MeCab or Janome, but a strong point is to get chunks of string.

        Examples
        --------
        >>> import cotohappy
        >>> coy = cotohappy()
        >>> sentence = '犬は歩く。'
        >>> type_    = 'default'
        >>> parse_li = coy.parse(sentence, type_)
        >>> for parse in parse_li:
        ...     parse
        ...     # form   id,head,dep,chunk_head,chunk_func
        犬は     0,1,D,0,1
        歩く。   1,-1,O,0,1
        >>> for parse in parse_li:
        ...     for token in parse.tokens:
        ...         token
        ...         # form   id,kana,lemma,pos,features[:5]
        犬   0,イヌ,犬,名詞,*,*,*,*,*
        は   1,ハ,は,連用助詞,*,*,*,*,*
        歩   2,アル,歩く,動詞語幹,K,*,*,*,*
        く   3,ク,く,動詞接尾辞,終止,*,*,*,*
        。   4,,。,句点,*,*,*,*,*
        """

        partial_url = 'nlp/v1/parse'
        body = {
            'sentence': sentence,
            'type'    : self.__attributed_type(type_),
        }
        if dic_type is not None:
            body['dic_type'] = self.__attributed_dic_type(dic_type)

        parse_li = self.__get_result(partial_url, body)

        return [
            Reshape('parse', parse)
            for parse in parse_li
        ]


    def ne(self, sentence: str, type_: str='default', dic_type: str or [str]=None) -> [Reshape]:

        """
        Parameters
        ----------
        sentence : str
            Sentence to be analyzed
        type_    : str
            You can choose one from the following (default: 'default')
            * 'default' - Normal sentence
            * 'kuzure'  - sentence contains word lengthening often found in SNSs
        dic_type : str or [str]
            Specify technical term dictionaries. Choose from ther below.(only for Enterprise user) That's too bad. I'm an university student. I want for academic.
            * 'IT'           - Computer,information,communication
            * 'automobile'   - Automobile
            * 'chemistry'    - Chemical and Petroleum Industries
            * 'company'      - Company Name
            * 'construction' - Civil engineering and construction
            * 'economy'      - Economy and laws and regulations
            * 'energy'       - Electric power and energy
            * 'institution'  - Organizations
            * 'machinery'    - Machinery
            * 'medical'      - Medical
            * 'metal'        - Metal

        See Also
        --------
        Reshape (reshape.py)

        Notes
        -----
        Named entity extraction API receives sentence written in Japanese as an input, analyzes, and outputs 8 types of named entity (the names of people, places, time expressions (time, date), the names of organization, quantitative expressions (amount of money, ratio) , artifacts), and extended named entity with more than 200 classes.

        Examples
        --------
        >>> import cotohappy
        >>> coy = cotohappy()
        >>> sentence = '昨日は東京駅を利用した。'
        >>> type_    = 'default'
        >>> ne_li = coy.ne(sentence, type_)
        >>> for ne in ne_li:
        ...     ne
        ...     # form   begin_pos,end_pos,std_form,class,extended_class,info,source
        昨日   0,2,昨日,DAT,*,*,basic
        東京駅 3,6,東京駅,LOC,*,*,basic
        """

        partial_url = 'nlp/v1/ne'
        body = {
            'sentence': sentence,
            'type_'    : self.__attributed_type(type_)
        }
        if dic_type is not None:
            body['dic_type'] = self.__attributed_dic_type(dic_type)

        ne_li = self.__get_result(partial_url, body)

        return [
            Reshape('ne', ne)
            for ne in ne_li
        ]


    def coreference(self, document: str or [str], type_: str='default', do_segment: bool=False) -> Reshape:

        """
        Parameters
        ----------
        document   : str or [str]
            You can choose one from the following
            * str   - sentence to be analyzed
            * [str] - sentences to be analyzed
        type_      : str
            You can choose one from the following (default: 'default')
            * 'default' - normal sentence
            * 'kuzure'  - sentence contains word lengthening often found in SNSs
        do_segment : bool
            You can choose whether to segment the sentences (default: False)
            * True  - if the type of 'document' is 'string', the document will be segmented.
            * False - the document will not be segmented. #if the type of 'document' is 'array (string)', do_segment will be ignored.

        See Also
        --------
        Reshape (reshape.py)

        Notes
        -----
        Receive multiple sentences written in Japanese as an input, extract pronouns such as "そこ", "それ","彼", "彼女", extract an antecedent that correspond to those pronouns, and outputs them as a pair of pronoun and object.

        Examples
        --------
        >>> import cotohappy
        >>> coy = cotohappy()
        >>> document   = '太郎は友人です。彼は焼き肉を食べた。'
        >>> type_      = 'default'
        >>> do_segment = True
        >>> coreference = coy.coreference(document, type_, do_segment)
        >>> for content in coreference.coreference:
        ...     content
        ...     # representative_id
        >>> for content in coreference.coreference:
        ...     for referent in content.referents:
        ...         referent
        ...         # form   referent_id,sentence_id,token_id_from,token_id_to
        太郎     0,0,0,0
        彼   1,1,0,0
        """

        partial_url = 'nlp/v1/coreference'
        body = {
            'document'  : document,
            'type_'      : self.__attributed_type(type_),
            'do_segment': do_segment
        }

        return Reshape('coreference', self.__get_result(partial_url, body))


    def keyword(self, document: str or [str], type_: str, do_segment: bool=False, max_keyword_num: int=5, dic_type: str or [str]=None) -> [Reshape]:

        """
        Parameters
        ----------
        document        : str or [str]
            You can choose one from the following
            * str   - sentence to be analyzed
            * [str] - sentences to be analyzed
        type_           : str
            You can choose one from the following (default: 'default')
            * 'default' - normal sentence
            * 'kuzure' - sentence contains word lengthening often found in SNSs
        do_segment      : bool
            You can choose whether to segment the sentences (default: False)
            * True  - if the type of 'document' is 'string', the document will be segmented.
            * False - the document will not be segmented. #if the type of 'document' is 'array (string)', do_segment will be ignored.
        max_keyword_num : int
            Maximum number of extracted keywords (default: 5)
        dic_type        : str or [str]
            Specify technical term dictionaries. Choose from ther below.(only for Enterprise user) That's too bad. I'm an university student. I want for academic.
            * 'IT'           - Computer,information,communication
            * 'automobile'   - Automobile
            * 'chemistry'    - Chemical and Petroleum Industries
            * 'company'      - Company Name
            * 'construction' - Civil engineering and construction
            * 'economy'      - Economy and laws and regulations
            * 'energy'       - Electric power and energy
            * 'institution'  - Organizations
            * 'machinery'    - Machinery
            * 'medical'      - Medical
            * 'metal'        - Metal

        See Also
        --------
        Reshape (reshape.py)

        Notes
        -----
        Keyword extraction API receives multiple sentences written in Japanese as an input, and extracts characteristic phrases and words contained in input sentence as a keywords. Multiple phrases and words are output in decending order based on the characteristic score measured from the text.

        Examples
        --------
        >>> import cotohappy
        >>> coy = cotohappy()
        >>> document        = 'レストランで昼食を食べた。'
        >>> type_           = 'default'
        >>> do_segment      = True
        >>> max_keyword_num = 2
        >>> keyword_li = coy.keyword(document, type_, do_segment, max_keyword_num)
        >>> for keyword in keyword_li:
        ...     keyword
        ...     # form   score
        昼食     12.1121
        レストラン   9.42937
        """

        partial_url = 'nlp/v1/keyword'
        body = {
            'document'       : document,
            'type'           : self.__attributed_type(type_),
            'do_segment'     : do_segment,
            'max_keyword_num': max_keyword_num
        }
        if dic_type is not None:
            body['dic_type'] = self.__attributed_dic_type(dic_type)

        keyword_li = self.__get_result(partial_url, body)

        return [
            Reshape('keyword', keyword)
            for keyword in keyword_li
        ]


    def similarity(self, s1: str, s2: str, type_: str, dic_type: str or [str]=None) -> Reshape:

        """
        Parameters
        ----------
        s1       : str
            Sentence to be calculated for similarity
        s2       : str
            Sentence to be calculated for similarity
        type_    : str
            You can choose one from the following (default: 'default')
            * 'default' - default sentence
            * 'kuzure'  - sentence contains word lengthening often found in SNSs
        dic_type : str or [str]
            Specify technical term dictionaries. Choose from ther below.(only for Enterprise user) That's too bad. I'm an university student. I want for academic.
            * 'IT'           - Computer,information,communication
            * 'automobile'   - Automobile
            * 'chemistry'    - Chemical and Petroleum Industries
            * 'company'      - Company Name
            * 'construction' - Civil engineering and construction
            * 'economy'      - Economy and laws and regulations
            * 'energy'       - Electric power and energy
            * 'institution'  - Organizations
            * 'machinery'    - Machinery
            * 'medical'      - Medical
            * 'metal'        - Metal

        See Also
        --------
        Reshape (reshape.py)

        Notes
        -----
        Similarity calculation receives two sentences written in Japanese as input, calculates and outputs semantic similarity between sentences. The degree of similarity is defined from 0 to 1, indicating that the closer to 1, the greater similarity betwen the texts.
        Since the similarity is calculated using semantic information of words contained in sentences, we can also estimate the similarity between the sentences containing different words.

        Examples
        --------
        >>> import cotohappy
        >>> coy = cotohappy()
        >>> s1     = '近くのレストランはどこですか？'
        >>> s2     = 'このあたりの定食屋はどこにありますか？'
        >>> type_  = 'default'
        >>> similarity = coy.similarity(s1, s2, type_)
        >>> similarity  # score
        0.88565135
        """

        partial_url = 'nlp/v1/similarity'
        body = {
            's1'  : s1,
            's2'  : s2,
            'type': self.__attributed_type(type_)
        }
        if dic_type is not None:
            body['dic_type'] = self.__attributed_dic_type(dic_type)

        return Reshape('similarity', self.__get_result(partial_url, body))


    def sentence_type(self, sentence: str, type_: str) -> Reshape:

        """
        Parameters
        ----------
        sentence : str
            Sentence to be analyzed
        type_    : str
            You can choose one from the following (default: 'default')
            * 'default' - default sentence
            * 'kuzure'  - sentence includs word lengthening often found in SNSs


        See Also
        --------
        Reshape (reshape.py)

        Notes
        -----
        Sentence type classification API receives a sentence written in Japanese as an input, identifies and outputs the Modality types (descriptions/questions/commands) and dialog act types.

        Examples
        --------
        >>> import cotohappy
        >>> coy = cotohappy()
        >>> sentence = 'あなたの名前は何ですか？'
        >>> type_    = 'default'
        >>> coy.sentence_type(sentence, type_)  # modality   dialog_act[:5]'
        interrogative    information-seeking,*,*,*,*
        """

        partial_url = 'nlp/v1/sentence_type'
        body = {
            'sentence': sentence,
            'type'    : self.__attributed_type(type_)
        }

        return Reshape('sentence_type', self.__get_result(partial_url, body))


    def sentiment(self, sentence: str) -> Reshape:

        """
        Parameters
        ----------
        sentence : str
            Sentence to be analyzed

        See Also
        --------
        Reshape (reshape.py)

        Notes
        -----
        Sentiment Analysis is text classification tool that analyses an incoming message and determine whether the underlying sentiment is positive or negative. Sentiment Analysis API can also recognize types of more than 50 different feelings such as joy, surprise, fear, pleasure etc. within the sentences.

        Examples
        --------
        >>> import cotohappy
        >>> coy = cotohappy()
        >>> sentence = '人生の春を謳歌しています'
        >>> sentiment = coy.sentiment(sentence)
        >>> sentiment   # sentiment,score
        Positive,0.19562121911742972
        >>> for emotional_phrase in sentiment.emotional_phrase:
        ...     emotional_phrase
        ...     # form   emotion[:5]
        謳歌     喜ぶ,安心,*,*,*
        """

        partial_url = 'nlp/v1/sentiment'
        body = {
            'sentence': sentence
        }

        return Reshape('sentiment', self.__get_result(partial_url, body))


    @__beta
    def user_attribute(self, document: str or [str], type_: str='default', do_segment: bool=False) -> Reshape:

        """
        Parameters
        ----------
        document   : str, [str]
            You can choose from the following
            * str   - sentence to be analyzed
            * [str] - sentences to be analyzed
        type_      : str
            You can choose one from the following (default: 'default')
            * 'default' - default sentence
            * 'kuzure'  - sentence contains word lengthening often found in SNSs
        do_segment : bool
            You can choose whether to segment the sentences (default: False)
            * True  - if the type of 'document' is 'string', the document will be segmented.
            * False - the document will not be segmented. #if the type of 'document' is 'array (string)', do_segment will be ignored.

        See Also
        --------
        Reshape (reshape.py)

        Notes
        -----
        User attribute estimation API receives sentence written in Japanese as an input, estimates and outputs the attributes of people such as age, gender, hobby, occupation, etc.
        This API is provided in Beta Version.

        Examples
        --------
        >>> import cotohappy
        >>> coy = cotohappy()
        >>> document = '私は昨日田町駅で飲みに行ったら奥さんに怒られた。'
        >>> type_    = 'default'
        >>> coy.user_attribute(document, type_) # age,civilstatus,earnings,gender,kind_of_bussiness,kind_of_occupation,location,position,habit[:2],hobby[:5],moving[:5]
        60歳以上,既婚,*,*,*,*,*,*,*,*,*,ANIMAL,CAMERA,COOKING,FISHING,FORTUNE,*,*
        """

        partial_url = 'nlp/beta/user_attribute'
        body = {
            'document'  : document,
            'type'      : type_,
            'do_segment': do_segment
        }

        return Reshape('user_attribute', self.__get_result(partial_url, body))


    @__beta
    def remove_filler(self, text: str, do_segment: bool=False) -> [Reshape]:

        """
        Parameters
        ----------
        text : str
            Text to be analyzed
        do_segment : bool
            Specify whether to delimit or not to delimit the sentence.
            Specify true when analyzing text that does not include punctuation marks. (default: False) 
            * True  – delimit the sentence
            * False - not delimit the sentence

        See Also
        --------
        Reshape (reshape.py)

        Notes
        -----
        Filler Removal API receives the text after speech recognition process, specify the fillers such as 「えーと」, 「あのー」, outputs the information and text without fillers. Also, it normalizes the wrong expressions which caused by long vowel and sound disruption, and outputs the normalized text strings.
        This API is provided in Beta Version.

        Examples
        --------
        >>> import cotohappy
        >>> coy = cotohappy()
        >>> text       = 'えーーっと、あの、今日の打ち合わせでしたっけ。すみません、ちょっと、急用が入ってしまって。'
        >>> do_segment = True
        >>> remove_filler_li = coy.remove_filler(text, do_segment)
        >>> for remove_filler in remove_filler_li:
        ...     remove_filler
        ...     # normalized_sentence    fixed_sentence
        えーっと、あの、今日の打ち合わせでしたっけ。     、今日の打ち合わせでしたっけ。
        すみません、ちょっと、急用が入ってしまって。     すみません、急用が入ってしまって。
        """

        partial_url = 'nlp/beta/remove_filler'
        body = {
            'text'      : text,
            'do_segment': do_segment
        }

        remove_filler_li = self.__get_result(partial_url, body)
        return [
            Reshape('remove_filler', remove_filler)
            for remove_filler in remove_filler_li
        ]


    @__beta
    def detect_misrecognition(self, sentence: str) -> Reshape:

        """
        Parameters
        ----------
        sentence : str
            Text to be analyzed

        See Also
        --------
        Reshape (reshape.py)

        Notes
        -----
        Error detection on speech recognition result API receives the text after speech recognition process, outputs the suspected recognition error and the score at the same time. It also shows the error degree from the entire input sentences in numbers and outputs them.
        This API is provided in Beta Version.

        Examples
        --------
        >>> import cotohappy
        >>> coy = cotohappy()
        >>> sentence = '温泉認識は誤りを起こす'
        >>> detect_misrecognition = coy.detect_misrecognition(sentence)
        >>> for candidate in detect_misrecognition.candidates:
        ...     candidate
        ...     # form   begin_pos,end_pos,detect_score,correct_score[:5]
        温泉     0,2,0.9999968696704667,音声,厭戦,怨念,おんねん,モンセン
        """

        partial_url = 'nlp/beta/detect_misrecognition'
        body = {
            'sentence': sentence
        }

        return Reshape('detect_misrecognition', self.__get_result(partial_url, body))

