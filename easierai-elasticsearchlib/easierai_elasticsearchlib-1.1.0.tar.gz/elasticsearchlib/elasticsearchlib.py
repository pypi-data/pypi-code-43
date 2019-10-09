import datetime as dt
from elasticsearch import Elasticsearch
import logging
import pydash as _

import elasticsearchlib.elastic_queries as queries
import elasticsearchlib.elastic_mappings

import time

import socket
#from urllib3.exceptions import ConnectTimeoutError

# This comment is necessary because pylint throws errors when using the elasticsearch API because it uses decorators.
# pylint: disable=E1123
# By default, queries will target to up to 10000 documents (maximum permitted by Elastic, without tweaking the legacy setup)

MAX_QUERY_SIZE = 10000
QUERY_SIZE = 2000
MAX_RESPONSE_SIZE = 200000
class Elasticsearchlib:
    __instance = None

    def __new__(cls, logger=None):
        if Elasticsearchlib.__instance is None:
            Elasticsearchlib.__instance = object.__new__(cls)
        return Elasticsearchlib.__instance

    def __init__(self, logger=None):
        if not logger:
            self._logger = logging.getLogger(__name__)
            self._logger.setLevel(logging.WARNING)
        else:
            self._logger = logger

    def start_connection(self, host, port, request_retries=3, total_retries=9):
        """
        :param request_retries: number of times a request will be retried before being dropped
        :param total_retries: number of consecutive retries before dropping the connection and throwing an Exception
        """
        _es = Elasticsearch(hosts=[{'host': host,
                                    'port': port}])
        self.request_retries = request_retries
        self.total_retries = total_retries
        self.current_total_retries = self.total_retries
        self.es = _es
        ok = self.safe_ping()
        return ok, _es
        
    # Request functions
    def create_index(self, index, mapping=None):
        # TODO We should discuss if after not reaching the server for checking if the index exists, we should go on
        if not self.safe_index_exists(index):
            self._logger.info('New index detected, creating corresponding entity in DB...')
            was_created = self.safe_create_index(index, mapping)
            
            if was_created:
                self._logger.info("Created new index correctly for " + index)
                return True
            else:
                self._logger.error("Could not create new index for " + index)
                return False
        else:
            self._logger.debug("Index already exists for " + index)
            return True

    def add_to_index(self, index, body, id=''):
        return self.safe_add_to_index(index, body, id)

    def search_last_n_measures(self, index, id_dataset, n):
        if(n > QUERY_SIZE):
            size = QUERY_SIZE
        else:
            size = n
        filter_by_timestamp = queries.query_last_n_by_timestamp(id_dataset)
        ok, res = self.safe_search(self, index, filter_by_timestamp, size=size)
        if ok:
            scroll_id = res['_scroll_id']
            num_results = len(res['hits']['hits'])
            if(num_results):
                output = res['hits']['hits']
            else: 
                return False, []
        else: return False, []
        # TODO We should discuss if we want to return empty if there is timeout on the scrolling operation
        while(num_results < n):
            ok, res = self.safe_scroll(scroll_id)
            if ok:
                output = _.concat(output, res['hits']['hits'])
                num_results = num_results + len(res['hits']['hits'])
        self.safe_clear_scroll(scroll_id)
        return True, self.get_source_as_list(output)[:n]
    
    def remove_duplicates_by_field(self, object_list, field):
        processed_list = []
        c = 0
        for obj in object_list:
            if obj['_source'][field] not in processed_list:
                processed_list.append(obj['_source'][field])
            else:
                object_list.remove(obj)
                c += 1
        return object_list

    def scrolled_query(self, query, index, filter_path=None, query_size=QUERY_SIZE, max_size=MAX_RESPONSE_SIZE):
        '''
        : max_size parameter should be a multiple of query_size or the results won't have the expected size.
        '''
        output = []
        if query_size > MAX_QUERY_SIZE:
            self._logger.warning('Passing a greater query size ('+ str(query_size) +  ') than maximum permitted by elasticsearch. Setting value to ' + str(MAX_QUERY_SIZE))
            query_size = MAX_QUERY_SIZE
        ok, res = self.safe_search(index, query, filter_path, size=query_size)
        if ok:
            scroll_id = res['_scroll_id']
            if (res['hits']['total']['value']):
                output = _.concat(output, res['hits']['hits'])

            if (res['hits']['total']['value'] > QUERY_SIZE):
                more = True
                while more and len(output)<max_size:
                    ok, res = self.safe_scroll(scroll_id, filter_path=filter_path)
                    if ok:
                        if _.has(res, 'hits.hits'):
                            more = res['hits']['hits']
                            output = _.concat(output, res['hits']['hits'])
                    else:
                        return False, []
            # ToDo - performance and logging

            ###
        else:
            return False, []
        self.safe_clear_scroll(scroll_id)
        return True, output

    def get_entities_ids(self, index):

        filter_path = ['_scroll_id', 'took', 'hits.total', 'hits.hits._id']
        ok, aux = self.scrolled_query(queries.QUERY_ALL, index, filter_path)
        if ok:
            return True, _.map_(aux, lambda x: x['_id'])
        else: 
            return False, []

    def get_last_document(self, index, device_id):
        output = []
        query = queries.query_by_id(device_id)
        filter_path = ['hits.hits._source', 'hits.total', 'hits.hits._id']

        ok, res = self.safe_search(index, query, filter_path=filter_path, size=1, sort='timestamp:desc')
        if not ok:
            return output
        # ToDo - performance and logging

        ###
        if (res['hits']['total']['value'] > 0):
            output = _.head(res['hits']['hits'])
        else:
            output = []
        return True, output
    
    def get_last_document_with_params(self, index, device_id, params_filter):
        output = []
        query = queries.query_by_id_with_params(device_id, params_filter)
        filter_path = ['hits.hits._source', 'hits.total', 'hits.hits._id']
        ok, res = self.safe_search(index, query, filter_path=filter_path, size=1, sort='timestamp:desc')
        if not ok:
            return output
        # ToDo - performance and logging

        ###
        if (res['hits']['total']['value'] > 0):
            output = _.head(res['hits']['hits'])
        else:
            output = []
        return True, output

    def check_model_params(self, model_index, params_query):
        """
        This function searches for models in the database with params that match the current configuration. 
        """
        query = queries.query_check_model_params(params_query)
        filter_path = ['hits.total', 'hits.hits._source.id']
        ok, res = self.safe_search(model_index, query, filter_path=filter_path)
        if not ok:
            return []
        else:
            return res

    def get_data_history(self, index, device_id=None, gte='0', lte='now', time_index='timestamp', size=0, sort=None):
        filter_path = ['_scroll_id', 'took', 'hits.total', 'hits.hits._source']
        # Get all data
        query = queries.query_data_history(device_id, gte, lte, time_index, sort)
        if size:
            ok, aux = self.scrolled_query(query, index, filter_path, query_size=size, max_size=size)
        else: 
            ok, aux = self.scrolled_query(query, index, filter_path)
        aux = self.remove_duplicates_by_field(aux, time_index)
        if ok:
            return True, _.collections.map_(aux, lambda x: x['_source'])
        else:
            return False, []

    # Data operation functions
    def get_source_as_list(self, results, s_list=None):
        if (s_list is None):
            source_list = []
        else:
            source_list = s_list
        for el in results:
            source_list.append(el['_source'])
        return source_list

    # Private functions to manage retries
    def should_drop_connection(self):
        self.current_total_retries = self.current_total_retries - 1
        if(self.current_total_retries <= 0):
            raise Exception("Maximum number of retries exceeded")

    def reset_current_retries(self):
        self.current_total_retries = self.total_retries
        return 0

    def check_retries(self, retries):
        retries = retries - 1
        time.sleep(5)
        self.should_drop_connection()
        return retries
        
    # Private functions that provide a safe way to use the elasticsearch API
    def safe_scroll(self, scroll_id, scroll_period='2m', filter_path=None):
        retries = self.request_retries
        while(retries):
            try:
                res = self.es.scroll(scroll_id=scroll_id, scroll=scroll_period, filter_path=filter_path)
                retries = self.reset_current_retries()
            except Exception as ex:
                self._logger.error("Cannot perform scroll in Elastic " + str(ex))
                retries = self.check_retries(retries)
                if(retries == 0): return False, []
        return True, res
        
    def safe_search(self, index, query, filter_path=None, scroll_period='2m', size=QUERY_SIZE, sort=None):
        retries = self.request_retries
        while(retries):
            try:
                res = self.es.search(index=index, body=query, scroll=scroll_period,
                                filter_path=filter_path, size=size, sort=sort)
                retries = self.reset_current_retries()
            except Exception as ex:
                self._logger.error("Couldn't perform the scrolled query " + str(ex), query)
                retries = self.check_retries(retries)
                if(retries == 0): return False, []
        return True, res
    
    def safe_clear_scroll(self, scroll_id):
        retries = self.request_retries
        while(retries):
            try:
                self.es.clear_scroll(scroll_id=scroll_id)
                retries = self.reset_current_retries()
                return True
            except Exception as ex:
                self._logger.error("Couldn't clear scroll " + str(ex))
                retries = self.check_retries(retries)
                if(retries == 0): return False

    def safe_create_index(self, index, mapping):
        retries = self.request_retries
        while(retries):
            try:
                res = self.es.indices.create(index=index, body=mapping)
                retries = self.reset_current_retries()
                return res['acknowledged']
            except Exception as e:
                self._logger.error("Could not create new index for " + index + "  -  " + str(e))
                retries = self.check_retries(retries)
                if(retries == 0): return False

    def safe_add_to_index(self, index, body, id):
        retries = self.request_retries
        while(retries):
            try:
                self.es.index(index=index, body=body, id=id)
                retries = self.reset_current_retries()
                #TODO There should be some check for the correct addition to the index
                return True
            except Exception as e:
                self._logger.error('Cannot save document on Elastic - ' + str(e))
                retries = self.check_retries(retries)
                if(retries == 0): return False

    def safe_index_exists(self, index):
        retries = self.request_retries
        while(retries):
            try:
                exists = self.es.indices.exists(index)
                retries = self.reset_current_retries()
                return exists
            except Exception as ex:
                self._logger.error('Cannot check index on Elastic - ' + str(ex))
                retries = self.check_retries(retries)
                if(retries == 0): return False

    def safe_ping(self):
        retries = self.request_retries
        while(retries):
            try:
                self.es.ping()
                retries = self.reset_current_retries()
                self._logger.info('Connected successfully to Elasticsearch')
                return True
            except Exception as e:
                self._logger.error('Could not connect to Elasticsearch + ' + str(e))
                retries = self.check_retries(retries)
                if(retries == 0): return False
