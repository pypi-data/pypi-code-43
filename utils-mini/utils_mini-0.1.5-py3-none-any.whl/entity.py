from utilsMini.parse import parseStr, parseDict, parseFloat, parseInt, parseList, parseTime
from types import FunctionType


class EntityMetaClass(type):
    def __new__(cls, name, bases, attrs):
        if name != "Entity":
            mappings = {}  # 定义好的字段
            # 循环加入对比映射序列
            for k, v in attrs.items():
                mappings[k] = v
            attrs['__mappings__'] = mappings  # 保存属性和列的映射关系
            if bases :
                for ibase in bases:
                    if ibase is not Entity:
                        attrs['__mappings__'].update(ibase.__mappings__)
        return type.__new__(cls, name, bases, attrs)


class FeildType():
    pass


class Entity(dict, metaclass=EntityMetaClass):
    """
    实体类型继承
    """
    def __getattribute__(self, key):
        if key in object.__getattribute__(self, '__mappings__'):
            if key in self:
                return self[key]
            else:
                return object.__getattribute__(self,
                                               '__mappings__')[key].default
        return object.__getattribute__(self, key)

    def __setattr__(self, key, value):
        if key in object.__getattribute__(self, '__mappings__'):
            self[key] = value

    def __init__(self, middleware=None, **kwargs):
        if isinstance(kwargs, dict):
            for k, v in kwargs.items():
                if k in self.__mappings__:
                    if middleware:
                        k, v = middleware(k, v)
                    if isinstance(self.__mappings__[k],
                                  (ObjectType, ListType)):
                        self[k] = self.__mappings__[k].parseValue(v)
                    elif issubclass(type(self.__mappings__[k]), FeildType):
                        self[k] = self.__mappings__[k].parseValue(v)
                    else:
                        self[k] = v


class StringType(FeildType):
    """
    实体强制类型
    """
    def __init__(self, default=""):
        self.default = default

    def parseValue(self, value):
        return parseStr(value, self.default)


class IntgerType(FeildType):
    """
    实体强制类型
    """
    def __init__(self, default=0):
        self.default = default

    def parseValue(self, value):
        return parseInt(value, self.default)


class FloatType(FeildType):
    """
    实体强制类型
    """
    def __init__(self, default=0.0):
        self.default = default

    def parseValue(self, value):
        return parseFloat(value, self.default)


class ListType(FeildType):
    """
    实体强制类型
    """
    def __init__(self, typeFeild, default=[]):
        self.default = default
        self.typeFeild = typeFeild

    def parseValue(self, value):
        tempList = parseList(value, self.default)
        res = []
        if tempList:
            if issubclass(self.typeFeild, Entity):
                for item in tempList:
                    res.append(self.typeFeild(**item))
            elif issubclass(self.typeFeild, FeildType):
                for item in tempList:
                    res.append(self.typeFeild().parseValue(item))
            elif isinstance(self.typeFeild, FunctionType):
                for item in tempList:
                    res.append(self.typeFeild(item))
            else:
                for item in tempList:
                    res.append(item)
        return res


class DictionaryType(FeildType):
    """
    实体强制类型
    """
    def __init__(self, default={}):
        self.default = default

    def parseValue(self, value):
        return parseDict(value, self.default)


class DateTimeType(FeildType):
    """
    实体强制类型
    """
    def __init__(self, default=None):
        if default is None:
            default = '%Y-%m-%d %H:%M:%S'
        self.default = default

    def parseValue(self, value):
        return parseTime(value, self.default)


class ObjectType(FeildType):
    """
    实体强制类型
    """
    def __init__(self, typeFeild):
        self.typeFeild = typeFeild
        self.default = None

    def parseValue(self, value):
        return self.typeFeild(**value)
