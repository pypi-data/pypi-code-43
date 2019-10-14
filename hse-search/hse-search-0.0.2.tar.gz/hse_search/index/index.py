import json
import time

from google.cloud import storage

from ..utils import get_blob_string_from_bucket, row_key_formatters
from ..mapping import Mapping
from ..analyzers import analyze
from ..query_result import EmptyQR
from ..query_components import QueryComponent
from ..query_parser import parse_query

from cachetools import cached, LRUCache, TTLCache


class Index(object):
  """
  A logical representation of an HSE index.
  Maintains in-memory caches for performance.
  """
  def __init__(self, name,
    project_id=None,
    gcs_bucket_name=None,
    schema_blob_name=None,
    schema=None):
    self.project_id = project_id
    self.storage_client = storage.Client(self.project_id)
    self.bucket = self.storage_client.bucket(gcs_bucket_name)

    self.load_schema(schema, schema_blob_name)
    self.mapping = Mapping(self.schema.get('mapping', {}))

    self.ttl_for_ttled_postings = int(self.schema.get('ttl', 60*5)) # 5 minutes default
    self.ttled_fields = set(self.schema.get('ttled_fields', []))
    
    self.lru_cache = LRUCache(10000)
    self.ttl_cache = TTLCache(10000, self.ttl_for_ttled_postings)
  
  def load_schema(self, schema, schema_blob_name):
    if schema is not None:
      if type(schema) is not dict:
        raise Exception('When schema is specified, it must be of type dict')
      self.schema = schema
    else:
      if schema_blob_name is None:
        raise Exception('Must specify either schema or schema_blob_name')
      else:
        if type(schema_blob_name) is not str:
          raise Exception('schema_blob_name must be type str')
        self.schema = json.loads(get_blob_string_from_bucket(self.bucket, schema_blob_name))

  def fetch_postings(self, row_key, field_type):
    return EmptyQR()
  
  def get_row_key(self, field, value):
    field_type = self.mapping.get_type(field)
    row_key = row_key_formatters[field_type](field, value)
    return row_key
  
  def batch_fetch_postings(self, row_keys_and_fields):
    pass

  def get_postings(self, field, value):
    row_key = self.get_row_key(field, value)
    field_type = self.mapping.get_type(field)

    cached_value = None

    has_ttl = field in self.ttled_fields

    if has_ttl:
      cached_value = self.ttl_cache.get(row_key)
    else:
      cached_value = self.lru_cache.get(row_key)
    
    if cached_value is not None:
      return cached_value
    else:
      fetched_qr = self.fetch_postings(row_key, field_type)
      if has_ttl:
        self.ttl_cache[row_key] = fetched_qr
      else:
        self.lru_cache[row_key] = fetched_qr
      return fetched_qr
      return fetched_qr
  
  def get_documents(self, doc_ids):
    return []
  
  def has_row_key_cached(self, row_key, field=None):
    if field is not None:
      if field in self.ttled_fields:
        return row_key in self.ttl_cache
      else:
        return row_key in self.lru_cache
    else:
      return row_key in self.lru_cache or row_key in self.ttl_cache
  
  def analyze(self, field, text, return_text=False):
    assert type(text) is str
    analyzer_type = self.mapping.get_analyzer(field)
    return analyze(text, analyzer=analyzer_type, return_text=return_text)

  def query(self, query,
      limit=10,
      offset=0,
      min_score=0,
      return_scores=True,
      return_doc_ids=True,
      return_documents=False,
      prefetch=True):
    print(json.dumps(query) + '\n')
    time_start = time.time()

    time_query_parse_start = time.time()

    try:
      query_object = None
      if isinstance(query, QueryComponent):
        query_object = query
      elif isinstance(query, dict):
        query_object = parse_query(query)
      time_query_parse_done = time.time()
      
      time_validate_start = time.time()
      query_object.validate(self, score=True)
      time_validate_done = time.time()

      time_prefetch_start = time.time()
      if prefetch:
        required_rows = query_object.required_rows(self, score=True)
        self.batch_fetch_postings(required_rows)
      time_prefetch_done = time.time()
      
      time_execution_start = time.time()
      ids, scores = query_object.execute(self, score=True).getTopN(limit + offset)
      time_execution_done = time.time()

      start = min(offset, ids.size)
      end = min(offset + limit, ids.size)

      doc_ids = [int(_id) for _id in ids[start:end]]

      response = {}
      if return_scores:
        response['scores'] = [float(score) for score in scores[start:end]]
      if return_doc_ids:
        response['docs'] = doc_ids
      if return_documents:
        response['hits'] = self.get_documents(doc_ids)

      time_finish = time.time()

      response['parsing_took'] = time_query_parse_done - time_query_parse_start
      response['validation_took'] = time_validate_done - time_validate_start
      response['prefetch_took'] = time_prefetch_done - time_prefetch_start
      response['query_took'] = time_execution_done - time_execution_start
      response['response_took_total'] = time_finish - time_start

      return response
    except Exception as e:
      return {
        'error': str(e)
      }
