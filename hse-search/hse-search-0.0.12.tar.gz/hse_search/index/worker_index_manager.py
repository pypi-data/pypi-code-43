import os
import json
import logging

from google.cloud import storage

from ..utils import get_blob_string_from_bucket
from .bigtable_index import BigTableIndex
from .sharded_index import ShardedIndex
from .http_index import HTTPIndex

class WorkerIndexManager:
  def __init__(self, project_id, gcs_bucket_name, cluster_root, worker_group_identifier):
    self.indices = {}
    self.aliases = {}
    self.config = {}
    self.project_id = project_id
    self.gcs_bucket_name = gcs_bucket_name
    self.cluster_root = cluster_root
    self.worker_group_identifier = worker_group_identifier
    self.storage_client = storage.Client(self.project_id)
    self.bucket = self.storage_client.bucket(self.gcs_bucket_name)
  
  def get_remote_config(self):
    blob_name = os.path.join(self.cluster_root, 'worker_groups', self.worker_group_identifier, 'worker_config.json')
    config = {}
    try:
      config_str = get_blob_string_from_bucket(self.bucket, blob_name)
      config = json.loads(config_str)
    except:
      print(f'CRITICAL ERROR: Unable to load worker config from {blob_name}')
      logging.error(f'CRITICAL ERROR: Unable to load worker config from {blob_name}')
    return config
  
  def create_index(self, index_name, config):
    try:
      index = None
      index_type = config.get('index_type')
      assert index_type in {'BigTableIndex', 'ShardedIndex', 'HTTPIndex'}

      schema_blob_name = os.path.join(self.cluster_root, 'schemas', config.get('schema_location'))

      if index_type == 'BigTableIndex':
        index = BigTableIndex(index_name,
                                project_id=self.project_id,
                                gcs_bucket_name=self.gcs_bucket_name,
                                schema_blob_name=schema_blob_name,
                                storage_client=self.storage_client,
                                instance_id=config.get('instance_id'),
                                table_id=config.get('table_id'))
      elif index_type == 'HTTPIndex':
        index = HTTPIndex(index_name,
                            project_id=self.project_id,
                            gcs_bucket_name=self.gcs_bucket_name,
                            schema_blob_name=schema_blob_name,
                            storage_client=self.storage_client,
                            url=config.get('url'))
      elif index_type == 'ShardedIndex':
        shard_configs = config.get('shards', [])
        shard_indices = []
        for config_obj in shard_configs:
          assert type(config_obj) is dict and len(config_obj) == 1
          shard_index_name = [k for k in config_obj][0]
          shard_config = config_obj[shard_index_name]
          shard_indices.append(self.create_index(shard_index_name, shard_config))

        index = ShardedIndex(index_name,
                              project_id=self.project_id,
                              gcs_bucket_name=self.gcs_bucket_name,
                              schema_blob_name=schema_blob_name,
                              storage_client=self.storage_client,
                              shards=shard_indices)
      return index
    except:
      print(f'CRITICAL ERROR: Could not load index [{index_name}] from config')
      logging.error(f'CRITICAL ERROR: Could not load index [{index_name}] from config')

  def update_indices(self):
    print('WorkerIndexManager.update_indices')
    new_config = self.get_remote_config()
    new_config_indices = new_config.get('indices', {})
    old_config_indices = self.config.get('indices', {})
    for index_name in new_config_indices:
      new_index_config = new_config_indices[index_name]
      old_index_config = old_config_indices.get(index_name)
      if not new_index_config == old_index_config:
        if old_index_config is not None:
          del self.indices[index_name]
        self.indices[index_name] = self.create_index(index_name, new_index_config)
    for index_name in old_config_indices:
      if index_name not in new_config_indices:
        del self.indices[index_name]
    self.config = new_config
    self.aliases = new_config.get('aliases', {})
  
  def get_index(self, index_name):
    return self.indices.get(self.aliases.get(index_name, index_name))
