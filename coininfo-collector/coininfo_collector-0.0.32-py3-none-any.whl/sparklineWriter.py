# -*- coding: utf-8 -*-
# 코인 가격 변동 그래프(sparkline)를 coingecko 홈페이지에서 크롤링해서 s3 버킷에 저장합니다.)
import boto3
from bs4 import BeautifulSoup
import logging
import os
from os.path import dirname, realpath
from selenium import webdriver
import threading
from time import sleep

log = logging.getLogger('coininfo_collector')

from botocore.exceptions import NoCredentialsError

SparklineInitPageURL = 'https://www.coingecko.com/en'

class SparklineWriterBaseClass:
	pass

class SparklineWriterSingleton(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(SparklineWriterSingleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]

class SparklineWriter(SparklineWriterBaseClass, metaclass=SparklineWriterSingleton):
    def __init__(self):
        self._createdInstance = False

    def initSparklineWriter(
        self,
        ACCESS_KEY = None, 
        SECRET_KEY = None, 
        webdriverPath = None,
        sparklineS3BucketName = None,
        sparklineOutputPrefix = None,
        ):

        self._ACCESS_KEY = ACCESS_KEY
        self._SECRET_KEY = SECRET_KEY

        self._s3 = boto3.client(
            's3',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
        )

        self._lockList = threading.Lock()
        self._jobList = list()

        # 
        self._webDriverPath = webdriverPath

        if self._webDriverPath:
            self._initChromeDriver()

        self._sparklineS3BucketName = sparklineS3BucketName
        self._sparklineOutputPrefix = sparklineOutputPrefix

        t = threading.Thread(
            target=self._processQueue,
            name='s3_sparkline',
        )
        t.setDaemon(False)
        t.start()

        self._createdInstance = True


    def _initChromeDriver(self):
        log.info('init ChromeDriver...')

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('no-sandbox')
        options.add_argument('disable-dev-shm-usage')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
        options.add_argument("lang=ko_KR")
        self._driver = webdriver.Chrome(self._webDriverPath, chrome_options=options)
        log.debug('chrome driver loading... ')
        self._driver.implicitly_wait(5)

        # set timeout => 60 sec
        self._driver.set_page_load_timeout(60)

        self._execute_script_imitating_people()

        self._driver.get(SparklineInitPageURL)

        log.debug('selenium loading completed. url:{}'.format(SparklineInitPageURL))

        log.debug('wait 15 seconds for firewall(coingecko)...')
        sleep(15)


    def _execute_script_imitating_people(self):
        self._driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5]}})")
        self._driver.execute_script("Object.defineProperty(navigator, 'languages', {get: function() {return ['ko-KR', 'ko']}})")
        self._driver.execute_script("const getParameter = WebGLRenderingContext.getParameter;WebGLRenderingContext.prototype.getParameter = function(parameter) {if (parameter === 37445) {return 'NVIDIA Corporation'} if (parameter === 37446) {return 'NVIDIA GeForce GTX 980 Ti OpenGL Engine';}return getParameter(parameter);};")

    # def _upload_to_aws(self, local_file, bucket, s3_file):
    #     s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
    #                     aws_secret_access_key=SECRET_KEY)

    #     try:
    #         s3.upload_file(local_file, bucket, s3_file)
    #         print("Upload Successful")
    #         return True
    #     except FileNotFoundError:
    #         print("The file was not found")
    #         return False
    #     except NoCredentialsError:
    #         print("Credentials not available")
    #         return False
    #     except Exception as inst:
    #         log.error('err in upload_to_aws. msg:{}'.format(inst.args))

    #     # uploaded = upload_to_aws('/tmp/sparkline.svg', 'com.bitk.img', 'sparklines/7days/sparkline.svg')

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

    def _downloadSparkline(self, id):
        url = 'https://www.coingecko.com/coins/{}/sparkline'.format(id)
        self._driver.get(url)
        self._driver.implicitly_wait(3)

        log.debug('loading completed')

        svg = None

        for i in range(15):
            sleep(1)
            svg = self._driver.find_element_by_tag_name('svg')

            if svg is not None:
                break

        if svg is None:
            return False

        soup = BeautifulSoup( self._driver.page_source, 'lxml')
        svg = soup.find('svg')
        svgString = '{}'.format(svg)

        self._upload_to_aws(
            svgString,
            self._sparklineS3BucketName,
            '{}{}.svg'.format(self._sparklineOutputPrefix, id),
        )

    def updateSparkline(self, sparklineIDList):
        if self._createdInstance is False:
            return

        with self._lockList:
            for id in sparklineIDList:
                if id not in self._jobList:
                    self._jobList.append(id)

        # sparklineIDList

    def _processQueue(self):
        while True:
            sleep(10)
            
            try:
                jobId = 0

                with self._lockList:
                    if 0 >= len(self._jobList):
                        sleep(1)
                        continue
                    jobId = self._jobList[0]
                    self._jobList.remove(jobId)

                self._downloadSparkline(jobId)
                
                # 1개씩 처리합니다.
                continue

            except Exception as inst:
                log.error('failed in sparkline _processQueue. msg:{}'.format(inst.args))