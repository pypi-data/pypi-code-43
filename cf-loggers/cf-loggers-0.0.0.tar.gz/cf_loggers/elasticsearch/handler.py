import logging
from elasticsearch import Elasticsearch
from datetime import datetime
from .serializers import DefaultSerializer
import socket

try:
    from elasticsearch_async import AsyncElasticsearch
except Exception as e:
    print("NOTE: `pip install elasticsearch-async` not installed. "
          "So `AsyncESLoggingHandler` will not work. You can ignore "
          "this message")
    AsyncElasticsearch = None


class ESLoggingHandlerBase(logging.Handler):
    """
    Elasticsearch base Logger

    """
    es_cls = None

    IGNORE_FIELDS = ["funcName", "args"]

    def __init__(self, hosts=None, index=None, doc_type=None, extra_data=None, **kwargs):
        """
        
        :param hosts: 
        :param index: 
        :param doc_type: 
        :param extra_data: extra data in dict that you want to add to the log.
        :param kwargs: 
        """
        super(ESLoggingHandlerBase, self).__init__(**kwargs)
        self.hosts = hosts or []
        self.doc_type = doc_type
        self.index = index
        self.serializer = DefaultSerializer()
        self.es_client = self.es_cls(hosts=hosts, serializer=self.serializer)
        self.extra_fields = extra_data if extra_data else {}
        self.extra_fields.update(self.get_host_details())

    def log(self, body):
        self.es_client.index(index=self.index, doc_type=self.doc_type, body=body)

    @staticmethod
    def get_host_details():
        return {
            'host': socket.gethostname(),
            'host_ip': socket.gethostbyname(socket.gethostname())
        }

    def emit(self, record):
        self.format(record)
        body = {}
        for key, value in record.__dict__.items():
            if key not in self.IGNORE_FIELDS:
                body[key] = value
        body["logged_at"] = datetime.now()
        body.update(self.extra_fields)
        self.log(body)

    def close(self):
        pass


class ESLoggingHandler(ESLoggingHandlerBase):
    es_cls = Elasticsearch


class AsyncESLoggingHandler(ESLoggingHandlerBase):
    es_cls = AsyncElasticsearch
