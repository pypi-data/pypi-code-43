# coding=utf-8
from bson.errors import InvalidBSON
from bson.codec_options import CodecOptions
from operator import getitem
from elasticsearch import Elasticsearch
from pymongo import MongoClient
import logging
import json
import bson
import functools

LOGGER = logging.getLogger(__name__)

# Dictionary keys for sentiments.
POSITIVE = 'p'
NEGATIVE = 'n'
NEUTRAL = 'o'

SENTIMENT_VALS = {'p': 100, 'n': 10, 'o': 1}


def sentiment_to_field(sentiment):
    if sentiment == +1:
        return POSITIVE
    elif sentiment == -1:
        return NEGATIVE
    elif sentiment == 0:
        return NEUTRAL
    else:
        raise ValueError('%r is not a valid sentiment value' % sentiment)


def field_to_sentiment(field):
    if field == POSITIVE:
        return +1
    elif field == NEGATIVE:
        return -1
    elif field == NEUTRAL:
        return 0
    else:
        raise ValueError('%r is not a valid sentiment field' % field)


def get_polarity_representation(sentiments):
    # Map post's sentiments into four digit representation.
    # If a post has positive and negative sentiments then it is represented
    # as 1101. If a post contains negative and neutral sentiments then
    # its representation is 1011.
    sentiment = 1000
    for polarity in set(sentiments):
        # sometimes polarity is None. Why ???
        if polarity is None:
            polarity = 0
        sentiment += SENTIMENT_VALS[sentiment_to_field(polarity)]

    return sentiment


def decode_bson(body):
    try:
        options = CodecOptions(tz_aware=True)
        item = bson.BSON(body).decode(options)
        return item
    except InvalidBSON as e:
        LOGGER.error(e)
        LOGGER.warn(json.loads(body))
        LOGGER.warn(body)


def encode_bson(body):
    return bson.BSON.encode(body)


def getter_by_dot_separated(_dict, dot_separated_str):
    """ get dict value with dot notation
    :param _dict:
    :param dot_separated_str: key1.key2.key3
    :return:
    """
    return functools.reduce(getitem, dot_separated_str.split('.'), _dict)


class ElasticConn(object):
    def __init__(self, uri):
        self.uri = uri
        self.client = Elasticsearch(self.uri)

    def __enter__(self):
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.transport.close()


class MongoConn(object):
    def __init__(self, uri, db=None, collection=None):
        self.uri = uri
        self.client = MongoClient(uri)
        self.db = None
        self.collection = None
        if db:
            self.db = self.client[db]
            if collection:
                self.collection = self.db[collection]

    def __enter__(self):
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
