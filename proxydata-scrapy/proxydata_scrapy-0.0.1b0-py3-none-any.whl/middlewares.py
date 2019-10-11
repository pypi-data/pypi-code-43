# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import logging
import json
from scrapy.exceptions import NotConfigured
from scrapy.http import JSONRequest, TextResponse

logger = logging.getLogger(__name__)


class PFDDownloaderMiddleware(object):
    """
    Перенаправляет запрос через PFD
    """

    def __init__(self, settings):
        self.TOKEN = settings.get('PFD_TOKEN')
        self.API_URL = 'https://proxyfordevelopers.com/api/make-request/'

        # Если не установлен токен доступа к АПИ
        if not self.TOKEN:
            logger.error("Undefined PFD API access token. Check variable PFD_TOKEN in settings.py")
            raise NotConfigured("Undefined variable PFD_TOKEN")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        # Если урл уже поменяли
        if request.url == self.API_URL:
            return

        api_request_data = {}
        headers = request.headers
        user_agent = headers.pop(b'User-Agent', [])
        if user_agent:
            api_request_data['user_agent'] = ' '.join(
                [x.decode() for x in user_agent]
            )
        api_request_data['headers'] = {}
        for key, value in headers.items():
            if isinstance(value, bytes):
                api_request_data['headers'][key.decode()] = value.decode()
            elif isinstance(value, list):
                api_request_data['headers'][key.decode()] = ' '.join(
                    [val.decode() for val in value]
                )
        api_request_data['url'] = request.url
        api_request_data['request_type'] = 1 if request.method == 'POST' else 0
        api_request_data['request_data'] = request.body.decode()
        api_request_data['proxy_type'] = request.cb_kwargs.pop('proxy_type', 0)
        api_request_data['js_enabled'] = request.cb_kwargs.pop('js_enabled', False)
        api_request_data['country'] = request.cb_kwargs.pop('country', None)
        api_request_data['protocol'] = request.cb_kwargs.pop('protocol', 0)

        meta = request.meta
        meta['handle_httpstatus_list'] = [201]

        api_request = JSONRequest(
            url=self.API_URL,
            method='POST',
            headers={'Authorization': 'Token %s' % self.TOKEN},
            data=api_request_data,
            body=None,
            dont_filter=True,
            meta=meta,
            cb_kwargs=request.cb_kwargs,
            errback=request.errback,
            flags=request.flags,
            callback=request.callback,
            encoding=request.encoding,
            priority=request.priority
        )
        return api_request

    def process_response(self, request, response, spider):
        # как обрабатывать status 400 '["Max retries exceeded with url."]' ???
        proxy_status = response.status

        # API успешно обработал запрос
        if proxy_status == 201:
            self._set_api_response(response)
            url = self.get_url_from_response()

            response_data, status = self.parse_api_response()

            # Запрашиваемый ресурс вернул ответ
            httpstatus_list = getattr(spider, 'handle_httpstatus_list', [200])
            if status in httpstatus_list:
                response = TextResponse(**response_data)
                logger.debug(
                    "Request %s to API is successed. Status %s" % (url, proxy_status)
                )
                return response
            else:
                logger.error(
                    "Request %s to API is successed. But response status %s. Try request again" % (url, status)
                )
        else:
            body = response.body
            logger.error(
                "Request to API is failed. Status %s. Try request again" % (proxy_status)
            )
        return request

    def _set_api_response(self, response):
        self.api_response = json.loads(response.body)

    def get_url_from_response(self):
        """
        Достает первоначальный урл из ответа
        """
        return self.api_response.get('url')

    def parse_api_response(self):
        """
        Парсит ответ от API
        """
        api_response = self.api_response
        response_data = {}

        url = api_response.get('url')
        response_data['url'] = url

        status = api_response.get('status_code')
        response_data['status'] = status

        headers = json.loads(api_response.get('response_headers'))
        response_data['headers'] = headers

        body = api_response.get('response')
        response_data['body'] = body

        # Example content_type_data: "text/html; charset=UTF-8"
        content_type_data = headers['Content-Type'].split(';')
        charset = [c for c in content_type_data if 'charset' in c]
        if charset and len(charset) == 1:
            charset = charset[0].split('=')[-1]
            response_data['encoding'] = charset

        return response_data, status
