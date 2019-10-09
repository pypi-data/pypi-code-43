import json
from datetime import datetime
from decimal import Decimal

from bson import Decimal128


class FixedTypeListException(Exception):
    pass


class FixedTypeList(list):
    def __init__(self, element_type, *args):
        self.element_type = element_type
        list.__init__(self, *args)

    def __setitem__(self, ind, val):
        self.__check_insert_obj_type(val)
        list.__setitem__(self, ind, val)

    def insert(self, idx, val):
        self.__check_insert_obj_type(val)
        list.insert(self, idx, val)

    def append(self, val):
        self.__check_insert_obj_type(val)
        list.append(self, val)

    def __check_insert_obj_type(self, obj):
        if not isinstance(obj, self.element_type):
            raise FixedTypeListException(
                'object to be inserted is not same of element_type, %s, %s'
                % (str(type(obj)), str(self.element_type)))


class JsonSerializerutils:

    @staticmethod
    def load_from_json(obj, json_str, input_encoding='gbk'):
        '''
        obj表示预期转换成的对象
        input_encoding表示输入json字符串的编码格式
        '''
        json_object = json.loads(json_str, input_encoding)
        return JsonSerializerutils._load_from_json_object(obj, json_object)

    @staticmethod
    def dump_to_json(obj, outpu_encoding='UTF-8', no_extra_space=True):
        '''
        obj为需要dump的对象
        output_encoding为输出json字符串的编码格式
        no_extra_space为True, 表示紧凑格式输出，不输出多余的空格
        '''
        json_object = JsonSerializerutils._dump_to_json_object(obj)
        sep = (',', ':') if no_extra_space else None
        return json.dumps(json_object, ensure_ascii=False,
                          separators=sep).encode(outpu_encoding)

    @staticmethod
    def _is_native_json_type(obj):
        return obj is None or isinstance(obj, bool) \
               or isinstance(obj, str) \
               or isinstance(obj, int) \
               or isinstance(obj, float)

    @staticmethod
    def _load_from_json_object(obj, json_object):
        if isinstance(json_object, dict):
            return JsonSerializerutils._load_from_json_dict(obj, json_object)
        elif isinstance(json_object, list):
            return JsonSerializerutils._load_from_json_array(obj, json_object)
        else:
            return json_object

    @staticmethod
    def _load_from_json_dict(obj, json_dict):
        for (k, v) in json_dict.items():
            if not hasattr(obj, k):
                raise ValueError("obj[%s] has no attribute[%s]" %
                                 (str(type(obj)), k))
            subobj = getattr(obj, k)
            subobj = JsonSerializerutils._load_from_json_object(subobj, v)
            setattr(obj, k, subobj)
        return obj

    @staticmethod
    def _load_from_json_array(array_obj, json_array):
        if isinstance(array_obj, FixedTypeList):
            element_type = array_obj.element_type
            for json_element in json_array:
                element_obj = JsonSerializerutils._load_from_json_object(element_type(), json_element)
                array_obj.append(element_obj)
        else:
            raise ValueError('must use FixedTypeList to store json array')
        return array_obj

    @staticmethod
    def _dump_to_json_object(obj):
        if isinstance(obj, list):
            return JsonSerializerutils._dump_array(obj)
        elif JsonSerializerutils._is_native_json_type(obj):
            return obj
        elif isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        elif isinstance(obj, Decimal128) or isinstance(obj, Decimal):
            return str(obj)
        else:
            return JsonSerializerutils._dump_custom_object(obj)

    @staticmethod
    def _dump_array(obj):
        sub_obj_list = []
        for s in obj:
            sub_obj_list.append(JsonSerializerutils._dump_to_json_object(s))
        return sub_obj_list

    @staticmethod
    def _dump_custom_object(obj):
        if isinstance(obj, dict):
            attr_list = obj
        else:
            attr_list = obj.__dict__
        json_object = {}
        for (key, val) in attr_list.items():
            json_object[key] = JsonSerializerutils._dump_to_json_object(val)
        return json_object
