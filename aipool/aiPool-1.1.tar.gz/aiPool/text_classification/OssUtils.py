# -*- coding: utf-8 -*-

import os
import shutil
import configparser
import oss2

# 以下代码展示了基本的文件上传、下载、罗列、删除用法。


# 首先初始化AccessKeyId、AccessKeySecret、Endpoint等信息。
# 通过环境变量获取，或者把诸如“<你的AccessKeyId>”替换成真实的AccessKeyId等。
#
# 以杭州区域为例，Endpoint可以是：
#   http://oss-cn-hangzhou.aliyuncs.com
#   https://oss-cn-hangzhou.aliyuncs.com
# 分别以HTTP、HTTPS协议访问。
# ossConfig = "./config.ini"
# config_raw = configparser.ConfigParser()
# config_raw.read(ossConfig)
#

class OSSUtils:

    def __init__(self):
        # oss_config = config_raw['oss']
        # 确认上面的参数都填写正确了
        #
        # self.access_key_id = os.getenv('OSS_TEST_ACCESS_KEY_ID', oss_config["OSS_TEST_ACCESS_KEY_ID"])
        # self.access_key_secret = os.getenv('OSS_TEST_ACCESS_KEY_SECRET', oss_config["OSS_TEST_ACCESS_KEY_SECRET"])
        # self.bucket_name = os.getenv('OSS_TEST_BUCKET', oss_config["OSS_TEST_BUCKET"])
        # self.endpoint = os.getenv('OSS_TEST_ENDPOINT', oss_config["OSS_TEST_ENDPOINT"])

        self.access_key_id = os.getenv('OSS_TEST_ACCESS_KEY_ID', "LTAIvaWUaUnzJ0Uj")
        self.access_key_secret = os.getenv('OSS_TEST_ACCESS_KEY_SECRET', "F8Rv7T3jJn6xSp6IpZEmR30fh7HKWJ")
        self.bucket_name = os.getenv('OSS_TEST_BUCKET', "luoaijun")
        self.endpoint = os.getenv('OSS_TEST_ENDPOINT', "oss-cn-beijing.aliyuncs.com")

        for param in (self.access_key_id, self.access_key_secret, self.bucket_name, self.endpoint):
            assert '<' not in param, '请设置参数：' + param

    def getBucket(self):
        # 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
        self.bucket = oss2.Bucket(oss2.Auth(self.access_key_id, self.access_key_secret), self.endpoint,
                                  self.bucket_name)

    def upload(self, fileName, str):
        # 上传一段字符串。Object名是motto.txt，内容是一段名言。
        self.bucket.put_object(fileName, str)

    def getMetadata(self, matadata):
        # 获取Object的metadata
        object_meta = self.bucket.get_object_meta(matadata)
        print('last modified: ' + object_meta.last_modified)
        print('etag: ' + object_meta.etag)
        print('size: ' + object_meta.content_length)

    def download(self, ossFileName, localFileName):
        # 下载到本地文件
        self.bucket.get_object_to_file(ossFileName, localFileName)

    def copy(self):
        # 把刚刚上传的Object下载到本地文件 “座右铭.txt” 中
        # 因为get_object()方法返回的是一个file-like object，所以我们可以直接用shutil.copyfileobj()做拷贝
        with open(oss2.to_unicode('本地座右铭.txt'), 'wb') as f:
            shutil.copyfileobj(self.bucket.get_object('motto.txt'), f)

    def uploadFile(self, ossFileName, localFileName):
        # 把本地文件 “座右铭.txt” 上传到OSS，新的Object叫做 “我的座右铭.txt”
        # 注意到，这次put_object()的第二个参数是file object；而上次上传是一个字符串。
        # put_object()能够识别不同的参数类型
        # with open(oss2.to_unicode('本地座右铭.txt'), 'rb') as f:
        #     self.bucket.put_object('云上座右铭.txt', f)
        # 上面两行代码，也可以用下面的一行代码来实现
        self.bucket.put_object_from_file(ossFileName, localFileName)

    def listObject(self,number):
        # 列举Bucket下10个Object，并打印它们的最后修改时间、文件名
        for i, object_info in enumerate(oss2.ObjectIterator(self.bucket)):
            print("{0} {1}".format(object_info.last_modified, object_info.key))

            if i >= number:
                break

    def delete(self,objectName):

        # 删除名为motto.txt的Object
        self.bucket.delete_object(objectName)

    def batchDelete(self,list):
        # 也可以批量删除
        # 注意：重复删除motto.txt，并不会报错
        self.bucket.batch_delete_objects(list)

    def exists(self,objectName):
        # 确认Object已经被删除了
        assert not self.bucket.object_exists(objectName)

    def get(self,ossName):
        # 获取不存在的文件会抛出oss2.exceptions.NoSuchKey异常
        try:
            self.bucket.get_object(ossName)
        except oss2.exceptions.NoSuchKey as e:
            print(u'已经被删除了：request_id={0}'.format(e.request_id))
        else:
            assert False


if __name__ == '__main__':
    oss = OSSUtils()
    oss.getBucket()
    oss.uploadFile("data/TextClassification/text.log","all.log")

