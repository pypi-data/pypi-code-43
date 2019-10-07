# -*- coding: utf-8 -*-


from collections import OrderedDict


class HttpMethod:
    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"
    HEAD = "head"
    OPTIONS = "options"
    ANY = "any_"

    _valid_func_name_to_http_method_name_mapper = OrderedDict()

    @classmethod
    def is_valid_func_name(cls, name):
        return name in cls._valid_func_name_to_http_method_name_mapper

    @classmethod
    def get_all_valid_func_name(cls):
        return list(cls._valid_func_name_to_http_method_name_mapper.keys())

    @classmethod
    def get_all_valid_http_method(cls):
        return list(cls._valid_func_name_to_http_method_name_mapper.values())


for k, v in HttpMethod.__dict__.items():
    if (not k.startswith("_")) and (k.upper() == k):
        HttpMethod._valid_func_name_to_http_method_name_mapper[v] = k
