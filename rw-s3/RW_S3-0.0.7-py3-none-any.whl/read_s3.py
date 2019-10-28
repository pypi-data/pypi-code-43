import pandas as pd
import boto3
from boto3.session import Session
import re
import json
import pickle
import warnings


class read_s3(object):
    """s3のファイルやpathリストを取得するクラス

    Args:
        s3_profile (str): s3を読み込むための権限を持ったprofile

    """

    def __init__(self, s3_profile):
        warnings.warn("read_s3クラスは非推奨です(今後のupdateなし)\nS3_Readerクラスを用いてください")
        session = Session(profile_name=s3_profile)  # s3にアクセスするためのプロファイルを指定
        self.__s3 = session.client('s3')

    def ls(self, bucket: str, path: str = ""):
        """bucket内のpathリストを取得

        Args:
            bucket (str): バケット名
            path (str): バケット内のオブジェクトのpath

        """
        return self.__get_all_keys(bucket, path)

    def __get_all_keys(self, bucket: str = '', prefix: str = '', keys: list = [], marker: str = '') -> [str]:
        """指定した prefix のすべての key の配列を返す
        """
        response = self.__s3.list_objects(
            Bucket=bucket, Prefix=prefix, Marker=marker)
        if 'Contents' in response:  # 該当する key がないと response に 'Contents' が含まれない
            keys.extend([content['Key'] for content in response['Contents']])
            if 'IsTruncated' in response:
                return self.__get_all_keys(bucket=bucket, prefix=prefix, keys=keys, marker=keys[-1])
        return keys

    def read_file(self, bucket: str, path: str, encoding="utf_8") -> str:
        """拡張子を問わずファイルを読み込む

        Args:
            bucket (str): バケット名
            path (str): バケット内のオブジェクトのpath

        """
        read_file = self.__s3.get_object(Bucket=bucket, Key=path)
        f = read_file["Body"].read().decode(encoding)
        return f

    def read_json_file(self, bucket: str, path: str, encoding="utf_8") -> dict:
        """jsonファイルをdictとして読み込む

        Args:
            bucket (str): バケット名
            path (str): バケット内のオブジェクトのpath

        """
        f = self.read_file(bucket, path, encoding)
        return json.loads(f)
        

    def read_pickle_file(self, bucket: str, path: str):
        """pickleのファイルを読み込む

        Args:
            bucket (str): バケット名
            path (str): バケット内のオブジェクトのpath

        """
        read_file = self.__s3.get_object(Bucket=bucket, Key=path)
        f = pickle.loads(read_file['Body'].read())
        return f

    def read_csv(self, bucket: str, path: str, encoding="utf_8", sep=',', header=0, index_col=None, usecols=None, na_values=None, nrows=None, skiprows=0):
        """csvの読み込み(pandasのread_csvとほぼ同じ)

        Args:
            bucket (str): バケット名
            path (str): バケット内のオブジェクトのpath

        """
        read_file = self.__s3.get_object(Bucket=bucket, Key=path)
        df = pd.read_csv(read_file['Body'], encoding=encoding, sep=sep, header=header,
                         index_col=index_col, usecols=usecols, na_values=na_values, nrows=nrows, skiprows=skiprows)
        return df

    def read_excel(self, bucket: str, path: str, encoding="utf_8", sheet_name=0, header=0, index_col=None, usecols=None, na_values=None, nrows=None, skiprows=0):
        """excelの読み込み(pandasのread_excelとほぼ同じ)

        Args:
            bucket (str): バケット名
            path (str): バケット内のオブジェクトのpath

        """
        read_file = self.__s3.get_object(Bucket=bucket, Key=path)
        df = pd.read_excel(read_file['Body'], encoding=encoding, sheet_name=sheet_name,
                           header=header, index_col=index_col, usecols=usecols, na_values=na_values, nrows=nrows, skiprows=skiprows)
        return df

    def read_table(self, bucket: str, path: str, encoding="utf_8", sep="\t", header=0, index_col=None, usecols=None, na_values=None, nrows=None):
        """csv, tsv, excel等の読み込み(pandasのread_tableとほぼ同じ)

        Args:
            bucket (str): バケット名
            path (str): バケット内のオブジェクトのpath

        Note:
            pandasではread_tableは非推奨扱いです
            read_csv(sep='\t')を用いてください

        """
        read_file = self.__s3.get_object(Bucket=bucket, Key=path)
        df = pd.read_table(read_file['Body'], encoding=encoding, header=header, sep=sep,
                           index_col=index_col, usecols=usecols, na_values=na_values, nrows=nrows)
        return df


if __name__ == '__main__':
    s3 = read_s3("read_s3")
    print(s3.ls("estiepro"))
