import json

import numpy as np

from google.cloud import bigtable
from google.cloud.bigtable import row_filters, row_set

from ..query_result import IdsQR, IdsScoresQR
from .index import Index

def keyword_row_parser(row):
    ids_bytes = row.cells.get('i').get('i'.encode())[0].value
    ids = np.array(np.frombuffer(ids_bytes, dtype=np.int32), dtype=np.int32)
    return IdsQR(ids)

def integer_row_parser(row):
    ids_bytes = row.cells.get('i').get('i'.encode())[0].value
    ids = np.array(np.frombuffer(ids_bytes, dtype=np.int32), dtype=np.int32)
    scores_bytes = row.cells.get('s').get('i'.encode())[0].value
    scores = np.array(np.frombuffer(scores_bytes, dtype=np.float32), dtype=np.float32)
    return IdsScoresQR(ids, scores)

def float_row_parser(row):
    ids_bytes = row.cells.get('i').get('i'.encode())[0].value
    ids = np.array(np.frombuffer(ids_bytes, dtype=np.int32), dtype=np.int32)
    scores_bytes = row.cells.get('s').get('f'.encode())[0].value
    scores = np.array(np.frombuffer(scores_bytes, dtype=np.float32), dtype=np.float32)
    return IdsScoresQR(ids, scores)

def doc_row_parser(row):
    response = row.cells.get('doc').get('doc'.encode())[0].value
    try:
        return json.loads(response)
    except:
        return response

row_parsers = {
    'keyword': keyword_row_parser,
    'text': keyword_row_parser,
    'integer': integer_row_parser,
    'float': float_row_parser,
    'boolean': keyword_row_parser,
    'scored_keyword': float_row_parser,
    'doc': doc_row_parser,
}

class BigTableIndex(Index):
  def __init__(self, name,
    project_id=None,
    gcs_bucket_name=None,
    schema_blob_name=None,
    schema=None,
    instance_id=None,
    table_id=None,
    instance=None,
    table=None):
    super().__init__(name, 
      project_id=project_id,
      gcs_bucket_name=gcs_bucket_name,
      schema_blob_name=schema_blob_name,
      schema=schema)
    
    if table is not None:
      self.table = table
    else:
      if table_id is None:
        raise Exception('table_id or table must be provided')
      if instance is not None:
        self.table = instance.table(table_id)
      else:
        if instance_id is None:
          raise Exception('instance_id or instance must be provided')
        bt_client = bigtable.Client(self.project_id)
        instance = bt_client.instance(instance_id)
        self.table = instance.table(table_id)
    
    self.bt_row_filter = row_filters.CellsColumnLimitFilter(1)
  
  def bt_lookup(self, row_key):
    row = self.table.read_row(row_key.encode('utf-8'), self.bt_row_filter)
    return row

  def fetch_postings(self, row_key, field_type):
    row = self.bt_lookup(row_key)
    fetched_qr = None
    if row is not None:
      fetched_qr = row_parsers[field_type](row)
    else:
      fetched_qr = EmptyQR()
    return fetched_qr

  def batch_fetch_postings(self, row_keys_and_fields):
    row_keys_fields = {
      key: field for key, field in row_keys_and_fields
      if not self.has_row_key_cached(key, field=field)
    }
    row_keys_types = {key: self.mapping.get_type(row_keys_fields[key]) for key in row_keys_fields}

    rs = row_set.RowSet()
    set_size = 0
    for rk in row_keys_fields:
      rs.add_row_key(rk)
      set_size += 1
    if set_size > 0:
      partial_rows_data = self.table.read_rows(row_set=rs, filter_=self.bt_row_filter)
      partial_rows_data.consume_all()

      for rk in row_keys_types:
        row = partial_rows_data.rows.get(rk.encode())
        t = row_keys_types[rk]
        f = row_keys_fields[rk]
        qr = None
        if row is None:
          qr = EmptyQR()
        else:
          qr = row_parsers[t](row)
        
        if f in self.ttled_fields:
          self.ttl_cache[rk] = qr
        else:
          self.lru_cache[rk] = qr
    
  def get_documents(self, doc_ids):
    row_keys = ['doc|%s' % (i) for i in doc_ids]

    documents = []

    rs = row_set.RowSet()
    set_size = 0
    for rk in row_keys:
      rs.add_row_key(rk)
      set_size += 1
    if set_size > 0:
      partial_rows_data = self.table.read_rows(row_set=rs, filter_=self.bt_row_filter)
      partial_rows_data.consume_all()

      for rk in row_keys:
        row = partial_rows_data.rows.get(rk.encode())
        if row is not None:
          doc = row_parsers['doc'](row)
          documents.append(doc)
        else:
          documents.append(None)
    return documents