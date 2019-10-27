# -*- coding: utf-8 -*-
# s3interface
import boto3
from datetime import datetime
import logging
import os
import queue
import threading
from time import mktime, sleep
import ujson


log = logging.getLogger('coininfo_collector')

from botocore.exceptions import NoCredentialsError

class S3InterfaceBaseClass:
	pass

class S3InterfaceSingleton(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(S3InterfaceSingleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]

class S3Interface(S3InterfaceBaseClass, metaclass=S3InterfaceSingleton):
    def __init__(self):
        self._jobQ = queue.Queue()

    def S3InterfaceInit(
        self,
        ACCESS_KEY = None, 
        SECRET_KEY = None, 
        ):

        self._ACCESS_KEY = ACCESS_KEY
        self._SECRET_KEY = SECRET_KEY

        self._s3 = boto3.client(
            's3',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
        )

        t = threading.Thread(
            target=self._processQueue,
            name='S3Interface',
        )
        t.setDaemon(False)
        t.start()

    
    def _processQueue(self):
        while True:
            try:
                if self._jobQ.empty() is True:
                    sleep(1)
                    continue

                direction = self._jobQ.get()
                jobName = direction['jobName']

                if jobName == 'snapCoin':
                    self._upload_to_aws(
                        # body
                        ujson.dumps(direction['data'], ensure_ascii=False),

                        # bucket name
                        direction['bucketName'],

                        # outfile name
                        '{}/coin-sumarry.json'.format(
                            direction['outputPrefix'], 
                        ),
                    )

            except Exception as inst:
                log.error('failed in S3interface::_processQueue. msg:{}'.format(inst.args))


    def addJob(self, direction):
        self._jobQ.put(direction)

    def _upload_to_aws(self, binary_data, bucket, s3_file):
        self._s3 = boto3.client('s3', aws_access_key_id=self._ACCESS_KEY,
                        aws_secret_access_key=self._SECRET_KEY)

        try:
            self._s3.put_object(
                Body=binary_data,
                Bucket=bucket,
                Key=s3_file,
                ACL='public-read',
            )
            log.debug("s3 upload Successful. file:{}".format(s3_file))
            return True
        except FileNotFoundError:
            log.debug("The file was not found. s3. file:{}".format(s3_file))
            return False
        except NoCredentialsError:
            log.debug("Credentials not available. s3. file:{}".format(s3_file))
            return False
        except Exception as inst:
            log.error('err in upload_to_aws. s3. file:{}. msg:{}'.format(s3_file, inst.args))

        return False

