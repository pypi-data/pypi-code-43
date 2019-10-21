# -*- coding: utf-8 -*-
# Created at 01/02/2019

__author__ = "Rimba Prayoga"
__copyright__ = "Copyright 2019, 88Spares"
__credits__ = ["88 Tech"]

__maintainer__ = "Rimba Prayoga"
__email__ = "rimba47prayoga@gmail.com"
__status__ = "Development"

import copy
import json
import requests
from typing import List
from urllib.parse import urljoin
from django.conf import settings
from django.db import models
from django.db.models import Q, ObjectDoesNotExist
from django.utils.functional import cached_property


class _VirtualInstance(object):
    def __init__(self, model: str, payload: dict):
        self.__model = model
        self._payload = payload
        self._attrs = {}

    def __setattr__(self, key, value):
        try:
            super(_VirtualInstance, self).__setattr__(key, value)
            if key not in ["__model", "_attrs", "_payload"]:
                self._attrs.update({
                    key: value
                })
        except Exception:
            pass

    def __repr__(self):
        key = self._attrs.get('id') or self._attrs.get(next(iter(self._attrs)))
        return f"<{self.__model.capitalize()} Virtual Instance: {key}>"

    def save(self):
        instance = ORMServices(model=self.__model, fields=list(self._attrs))
        return instance.save(*(), **self._attrs)


try:
    ORM_SERVICE_URL = settings.ORM_SERVICE_URL
except AttributeError:
    ORM_SERVICE_URL = ''

try:
    ORM_SERVICE_AUTH_HEADER = settings.ORM_SERVICE_AUTH_HEADER
except AttributeError:
    ORM_SERVICE_AUTH_HEADER = ''


