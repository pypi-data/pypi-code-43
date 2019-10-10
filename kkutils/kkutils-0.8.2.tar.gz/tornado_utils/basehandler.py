#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Email: kai.zhang1@nio.com
Last modified: 2018-04-14 14:21:15
'''
import copy
import datetime
import hashlib
import json
import math
import re
import traceback

import tornado.gen
import tornado.web
from bson import ObjectId
from utils import Dict
from utils import JSONEncoder
from utils import property_wraps


class BaseHandler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request)
        self.logger = application.logger
        self.cache_enabled = application.cache_enabled
        self.ua = self.request.headers.get('User-Agent', '')

    def __getattr__(self, key):
        value = getattr(self.app, key)
        setattr(self, key, value)
        return value

    def _request_summary(self):
        return f"{self.request.method} {self.request.uri} ({self.ip})"

    @property
    @property_wraps
    def ip(self):
        if 'Cdn-Real-Ip' in self.request.headers:
            return self.request.headers['Cdn-Real-Ip']
        elif 'X-Forwarded-For' in self.request.headers:
            return self.request.headers['X-Forwarded-For'].split(',')[0]
        elif 'X-Real-Ip' in self.request.headers:
            return self.request.headers['X-Real-Ip']
        else:
            return self.request.remote_ip

    @property
    @property_wraps
    def mobile(self):
        mobile_re = re.compile(r'(iOS|iPhone|Android|Windows Phone|webOS|BlackBerry|Symbian|Opera Mobi|UCBrowser|MQQBrowser|Mobile|Touch)', re.I)
        return True if mobile_re.search(self.ua) else False

    @property
    @property_wraps
    def weixin(self):
        if self.get_argument('f', None) == 'weixin':
            return True
        else:
            weixin_re = re.compile(r'MicroMessenger', re.I)
            return True if weixin_re.search(self.ua) else False

    @property
    @property_wraps
    def cache_key(self):
        key = 'mobile' if self.mobile else 'pc'
        return f'{self.prefix}_{key}_{hashlib.md5(self.request.uri.encode()).hexdigest()}'

    def get_current_user(self):
        if hasattr(self.app, 'db'):
            token = self.get_cookie('user_token')
            return self.app.db.users.find_one({'token': token}) if token else Dict()

    def prepare(self):
        if self.app.cache_enabled and self.request.method in ['POST', 'PUT', 'DELETE']:
            self.app.rd.clear(f'{self.prefix}*')

    def write(self, chunk):
        if isinstance(chunk, (dict, list)):
            chunk = json.dumps(chunk, cls=JSONEncoder)
            self.set_header('Content-Type', 'application/json; charset=UTF-8')

        if self.app.cache_enabled and hasattr(self, 'cache_time') \
                and self.request.method == 'GET' and self._status_code == 200:
            self.app.rd.set(self.cache_key, chunk, self.cache_time)

        return super().write(chunk)

    def write_error(self, status_code, **kwargs):
        self.logger.error(f'{self.request.method} {self.request.uri} failed: {status_code}')
        if kwargs.get('exc_info'):
            msg = ''.join(traceback.format_exception(*kwargs["exc_info"]))
            self.logger.error(msg)
        super().write_error(status_code, **kwargs)

    def render(self, template_name, **kwargs):
        if self.get_argument('f', None) == 'json':
            self.finish(kwargs)
        else:
            super().render(template_name, **kwargs)

    @property
    @property_wraps
    def args(self):
        return self.get_args()

    @args.setter
    def args(self, value):
        self._args = value

    def get_args(self, **kwargs):
        if self.request.body and self.request.headers.get('Content-Type') == 'application/json':
            try:
                kwargs.update(json.loads(self.request.body))
            except Exception:
                self.logger.warning(self.request.body)

        for key, value in self.request.arguments.items():
            value = list(filter(None, map(lambda x: x.decode().strip(), value)))
            if value:
                kwargs[key] = value[0]

        for key in ['page', 'count', 'order']:
            if kwargs.get(key) is not None:
                kwargs[key] = int(kwargs[key])

        self.args = Dict(kwargs)
        return Dict(kwargs)

    def filter(self, query, include=[], exclude=[]):
        exclude = list(set(exclude) | set(['page', 'count', 'sort', 'order', 'f']))
        if include:
            query = dict(filter(lambda x: x[0] in include or x[0].startswith('$'), query.items()))
        query = dict(filter(lambda x: x[0] not in exclude, query.items()))
        return query

    def format(self, query, schema):
        for k, t in schema.items():
            if not (query.get(k) and t in [int, float, datetime]):
                continue
            if t in [int, float]:
                values = [t(x.strip()) if x.strip() else None for x in query[k].strip().split('~')]
            else:
                values = [x.strip() for x in query[k].strip().split('~')]
                for i, value in enumerate(values):
                    if value:
                        value = re.sub(r'[^\d]', '', value)
                        value += (14 - len(value)) * '0'
                        values[i] = datetime.datetime.strptime(value, '%Y%m%d%H%M%S')
                    else:
                        values[i] = None

            if len(values) == 1:
                query[k] = values[0]
            else:
                if values[0] is not None and values[-1] is not None:
                    query[k] = {'$gte': values[0], '$lte': values[-1]}
                elif values[0] is not None:
                    query[k] = {'$gte': values[0]}
                elif values[-1] is not None:
                    query[k] = {'$lte': values[-1]}
        return Dict(query)

    def query(self, collection, query=None, result=None, include=[], exclude=[], schema={}):
        query = copy.deepcopy(query or self.args)
        query = self.filter(query, include=include, exclude=exclude)
        query = self.format(query, schema)
        if query._id:
            query._id = ObjectId(query._id)
        self.logger.info(f'{self.app.db.name}.{collection} query: {query}')

        db = self.app.db_read if hasattr(self.app, 'db_read') else self.app.db
        if result is not None:
            projection = {k: 1 for k in result}
            cursor = db[collection].find(query, projection)
        else:
            cursor = db[collection].find(query)

        self.args.setdefault('order', - 1)
        self.args.setdefault('page', 1)
        self.args.setdefault('count', 20)
        if self.args.sort:
            cursor = cursor.sort(self.args.sort, self.args.order)
        cursor = cursor.skip((self.args.page - 1) * self.args.count).limit(self.args.count)

        self.args.total = cursor.count()
        self.args.pages = int(math.ceil(self.args.total / float(self.args.count)))
        return list(cursor)
