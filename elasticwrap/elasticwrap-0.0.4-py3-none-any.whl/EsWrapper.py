import sys
import logging
import re
import json
from antlr4 import *
from elasticsearch5 import Elasticsearch as ES5
from elasticsearch5.exceptions import NotFoundError as NotFoundError5, \
    RequestError as RequestError5, TransportError as TransportError5
from elasticsearch6 import Elasticsearch as ES6
from elasticsearch6.exceptions import NotFoundError as NotFoundError6, \
    RequestError as RequestError6, TransportError as TransportError6
from elasticsearch import Elasticsearch as ES7
from elasticsearch.exceptions import NotFoundError as NotFoundError7, \
    RequestError as RequestError7, TransportError as TransportError7
from elasticwrap.parser.ESLexer import ESLexer
from elasticwrap.parser.ESListener import ESListener
from elasticwrap.parser.ESParser import ESParser

KEYS = [
    ('_term', '_key'),
    ('all_fields', 'default_field', '*')
]


class Elasticsearch(object):

    def __init__(self, host, es_version):
        self.host = host

        try:
            self.version = int(es_version)
        except ValueError as e:
            logging.exception(e)
            sys.exit(1)

        if self.version == 5:
            self.es = ES5(self.host)
        elif self.version == 6:
            self.es = ES6(self.host)
        elif self.version == 7:
            self.es = ES7(self.host)

    def inspect_query(self, key=None, substitution_key=None, substitution_value=None, dictionary=None):
        if key in dictionary:
            dictionary[substitution_key] = dictionary.pop(key)

            if substitution_value:
                dictionary[substitution_key] = substitution_value

        for k in dictionary.values():
            try:
                if isinstance(k, dict) or (isinstance(k, list) and isinstance(k[0], dict)):
                    self.inspect_query(key=key, substitution_key=substitution_key,
                                       substitution_value=substitution_value,
                                       dictionary=k if isinstance(k, dict) else k[0])

            except Exception as e:
                print(k, e)

        return dictionary

    def get_new_query(self, query):

        for tup in KEYS:
            # si hay que sustituir el key y el value...
            if len(tup) > 2:
                query = self.inspect_query(key=tup[0], substitution_key=tup[1], substitution_value=tup[2],
                                           dictionary=query)
            else:
                query = self.inspect_query(key=tup[0], substitution_key=tup[1], dictionary=query)

        return query

    def parse_query(self, query):
        try:
            query = json.dumps(query)
            query = json.loads(query)
        except Exception as e:
            print(e)
        try:
            if query['aggs']['terms']['terms']['order']:
                q = query['aggs']['terms']['terms']['order']
                if len((list(filter(lambda order: order['_term'] == 'asc', q)))) > 0 and isinstance(q[0], dict):
                    q[0]['_key'] = q[0].pop('_term')

                    query['aggs']['terms']['terms']['order'] = q
        except KeyError:
            pass

        try:
            query_tree = query['query']['function_score']['query']
        except KeyError:
            query_tree = query['query']

        query_tree = json.dumps(query_tree, ensure_ascii=False, separators=(',', ':'))
        input = InputStream(query_tree)
        lexer = ESLexer(input)
        stream = CommonTokenStream(lexer)
        parser = ESParser(stream)
        tree = parser.boolean()
        printer = ESListener()
        walker = ParseTreeWalker()
        walker.walk(printer, tree)
        input.reset()
        lexer.reset()
        stream.reset()
        parser.reset()

        reconstructed_bool_query = {
            "bool": printer.bools_pile[0]
        }
        try:
            query['query']['function_score']['query'] = reconstructed_bool_query
        except KeyError:
            query['query'] = reconstructed_bool_query

        
        return query

    def search(self, index, doc_type, body):
        if self.version == 5:
            try:
                rs = self.es.search(index, doc_type=doc_type, body=body)

            except (NotFoundError5, RequestError5, TransportError5) as e:
                logging.exception(e)
                sys.exit(1)

        elif self.version == 6:
            """
            Para la version 6 podemos mandar el mismo body, (linea comentada)
            es en la version 7 donde necesitamos modificar la query
            """
            # body = self.get_new_query(body)
            body = self.parse_query(body)

            try:
                rs = self.es.search(index=index + "_" + doc_type, doc_type=doc_type, body=body)

            except (NotFoundError6, RequestError6, TransportError6) as e:
                logging.exception(e)
                sys.exit(1)

        elif self.version == 7:

            body = self.parse_query(body)
            # body = self.get_new_query(body)

            try:
                rs = self.es.search(index=index + "_" + doc_type, body=body)

            except (NotFoundError7, RequestError7, TransportError7) as e:
                logging.exception(e)
                sys.exit(1)

        return rs
