import re
import json
import pickle
import pandas as pd
import logging
import boto3
from boto3.session import Session
from botocore.exceptions import ClientError
import warnings


class write_s3():
    """s3にデータをuploadするクラス

    Args:
        s3_profile (str): s3にputするためのprofile

    """

    def __init__(self, s3_profile):
        warnings.warn("write_s3クラスは非推奨です(今後のupdateなし)\nS3_Writerクラスを用いてください")
        session = Session(profile_name=s3_profile)  # s3にアクセスするためのプロファイルを指定
        self.__s3 = session.client('s3')

    def upload_file(self, src_data: str, bucket: str, path: str):
        """

        Args:
            src_data: bytes of data or string reference to file spec
            bucket (str): bucket name
            path (str): path name

        Returns:
            bool
            True if src_data was added to dest_bucket/dest_object, otherwise False

        """
        if isinstance(src_data, bytes):
            object_data = src_data
        elif isinstance(src_data, str):
            try:
                object_data = open(src_data, 'rb')
                # possible FileNotFoundError/IOError exception
            except Exception as e:
                logging.error(e)
                return False
        else:
            logging.error('Type of ' + str(type(src_data)) +
                          ' for the argument \'src_data\' is not supported.')
            return False
        try:
            self.__s3.put_object(Bucket=bucket, Key=path, Body=object_data)
        except ClientError as e:
            # AllAccessDisabled error == bucket not found
            # NoSuchKey or InvalidRequest error == (dest bucket/obj == src bucket/obj)
            logging.error(e)
            return False
        finally:
            if isinstance(src_data, str):
                object_data.close()
        return True

    def upload_object_by_pickle(self, obj, bucket: str, path: str):
        """objectをpickleとしてs3に書き出す

        Args:
            obj (any types): 
            bucket (str): bucket name
            path (str): path name

        """
        self.__s3.put_object(Bucket=bucket, Key=path, Body=pickle.dumps(obj))

    def to_json(self, dic: dict, bucket: str, path: str):
        """dictをjsonファイルとしてs3に書き出す

        Args:
            dic (dict): s3に書き出したい辞書
            bucket (str): bucket name
            path (str): path name

        """
        self.__s3.put_object(Bucket=bucket, Key=path, Body=json.dumps(dic))

    def to_csv(self, df: pd.DataFrame, bucket: str, path: str, index=True, encoding="utf_8"):
        """ s3にデータフレームをcsvとして書き出す

        Args:
            df (pd.DataFrame)
            bucket (str): bucket name
            path (str): path name

        Note:
            存在しないバケットにもアップロードできます

        """
        bytes_to_write = df.to_csv(
            None, index=index, encoding=encoding).encode(encoding)
        self.__s3.put_object(
            ACL='private', Body=bytes_to_write, Bucket=bucket, Key=path)

    def to_excel(self, df: pd.DataFrame, bucket, path, index=True, encoding="utf_8"):
        """s3にデータフレームをexcelとして書き出す

        Args:
            df (pd.DataFrame)
            bucket (str): bucket name
            path (str): path name

        Note:
            存在しないバケットにもアップロードできます

        """
        bytes_to_write = df.to_excel(
            None, index=index, encoding=encoding).encode(encoding)
        self.__s3.put_object(
            ACL='private', Body=bytes_to_write, Bucket=bucket, Key=path)
