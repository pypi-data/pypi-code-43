from enum import Enum

class Sex(Enum):
    F = '女'
    M = '男'

class Switch(Enum):
    OPEN = '开启'
    CLOSE = "关闭"

class State(Enum):
    SUCCESS = "成功"
    FAIL = "失败"
    WAIT = "等待"
    RUN = "运行中"

class YN(Enum):
    Y = "yes"
    N = "no"

class ClassType(Enum):
    STR = "str"
    LIST = "list"
    INT = "int"
    FLOAT = "float"
    BOOLEAN = "boolean"
    BASE_DAO = "base_dao"

