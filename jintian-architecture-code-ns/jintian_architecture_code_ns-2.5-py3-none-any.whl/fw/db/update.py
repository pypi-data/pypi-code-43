from enum import Enum


class Modifier(Enum):
    IS = "set"
    INC = "数字加减"
    MONGO_UNSET = "unset"
    MONGO_PUSH = "push"
    MONGO_PULL = "pull"
    MONGO_POP = "pop"
    MONGO_ADD_TO_SET = "addToSet"


class ModifierUpdate(object):

    def __init__(self, key: str, val: str, modifier=Modifier.IS):
        self.key = key
        self.val = val
        self.modifier = modifier


class UpdateUtils(object):

    def __init__(self):
        self.params = []

    def add_update(self, key: str, val: str, modifier=Modifier.IS):
        if not key or val is None:
            raise BaseException("缺少必要参数...")

        self.params.append(ModifierUpdate(key, val, modifier))
