import json
import re

from flask import request

from .constant import REGEX_PARAM, ANY


class Comparisons:
    def __init__(self, path):
        self.path = path
        self.result = {}

    @staticmethod
    def _is_regex(value):
        return str(value).startswith(REGEX_PARAM)

    @staticmethod
    def _match_regex(regex, value):
        return re.match(regex[7:].replace("\\", "\\\\"), str(value))

    def _compare_simple_dict(self, config, _request):
        if len(config.items()) == len(_request.items()):
            for k, v in config.items():
                if isinstance(v, dict):
                    return self._compare_simple_dict(v, _request[k])
                elif (self._is_regex(v) and not self._match_regex(v, _request[k])) or (
                        not self._is_regex(v) and v != _request[k]):
                    return False
            return True
        return False

    def _compare_path(self, config, _request):
        if config and self._is_regex(config):
            return bool(self._match_regex(config, _request))
        return config is None or config == _request

    @staticmethod
    def _compare_method(config, _request):
        return config == _request

    def _compare_headers(self, config, _request):
        request_upper = {k.upper(): v for k, v in _request.items()}
        for k, v in config.items():
            if (self._is_regex(v) and not self._match_regex(v, request_upper.get(k.upper()))) or \
                    (not self._is_regex(v) and v != request_upper.get(k.upper())):
                return False
        return True

    @staticmethod
    def _compare_type(config, _request):
        return config == _request

    def _compare_body(self, config, _request):
        if config == ANY:
            return True
        return self._compare_simple_dict(config, _request)

    def _compare_query(self, config, _request):
        return self._compare_simple_dict(config, _request)

    def compare(self, value):
        when = value.get('when', {})
        try:
            compare_path = self._compare_path(when.get('path'), self.path)
            compare_method = self._compare_method(when.get('method'), request.method)
            compare_headers = self._compare_headers(when.get('header') or {}, dict(request.headers.items()))
            compare_type = self._compare_type(when.get('type'), request.content_type)
            compare_body = self._compare_body(when.get('body') or ANY, json.loads(request.data.decode('utf8') or '{}'))
            compare_query = self._compare_query(when.get('query') or {}, request.args.to_dict())
            if compare_path and compare_method and compare_headers and compare_type and compare_body and compare_query:
                return True
            self.result[value['id']] = {'path': compare_path,
                                        'method': compare_method,
                                        'header': compare_headers,
                                        'type': compare_type,
                                        'body': compare_body,
                                        'query': compare_query}
        except Exception as e:
            self.result[value['id']] = {'ERR': str(e)}
