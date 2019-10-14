# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines helpful utilities for summarizing and uploading data."""

import os
from math import ceil
import json
import io
import pickle
try:
    from azureml._restclient.constants import RUN_ORIGIN
except ImportError:
    print("Could not import azureml.core, required if using run history")
from azureml.interpret.common.constants import History, IO

try:
    from azureml._logging import ChainedIdentity
except ImportError:
    from interpret_community.common.chained_identity import ChainedIdentity


class ArtifactUploader(ChainedIdentity):
    """A class for uploading explanation data to run history."""

    def __init__(self, run, max_num_blocks=None, block_size=None, **kwargs):
        """Initialize the upload mixin by setting up the storage policy."""
        self.storage_policy = {History.MAX_NUM_BLOCKS: 3, History.BLOCK_SIZE: 100}
        self._update_storage_policy(max_num_blocks, block_size)
        super(ArtifactUploader, self).__init__(**kwargs)
        self._logger.debug('Initializing ArtifactUploader')
        self.run = run

    def _update_storage_policy(self, max_num_blocks, block_size):
        if max_num_blocks is not None:
            self.storage_policy[History.MAX_NUM_BLOCKS] = max_num_blocks
        if block_size is not None:
            self.storage_policy[History.BLOCK_SIZE] = block_size

    def _create_upload_dir(self, explanation_id):
        self._logger.debug('Creating upload directory')
        # create the outputs folder
        upload_dir = './explanation/{}/'.format(explanation_id)
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir

    def _upload_artifact(self, upload_dir, artifact_name, values, upload_type=None):
        self._logger.debug('Uploading artifact')
        INTERPRET_EXT = '.interpret'
        try:
            if upload_type is None or upload_type == IO.JSON:
                json_string = json.dumps(values)
                stream = io.BytesIO(json_string.encode(IO.UTF8))
                file_string = '{}{}{}.{}'.format(upload_dir.lstrip('./'), artifact_name, INTERPRET_EXT, IO.JSON)
                self.run.upload_file(file_string, stream)
            else:
                pickle_string = pickle.dumps(values)
                stream = io.BytesIO(pickle_string)
                file_string = '{}{}{}.{}'.format(upload_dir.lstrip('./'), artifact_name, INTERPRET_EXT, IO.PICKLE)
                self.run.upload_file(file_string, stream)
        except ValueError as exp:
            self._logger.error('Cannot serialize numpy arrays as JSON')

    def _get_num_of_blocks(self, num_of_columns):
        block_size = self.storage_policy[History.BLOCK_SIZE]
        num_blocks = ceil(num_of_columns / block_size)
        max_num_blocks = self.storage_policy[History.MAX_NUM_BLOCKS]
        if num_blocks > max_num_blocks:
            num_blocks = max_num_blocks
        return num_blocks

    def _get_model_summary_artifacts(self, upload_dir, name, summary):
        self._logger.debug('Uploading model summary')
        num_columns = summary.shape[len(summary.shape) - 1]
        num_blocks = self._get_num_of_blocks(num_columns)
        block_size = self.storage_policy[History.BLOCK_SIZE]
        storage_metadata = {
            History.NAME: name,
            History.MAX_NUM_BLOCKS: self.storage_policy[History.MAX_NUM_BLOCKS],
            History.BLOCK_SIZE: self.storage_policy[History.BLOCK_SIZE],
            History.NUM_FEATURES: num_columns,
            History.NUM_BLOCKS: num_blocks
        }
        artifacts = [{} for _ in range(num_blocks)]
        # Chunk the summary and save it to Artifact
        start = 0
        for idx in range(num_blocks):
            if idx == num_blocks - 1:
                # on last iteration, grab everything that's left for the last block
                cols = slice(start, num_columns)
            else:
                cols = slice(start, start + block_size)
            block = summary[..., cols]
            block_name = '{}/{}'.format(name, idx)
            self._logger.debug('Uploading artifact for block: {}'.format(block_name))
            self._upload_artifact(upload_dir, block_name, block.tolist())
            artifacts[idx][History.PREFIX] = os.path.normpath('{}/{}/{}/{}'.format(RUN_ORIGIN,
                                                                                   self.run.id,
                                                                                   upload_dir,
                                                                                   block_name))
            start += block_size
        return artifacts, storage_metadata

    def upload_single_artifact_list(self, summary_object, artifact_tuple_list, explanation_id):
        """Upload data to individual run history artifacts from a list.

        :param summary_object: The object which aggregates metadata about the uploaded artifacts
        :type summary_object: azureml.interpret.common.ModelSummary
        :param artifact_tuple_list: A list with names, values, optional metadata and
            serialization format for each data type.  The serialization format can be
            json or pickle.
        :type artifact_tuple_list: (str, list, dict or None, str)
        :param explanation_id: The explanation ID the artifacts should be uploaded under
        :type explanation_id: str
        """
        upload_dir = self._create_upload_dir(explanation_id)
        for name, values, optional_metadata, upload_type in artifact_tuple_list:
            self._logger.debug('Uploading single {} artifact'.format(name))
            self._upload_artifact(upload_dir, name, values, upload_type)
            artifact_info = [{
                History.PREFIX: os.path.normpath('{}/{}/{}/{}'.format(RUN_ORIGIN,
                                                                      self.run.id,
                                                                      upload_dir,
                                                                      name))
            }]
            metadata_info = {History.NAME: name}
            if optional_metadata is not None:
                metadata_info.update(optional_metadata)
            summary_object.add_from_get_model_summary(name, (artifact_info, metadata_info))

    def upload_sharded_artifact_list(self, summary_object, artifact_tuple_list, explanation_id):
        """Upload data to sharded run history artifacts from a list.

        :param summary_object: The object which aggregates metadata about the uploaded artifacts
        :type summary_object: azureml.interpret.common.ModelSummary
        :param artifact_tuple_list: A list with names, and values for each data type
        :type artifact_tuple_list: (str, list)
        :param explanation_id: The explanation ID the artifacts should be uploaded under
        :type explanation_id: str
        """
        upload_dir = self._create_upload_dir(explanation_id)
        for name, values in artifact_tuple_list:
            self._logger.debug('Uploaded sharded {} artifacts'.format(name))
            artifacts = self._get_model_summary_artifacts(upload_dir, name, values)
            summary_object.add_from_get_model_summary(name, artifacts)
