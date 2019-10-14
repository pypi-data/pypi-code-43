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
    url=None):
    super().__init__(name, 
      project_id=project_id,
      gcs_bucket_name=gcs_bucket_name,
      schema_blob_name=schema_blob_name,
      schema=schema)
    self.url = url