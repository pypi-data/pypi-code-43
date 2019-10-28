import pandas as pd
import boto3
from boto3.session import Session
import re
import json
import pickle


class S3Reader(object):
    '''s3のファイルやpathリストを取得するクラス

    Args:
        s3_profile (str): s3を読み込むための権限を持ったprofile

    Examples:
        >>> s3_reader = S3Reader('hogehoge')
        >>> print(s3_reader.ls('hoge-bucket', 'hoge/'))

    '''

    def __init__(self, s3_profile=None):
        session = Session(profile_name=s3_profile)  # s3にアクセスするためのプロファイルを指定
        self.__s3 = session.client('s3')

    def ls(self, bucket: str, path: str = ''):
        '''bucket内のpathリストを取得

        Args:
            bucket (str): バケット名
            path (str): バケット内のオブジェクトのpath

        '''
        return self.__get_all_keys(bucket, path)

    def __get_all_keys(self, bucket: str = '', prefix: str = '', keys: list = None, marker: str = '') -> [str]:
        '''指定した prefix のすべての key の配列を返す
        '''
        response = self.__s3.list_objects(
            Bucket=bucket, Prefix=prefix, Marker=marker)
        
        #keyがNoneのときは初期化
        if keys is None:
            keys = []
            
        if 'Contents' in response:  # 該当する key がないと response に 'Contents' が含まれない
            keys.extend([content['Key'] for content in response['Contents']])
            if 'IsTruncated' in response:
                return self.__get_all_keys(bucket=bucket, prefix=prefix, keys=keys, marker=keys[-1])
        return keys

    def read_file(self, bucket: str, path: str, encoding='utf_8') -> str:
        '''拡張子を問わずファイルを読み込む

        Args:
            bucket (str): バケット名
            path (str): バケット内のオブジェクトのpath

        '''
        read_file = self.__s3.get_object(Bucket=bucket, Key=path)
        f = read_file['Body'].read().decode(encoding)
        return f

    def read_json_file(self, bucket: str, path: str, encoding='utf_8') -> dict:
        '''jsonファイルをdictとして読み込む

        Args:
            bucket (str): バケット名
            path (str): バケット内のオブジェクトのpath

        '''
        f = self.read_file(bucket, path, encoding)
        return json.loads(f)

    def read_pickle_file(self, bucket: str, path: str):
        '''pickleのファイルを読み込む

        Args:
            bucket (str): バケット名
            path (str): バケット内のオブジェクトのpath

        '''
        read_file = self.__s3.get_object(Bucket=bucket, Key=path)
        f = pickle.loads(read_file['Body'].read())
        return f

    def read_csv(self, bucket: str, path: str, encoding='utf_8', sep=',', header=0, index_col=None, usecols=None, na_values=None, nrows=None, skiprows=0):
        '''csvの読み込み(pandasのread_csvとほぼ同じ)

        Args:
            bucket (str): バケット名
            path (str): バケット内のオブジェクトのpath

        '''
        read_file = self.__s3.get_object(Bucket=bucket, Key=path)
        df = pd.read_csv(read_file['Body'], encoding=encoding, sep=sep, header=header,
                         index_col=index_col, usecols=usecols, na_values=na_values, nrows=nrows, skiprows=skiprows)
        return df

    def read_excel(self, bucket: str, path: str, encoding='utf_8', sheet_name=0, header=0, index_col=None, usecols=None, na_values=None, nrows=None, skiprows=0):
        '''excelの読み込み(pandasのread_excelとほぼ同じ)

        Args:
            bucket (str): バケット名
            path (str): バケット内のオブジェクトのpath

        '''
        read_file = self.__s3.get_object(Bucket=bucket, Key=path)
        df = pd.read_excel(read_file['Body'], encoding=encoding, sheet_name=sheet_name,
                           header=header, index_col=index_col, usecols=usecols, na_values=na_values, nrows=nrows, skiprows=skiprows)
        return df

    def read_table(self, bucket: str, path: str, encoding='utf_8', sep='\t', header=0, index_col=None, usecols=None, na_values=None, nrows=None):
        '''csv, tsv, excel等の読み込み(pandasのread_tableとほぼ同じ)

        Args:
            bucket (str): バケット名
            path (str): バケット内のオブジェクトのpath

        Note:
            pandasではread_tableは非推奨扱いです
            read_csv(sep='\t')を用いてください

        '''
        read_file = self.__s3.get_object(Bucket=bucket, Key=path)
        df = pd.read_table(read_file['Body'], encoding=encoding, header=header, sep=sep,
                           index_col=index_col, usecols=usecols, na_values=na_values, nrows=nrows)
        return df
