import time

from multiprocessing.pool import ThreadPool
from .index import Index

class ShardedIndex(Index):
  '''
  An index type that fans out incoming queries to each of the shards. 
  '''
  def __init__(self, name,
    project_id=None,
    gcs_bucket_name=None,
    schema_blob_name=None,
    schema=None,
    shards=[],
    max_threads=4):
    super().__init__(name, 
      project_id=project_id,
      gcs_bucket_name=gcs_bucket_name,
      schema_blob_name=schema_blob_name,
      schema=schema)
    self.shards = shards
    self.max_threads = max_threads
    self.pool = ThreadPool(processes=min(len(shards), self.max_threads))
  
  def query_shard(self, shard_params_tuple):
    shard_num, query_info = shard_params_tuple

    query = query_info.get('query')

    return self.shards[shard_num].query(query,
      limit=query_info.get('limit'),
      offset=query_info.get('offset'),
      min_score=query_info.get('min_score'),
      return_scores=query_info.get('return_scores'),
      return_doc_ids=query_info.get('return_doc_ids'),
      return_documents=query_info.get('return_documents'),
      prefetch=query_info.get('prefetch')
    )

  
  def query(self, query,
      limit=10,
      offset=0,
      min_score=0,
      return_scores=True,
      return_doc_ids=True,
      return_documents=False,
      prefetch=True):
    
    query_info = {
      'query': query,
      'limit': limit + offset,
      'offset': 0,
      'min_score': 0,
      'return_scores': True,
      'return_doc_ids': True,
      'return_documents': return_documents,
      'prefetch': prefetch
    }

    sharded_queries = [(shard, query_info) for shard in range(len(self.shards))]

    query_results = self.pool.map(self.query_shard, sharded_queries)

    response = {
      'parsing_took': [qr.get('parsing_took') for qr in query_results],
      'validation_took': [qr.get('validation_took') for qr in query_results],
      'prefetch_took': [qr.get('prefetch_took') for qr in query_results],
      'query_took': [qr.get('query_took') for qr in query_results],
      'response_took_total': [qr.get('response_took_total') for qr in query_results]
    }
    shards_ids = [qr.get('docs', []) for qr in query_results]
    shards_scores = [qr.get('scores', []) for qr in query_results]
    ids = []
    scores = []
    shard_pointers = [0 for _ in query_results]
    for i in range(limit + offset):
      curr_max = None
      shard_of_max = -1
      for j in range(len(shard_pointers)):
        if len(shards_scores[j]) > shard_pointers[j] and (curr_max is None or shards_scores[j][shard_pointers[j]] > curr_max):
          curr_max = shards_scores[j][shard_pointers[j]]
          shard_of_max = j
      if shard_of_max != -1:
        ids.append(shards_ids[shard_of_max][shard_pointers[shard_of_max]])
        scores.append(shards_scores[shard_of_max][shard_pointers[shard_of_max]])
        shard_pointers[shard_of_max] += 1
    
    response['scores'] = scores[offset:limit+offset]
    response['ids'] = ids[offset:limit+offset]
    return response