class ORMServices(object):
    """
    ORM Services Connector.
    because you are familiar with Django ORM.
    Use it like Django ORM :D
    """

    def __init__(self, model, fields=['__all__'], exclude_fields=None):
        if isinstance(model, str):
            self.model_name = model
        elif isinstance(model, type) and isinstance(model(), models.Model):
            self.model_name = model._meta.model_name
        else:
            raise TypeError('unsupported type "%s" for model.' % type(model))
        self.payload = {}
        self.fields = fields
        self.exclude_fields = exclude_fields
        self._result_cache = {}
        self.CHUNK_SIZE = 20

    ########################
    # PYTHON MAGIC METHODS #
    ########################

    def __repr__(self):
        if self.payload:
            data = self[:self.CHUNK_SIZE]
            if len(self) >= self.CHUNK_SIZE:
                data[-1] = '...(remaining elements truncated)...'
            return f"<Virtual Queryset {data}>"
        return super(ORMServices, self).__repr__()

    def __iter__(self):
        data = self._result_cache.get('result')
        if data is None:
            self.__bind()
            data = self._result_cache.get('result')
        return iter(data)

    def __len__(self):
        count = self._result_cache.get("count", 0)
        if not count and self.__last_query:
            self.__bind()
            count = self._result_cache.get("count", 0)
        return count

    def __bool__(self):
        return bool(len(self))

    def __getitem__(self, item):
        if isinstance(item, int):
            result_cache = self._result_cache.get('result')
            if result_cache:
                return result_cache[item]
        result_cache = self._result_cache.get('result')
        if result_cache:
            return result_cache[item]
        _self = self.__bind()
        if _self == self:
            result_cache = self._result_cache.get('result')
            return result_cache[item]
        return _self

    @cached_property
    def __exclude_params(self):
        return [
            "all",
            "exists",
            "count",
            "first",
            "last",
            "latest",
            "values",
            "save"
        ]

    @cached_property
    def __is_model_instance(self):
        for method in ["first", "last", "latest"]:
            if self.payload.get(method):
                return True
        return False

    @property
    def __payload_request(self):
        return {
            "model": self.model_name,
            "payload": self.payload,
            "fields": self.fields,
            "exclude_fields": self.exclude_fields
        }

    @property
    def __last_query(self) -> str:
        """
        :return: last query
        """
        try:
            return list(self.payload.keys())[-1]
        except IndexError:
            return ''

    @property
    def __is_return_different_object(self) -> bool:
        return self.__last_query in [
            'first', 'last', 'get', 'latest',
            'exists', 'count'
        ]

    @property
    def __is_return_instance(self) -> bool:
        return self.__last_query in ['first', 'last', 'get', 'latest']

    def __update_payload(self, name, data) -> None:
        try:
            existed = self.payload.get(name).copy()  # type: List
        except AttributeError:
            if isinstance(data, dict):
                data = [data]
        else:
            existed = existed.copy()
            if isinstance(data, (list, tuple)):
                for i in data:
                    if i not in existed:
                        existed.append(i)
            elif isinstance(data, dict):
                # this is magic python, that can check dict within list. :D
                if data not in existed:
                    existed.append(data)
            else:
                TypeError('unsupported type "%s" for updating data' % type(data))
            data = existed
        self.payload.update({
            name: data
        })

    # --- expressions
    def __resolve_q(self, params: Q, result, extra_params) -> List:
        """
        Resolve expression Q. e.g: Q(a=b) | Q(c=d).
        :param params:
        :param result:
        :param extra_params:
        :return:
        """
        if isinstance(params, Q):
            if len(params.children) > 1:
                _type, params, operand = params.deconstruct()
                operand = operand.get('_connector', 'AND')
                kwargs = {}
                for param in params:
                    if isinstance(param, tuple):
                        key, value = param
                        kwargs.update({
                            key: value
                        })
                    elif isinstance(param, Q):
                        extra_params.append(param)
                        continue
            else:
                _type, _, kwargs = params.deconstruct()
                operand = "AND"
                params = None  # break recursive function.
            result.append({
                'operand': operand,
                'kwargs': kwargs
            })
            return self.__resolve_q(params=params, result=result, extra_params=[])
        else:
            if extra_params:
                params = extra_params.pop(0)
                return self.__resolve_q(params=params, result=result, extra_params=extra_params)
        return result

    def __do_query(self, name, *args, **kwargs):
        clone = self._clone()
        if args:
            _args = []
            for arg in copy.deepcopy(args):
                if isinstance(arg, Q):
                    _kwargs = self.__resolve_q(arg, [], [])
                    clone.__update_payload(name, data=_kwargs)
                    args = ()
                else:
                    _args.append(arg)
            if _args:
                args = _args
        if args or kwargs or name in self.__exclude_params:
            payload = {
                "operand": "AND",
                "args": args,
                "kwargs": kwargs
            }
            clone.__update_payload(name, data=payload)
        if clone.__is_return_different_object:
            if clone.__is_return_instance:
                return clone.__bind()
            return clone.fetch()
        return clone

    def _clone(self):
        """
        :return: clone of current class
        """
        exclude_fields = self.exclude_fields
        if isinstance(exclude_fields, (dict, list)):
            exclude_fields = self.exclude_fields.copy()
        clone = self.__class__(self.model_name, self.fields.copy(), exclude_fields)
        clone.payload = self.payload.copy()
        return clone

    def __clear_query(self, name=None):
        if name is not None:
            try:
                del self.payload[name]
            except KeyError:
                pass
        else:
            self.payload = {}

    def __bind(self, model=None, data=None, with_relation=False):
        if data is None:
            data = self.fetch()

        if isinstance(data, dict):
            _model = model
            if _model is None:
                _model = self.model_name
            vi = _VirtualInstance(model=_model, payload=self.__payload_request)
            for key, value in data.items():
                if isinstance(value, dict) and with_relation:
                    value = self.__bind(model=key, data=value, with_relation=with_relation)
                setattr(vi, key, value)
            return vi
        vi = {
            "result": [],
            "count": 0
        }
        if isinstance(data, list):
            if self.__last_query in ['values', 'values_list']:
                vi.update({
                    "result": data
                })
            else:
                for i in data:
                    _vi = _VirtualInstance(model=self.model_name, payload=self.__payload_request)
                    for key, value in i.items():
                        if isinstance(value, dict) and with_relation:
                            value = self.__bind(model=key, data=value, with_relation=with_relation)
                        setattr(_vi, key, value)
                    vi.get('result').append(_vi)
                    vi.update({
                        "count": vi.get("count") + 1
                    })
            self._result_cache = vi
            return self

    def __bind_with_relation(self, relation_data):
        data = self.fetch_with_relation(relation_data)
        return self.__bind(data=data, with_relation=True)

    # for custom method
    def call_manager_method(self, name, *args, **kwargs):
        self.__clear_query(name='get')
        return self.__do_query(name, *args, **kwargs)

    # --- fetch data from orm services
    def __request_get(self, url, payload, params=None):
        response = requests.get(url, data=json.dumps(payload), headers={
            "content-type": "application/json",
            'Authorization': ORM_SERVICE_AUTH_HEADER
        }, params=params)
        if response.status_code == 404:
            raise ObjectDoesNotExist("%s matching query does not exist." % self.model_name.capitalize())
        try:
            return response.json()
        except json.decoder.JSONDecodeError:
            raise Exception(response.text)

    def __request_post(self, url, payload):
        response = requests.post(url, data=json.dumps(payload), headers={
            "content-type": "application/json",
            'Authorization': ORM_SERVICE_AUTH_HEADER
        })
        try:
            return response.json()
        except json.decoder.JSONDecodeError:
            raise Exception(response.text)

    def fetch(self):
        url = urljoin(ORM_SERVICE_URL, "/api/v1/orm_services/get_queryset")
        return self.__request_get(
            url=url,
            payload=self.__payload_request
        )

    def fetch_with_relation(self, relation_data):
        """
        fetch data with relation object
        :param relation_data: -- e.g: ORMServices(model='partitem').all()
                                      .fetch_with_relation({'member':[{'user': ['id', 'email']}]})
        :return: -- response: [{'member': {'user': {'id': 556, 'email': 'cobacoba@gmail.com'}}},]
        """
        payload = self.__payload_request.copy()
        payload.update({
            "relation_data": relation_data
        })
        url = urljoin(ORM_SERVICE_URL, "/api/v1/orm_services/get_queryset")
        return self.__request_get(
            url=url,
            payload=payload
        )

    def get_property(self, property_name):
        payload = self.__payload_request.copy()
        payload.update({
            "property_name": property_name
        })
        url = urljoin(ORM_SERVICE_URL, "/api/v1/orm_services/get_property")
        return self.__request_get(url=url, payload=payload)

    def call_property(self, property_name):
        payload = self.__payload_request.copy()
        payload.update({
            "property_name": property_name
        })
        url = urljoin(ORM_SERVICE_URL, "/api/v1/orm_services/call_property")
        return self.__request_get(url=url, payload=payload)

    # --- querying

    def get_queryset(self, *args, **kwargs):
        return self.__do_query('all', *args, **kwargs)

    def all(self):
        return self.get_queryset()

    def exists(self) -> bool:
        return self.__do_query('exists')

    def get(self, *args, **kwargs) -> _VirtualInstance:
        return self.__do_query('get', *args, **kwargs)

    def filter(self, *args, **kwargs):
        self.__clear_query(name='get')
        return self.__do_query('filter', *args, **kwargs)

    def exclude(self, *args, **kwargs):
        self.__clear_query(name='get')
        return self.__do_query('exclude', *args, **kwargs)

    def values(self, *args, **kwargs):
        self.__clear_query(name='get')
        return self.__do_query('values', *args, **kwargs)

    def values_list(self, *args, **kwargs):
        self.__clear_query(name='get')
        return self.__do_query('values_list', *args, **kwargs)

    def count(self, *args, **kwargs) -> int:
        self.__clear_query(name='get')
        return self.__do_query('count', *args, **kwargs)

    def first(self, *args, **kwargs) -> _VirtualInstance:
        self.__clear_query(name='get')
        return self.__do_query('first', *args, **kwargs)

    def last(self, *args, **kwargs) -> _VirtualInstance:
        self.__clear_query(name='get')
        return self.__do_query('last', *args, **kwargs)

    def latest(self, *args, **kwargs) -> _VirtualInstance:
        self.__clear_query(name='get')
        return self.__do_query('latest', *args, **kwargs)

    def order_by(self, *args, **kwargs):
        self.__clear_query(name='get')
        return self.__do_query('order_by', *args, **kwargs)

    def select_related(self, *args, **kwargs):
        self.__clear_query(name='get')
        return self.__do_query('select_related', *args, **kwargs)

    def prefetch_related(self, *args, **kwargs):
        self.__clear_query(name='get')
        return self.__do_query('prefetch_related', *args, **kwargs)

    def only(self, *args, **kwargs):
        self.__clear_query(name='get')
        return self.__do_query('only', *args, **kwargs)

    def defer(self, *args, **kwargs):
        self.__clear_query(name='get')
        return self.__do_query('defer', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.__do_query('delete', *args, **kwargs)

    def _save(self, payload=None):
        if payload is None:
            payload = self.__payload_request
        url = urljoin(ORM_SERVICE_URL, "/api/v1/orm_services/save")
        return self.__request_post(
            url=url,
            payload=payload
        )

    def save(self, payload=None, *args, **kwargs):
        self.__do_query('save', *args, **kwargs)
        return self._save(payload)
