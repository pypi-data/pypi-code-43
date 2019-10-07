import logging

from jsons import JsonSerializable, dump


class MyClass2(JsonSerializable.with_dump(strip_attr='log', fork=True)):
    def __init__(self):
        self.a = 1
        self.b = 2
        self.log = logging.getLogger(__name__)


class MyClass3(JsonSerializable):
    def __init__(self):
        self.a = 1
        self.b = 2
        self.log = logging.getLogger(__name__)

print(MyClass2().json)
print(MyClass3().json)