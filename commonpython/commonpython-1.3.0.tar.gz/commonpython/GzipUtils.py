#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@file: GzipUtils.py
@time: 2019/07/18
"""

import base64,gzip,traceback
class GzipUtils(object):
    '''
    gzip压缩工具类
    '''

    @classmethod
    def compress(cls,compressStr):
        '''
        压缩
        :param compressStr:
        :return:
        '''
        try:
            t = gzip.compress(compressStr.encode())
            return base64.b64encode(t).decode()
        except Exception as e:
            traceback.print_exc()
            return None

    @classmethod
    def uncompress(cls,uncompressStr):
        '''
        解压缩
        :param uncompressStr:
        :return:
        '''
        try:
            t = base64.b64decode(uncompressStr)
            return gzip.decompress(t).decode()
        except Exception as e:
            traceback.print_exc()
            return None


if __name__ == '__main__':
    t = GzipUtils.compress('111')
    print(t)
    print(GzipUtils.uncompress(t))