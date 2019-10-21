from com.fw.utils.id_util import IDUtils
from com.fw.base.base_exception import BaseException
import inspect

'''
主要是做dao数据库低层封装
1：get set str
2：字段反射
3：常用属性
'''


class BaseDao(object):
    table_name = None

    def __init__(self, id=None):
        if not id:
            id = IDUtils.get_primary_key()
        self.id = id

    def get_value(self, key):
        return self.__dict__.get(key)

    def set_value(self, key, value):
        self.__dict__[key] = value;

    def __str__(self):
        print(self.__dict__)

    def get_keys(self):
        return self.__dict__.keys()

    def __check_param(self):
        data_dict = self.__dict__

        if not data_dict:
            raise BaseException("THE DAO NO ATTRIBUTES")

        if "id" not in data_dict or not data_dict["id"]:
            raise BaseException("THE DAO PRIMARY KEY IS NONE")

        if len(data_dict) <= 1:
            raise BaseException("THE DAO ATTRIBUTE IS TOO LESS")

    @staticmethod
    def get_dao_fileds(T):
        data = inspect.signature(T.__init__).parameters
        result = []
        result.append("id")
        for key, val in data.items():
            if key != "self" and key != 'args' and key != 'kwargs':
                result.append(key)
        return result

    @staticmethod
    def dict_to_dao(data:dict):
        dao = BaseDao()
        for key, val in data.items():
            dao.set_value(key, val)
        return dao