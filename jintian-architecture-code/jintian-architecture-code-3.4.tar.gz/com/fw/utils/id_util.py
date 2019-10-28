'''
主键 和uuid 工具类
'''
import time
import shortuuid


class IDUtils(object):

    @staticmethod
    def get_primary_key(prefix: str = "", length=6):
        rand_str =  shortuuid.ShortUUID().random(length)
        return prefix +str(int(time.time())) + rand_str
