import requests

from .index import Index

class HTTPIndex(Index):
  '''
  An index type that forwards queries to a searcher located at a specific url.
  Masters might have these to handle sending requests to the right workers.
  '''
  def __init__(self, name,
    project_id=None,
    gcs_bucket_name=None,
    schema_blob_name=None,
    schema=None,
    storage_client=None,
    url=None):
    super().__init__(name, 
      project_id=project_id,
      gcs_bucket_name=gcs_bucket_name,
      schema_blob_name=schema_blob_name,
      schema=schema,
      storage_client=storage_client)
    self.url = url
  
  def query(self, query,
      limit=10,
      offset=0,
      min_score=0,
      return_scores=True,
      return_doc_ids=True,
      return_documents=False,
      prefetch=True):

    data = {
      "index": self.name,
      "limit": limit,
      "offset": offset,
      "return_scores": return_scores,
      "return_doc_ids": return_doc_ids,
      "return_documents": return_documents,
      "query": query
    }
    r = requests.post(self.url, json=data)
    res = r.json()
    return res
