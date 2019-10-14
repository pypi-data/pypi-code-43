# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the client that uploads and downloads explanations."""

import os
import scipy as sp
import numpy as np
import pandas as pd
import json
import pickle

from azureml.interpret.common.constants import ExplainParams, ExplainType, History, BackCompat, IO
from azureml.interpret.common.model_summary import ModelSummary
try:
    from azureml.core import Experiment, Run, Workspace, Dataset
    from azureml._restclient.assets_client import AssetsClient
    from azureml._restclient.constants import RUN_ORIGIN
    from azureml.exceptions import UserErrorException
except ImportError:
    print("Could not import azureml.core, required if using run history")
from interpret_community.common.explanation_utils import _sort_values, \
    _sort_feature_list_multiclass, _unsort_1d, _unsort_2d, module_logger
from azureml.interpret.common.explanation_utils import ArtifactUploader
from interpret_community.explanation.explanation import _create_local_explanation, \
    _create_global_explanation
from interpret_community.explanation.explanation import FeatureImportanceExplanation, LocalExplanation, \
    GlobalExplanation, ExpectedValuesMixin, ClassesMixin, PerClassMixin

from shap.common import DenseData
from interpret_community.dataset.dataset_wrapper import DatasetWrapper


def _create_download_dir():
    """Create a consistently named and placed directory for explanation downloads.

    :return: The download path relative to the current directory.
    :rtype: str
    """
    # create the downloads folder
    download_dir = './download_explanation/'
    os.makedirs(download_dir, exist_ok=True)
    return download_dir


def _download_artifact(run, download_dir, artifact_name, extension, explanation_id=None, file_type=IO.JSON):
    """Download an artifact file from a run and load the contents.

    :param run: The run artifacts are stored under.
    :type run: azureml.core.run.Run
    :param download_dir: The directory to which the file should be downloaded.
    :type download_dir: str
    :param artifact_name: The path of the artifact in the cloud.
    :type artifact_name: str
    :param extension: '.interpret.json' for v5, '.json' for earlier versions.
    :type extension: str
    :param explanation_id: The explanation ID the file is stored under.
        If None, it is assumed that the run is using an old storage format.
    :type explanation_id: str
    :param file_type: A switch for pickle or JSON storage.
    :type file_type: str
    :return: The loaded values from the artifact that has been downloaded.
    :rtype: object
    """

    if artifact_name.startswith(RUN_ORIGIN):
        _, artifact_name = os.path.split(artifact_name)
    # else is backwards compatibility since February 2019
    artifact_path = 'explanation/{}/'.format(explanation_id) if explanation_id is not None else 'explanation/'
    interpret_string = '.interpret' if 'interpret' in extension else ''
    file_name = '{}{}{}.{}'.format(artifact_path, artifact_name, interpret_string, file_type)
    path = os.path.join(download_dir, file_name)
    run.download_file(file_name, path)
    with open(path, 'rb') as f:
        file_string = f.read()
        if file_type == IO.JSON:
            values = json.loads(file_string.decode(IO.UTF8))
        else:
            values = pickle.loads(file_string)
    return values


def _load_artifact(path):
    """More directly load a downloaded artifact file into memory.

    :param path: The path to the JSON encoded file on disk.
    :type path: str
    :return: The loaded values from the file.
    :rtype: object
    """
    with open(path, 'rb') as f:
        file_string = f.read()
        return json.loads(file_string.decode(IO.UTF8))


def _load_sharded_data(name, file_dict, storage_metadata, download_dir, extension, explanation_id=None):
    """Download and aggregate a chunk of data from its sharded storage format.

    :param name: The name/data type of the chunk to download_dir
    :type name: str
    :param file_dict: Dictionary which here holds the name of the file to load data from.
    :type file_dict: dict
    :param storage_metadata: The metadata dictionary for the asset's stored data
    :type storage_metadata: dict[str: dict[str: Union(str, int)]]
    :param download_dir: The directory to which the asset's files should be downloaded
    :type download_dir: str
    :param extension: '.interpret.json' for v5, '.json' for earlier versions.
    :type extension: str
    :param explanation_id: The explanation ID the data is stored under.
        If None, it is assumed that the asset is using an old storage format.
    :type explanation_id: str
    :param top_k: If specified, limit the ordered data returned to the most important features and values
    :type top_k: int
    :return: The data chunk, anything from 1D to 3D, int or str
    """
    num_columns_to_return = int(storage_metadata[name][History.NUM_FEATURES])
    num_blocks = int(storage_metadata[name][History.NUM_BLOCKS])
    file_name = file_dict[name]
    if BackCompat.OLD_NAME in storage_metadata[name]:
        module_logger.debug('Working with constructed metadata from a v1 asset')
        # Backwards compatibility as of January 2019
        name = storage_metadata[name][BackCompat.OLD_NAME]
    # Backwards compatibility as of February 2019
    connector = '/' if explanation_id is not None else '_'
    artifact = _load_artifact('{}{}0'.format(file_name, connector) + extension)
    full_data = np.array(artifact)
    concat_dim = full_data.ndim - 1
    # Get the blocks
    for idx in range(1, num_blocks):
        block_name = '{}{}{}'.format(file_name, connector, idx)
        block = np.array(_load_artifact(block_name + extension))
        full_data = np.concatenate([full_data, block], axis=concat_dim)
        num_columns_read = full_data.shape[-1]
        if num_columns_read >= num_columns_to_return:
            break
    full_data_list = full_data[..., :num_columns_to_return]
    return full_data_list


def _load_sharded_data_from_list(data_tuples, storage_metadata, download_dir, file_dict, extension,
                                 explanation_id=None):
    """Check each data name in the list.

    If available on the stored explanation, download the sharded chunks and reconstruct the explanation.

    :param data_tuples: A list of data names and dict key names for each kind of data to download
    :type data_tuples: list[(str, str)]
    :param storage_metadata: The metadata dictionary for the asset's stored data
    :type storage_metadata: dict[str: dict[str: Union(str, int)]]
    :param download_dir: The directory to which the asset's files should be downloaded
    :type download_dir: str
    :param file_dict: Dictionary which here holds the name of the file to load data from.
    :type file_dict: dict
    :param extension: '.interpret.json' for v5, '.json' for earlier versions.
    :type extension: str
    :param explanation_id: The explanation ID the data is stored under.
        If None, it is assumed that the asset is using an old storage format.
    :type explanation_id: str
    :param top_k: If specified, limit the ordered data returned to the most important features and values
    :type top_k: int
    :return: A dictionary of the data that was able to be downloaded from run history
    :rtype: dict
    """
    output_kwargs = {}
    for history_name, key_name in data_tuples:
        if history_name in file_dict:
            module_logger.debug('Downloading ' + history_name)
            values = _load_sharded_data(history_name, file_dict, storage_metadata, download_dir, extension,
                                        explanation_id=explanation_id)
            output_kwargs[key_name] = np.array(values)
    return output_kwargs


def _download_artifacts(run, download_dir, extension, explanation_id=None):
    """Download all artifacts from a given explanation.

    :param run: The run artifacts are stored on.
    :type run: azureml.core.run.Run
    :param download_dir: The directory to which the asset's files should be downloaded
    :type download_dir: str
    :param extension: '.interpret.json' for v5, '.json' for earlier versions.
    :type extension: str
    :param explanation_id: The explanation ID the data is stored under.
        If None, it is assumed that the asset is using an old storage format.
    :type explanation_id: str
    :return: A dictionary mapping short names of data to full file paths.
    :rtype: dict
    """

    # else is backwards compatibility starting February 2019
    artifact_path = os.path.join('explanation', explanation_id) if explanation_id is not None else 'explanation'
    run.download_files(prefix=artifact_path, output_directory=download_dir)
    files = os.listdir(os.path.join(download_dir, artifact_path))
    file_dict = {}
    for f in files:
        if extension in f:
            json_len = len(extension)
            short_name = f if f[-json_len:] != extension else f[:-json_len]
        else:
            json_len = len('.json')
            short_name = f if f[-json_len:] != '.json' else f[:-json_len]
        # TODO extend in case someone has more than 10 shards
        short_name = short_name if short_name[-2] != '_' else short_name[:-2]
        file_dict[short_name] = os.path.join(download_dir, artifact_path, short_name)

    return file_dict


class ExplanationClient(object):
    """Defines the client that uploads and downloads explanations."""

    def __init__(self, service_context, experiment_name, run_id, _run=None):
        """Create the client used to interact with explanations and run history.

        :param service_context: Holder for service information.
        :type service_context: ServiceContext
        :param run_id: A GUID that represents a run.
        :type run_id: str
        :param _run: A run. If passed in, other args will be ignored.
        :type _run: azureml.core.run.Run
        """
        if _run is not None:
            module_logger.debug('Using run to initialize explanation client with service_context = {},'
                                'experiment_name = {}, run_id = {}'.format(service_context, experiment_name, run_id))
            self._run = _run
        else:
            module_logger.debug('Constructing run from workspace, experiment, and run ID')
            sc = service_context
            workspace = Workspace(sc.subscription_id, sc.resource_group_name, sc.workspace_name,
                                  auth=sc.get_auth(), _disable_service_check=True)
            experiment = Experiment(workspace, experiment_name)
            self._run = Run(experiment, run_id=run_id)

        service_context._add_user_agent(service_context._get_assets_restclient(), 'mli_user_agent')

    @classmethod
    def from_run(cls, run):
        """Create the client with factory method given a run.

        :param run: The run explanations will be attached to.
        :type run: azureml.core.run.Run
        :return: An instance of the ExplanationClient
        :rtype: ExplanationClient
        """
        return cls(run.experiment.workspace.service_context, run.experiment, run.id, _run=run)

    @classmethod
    def from_run_id(cls, workspace, experiment_name, run_id):
        """Create the client with factory method given a run id.

        :param workspace: An object that represents a workspace.
        :type workspace: azureml.core.workspace.Workspace
        :param experiment_name: The name of an experiment.
        :type experiment_name: str
        :param run_id: A GUID that represents a run.
        :type run_id: str
        :return: An instance of the ExplanationClient
        :rtype: ExplanationClient
        """
        return cls(workspace.service_context, experiment_name, run_id)

    @property
    def run(self):
        """Get the run from the explanation client.

        :return: The run object.
        :rtype: azureml.core.run.Run
        """
        return self._run

    def upload_model_explanation(self,
                                 explanation,
                                 max_num_blocks=None,
                                 block_size=None,
                                 top_k=None,
                                 comment=None,
                                 init_dataset_id=None,
                                 eval_dataset_id=None,
                                 ys_pred_dataset_id=None,
                                 ys_pred_proba_dataset_id=None,
                                 upload_datasets=False,
                                 model_id=None):
        """Upload the model explanation information to run history.

        :param explanation: The explanation information to save.
        :type explanation: BaseExplanation
        :param max_num_blocks: The maximum number of blocks to store.
        :type max_num_blocks: int
        :param block_size: The size of each block for the summary stored in artifacts storage.
        :type block_size: int
        :param top_k: Number of important features stored in the explanation. If specified, only the
            names and values corresponding to the top K most important features will be returned/stored.
            If this is the case, global_importance_values and per_class_values will contain the top k sorted values
            instead of the usual full list of unsorted values.
        :type top_k: int
        :param comment: A string specified by user to identify the explanation. Displayed when listing
            explanations.  Allows the user to identify the explanations they have uploaded.
        :type comment: str
        :param init_dataset_id: The ID of the initialization (background) dataset in the Dataset service, if
            available. If not passed, the background dataset will be uploaded to the Dataset service.
        :type init_dataset_id: str
        :param eval_dataset_id: The ID of the evaluation dataset in the Dataset service, if available. If not passed,
            the evaluation dataset will be uploaded to the Dataset service.
        :type eval_dataset_id: str
        :param upload_datasets: If set to True and no dataset IDs are passed in, the evaluation dataset will be
            uploaded to Azure storage. This will improve the visualization available in the web view.
        :type upload_datasets: bool
        :param model_id: The MMS model ID.
        :type model_id: str
        """
        uploader = ArtifactUploader(self._run, max_num_blocks=max_num_blocks, block_size=block_size)
        assets_client = AssetsClient(self._run.experiment.workspace.service_context)
        classification = ClassesMixin._does_quack(explanation)
        if classification:
            model_type = ExplainType.CLASSIFICATION
        else:
            model_type = ExplainType.REGRESSION
        explainer_type = ExplainType.TABULAR
        # save model type and explainer type
        # Note: only call add properties once on a run; for multiple runs with different properties
        # this will only show the first properties set
        run_properties = self._run.get_properties()
        if ExplainType.MODEL not in run_properties and ExplainType.EXPLAINER not in explainer_type:
            self._run.add_properties({ExplainType.MODEL: model_type, ExplainType.EXPLAINER: explainer_type})
        summary_object = ModelSummary()
        single_artifact_list = []
        sharded_artifact_list = []

        is_raw = False
        if FeatureImportanceExplanation._does_quack(explanation):
            if explanation.features is not None:
                features = explanation.features if isinstance(explanation.features, list) else \
                    explanation.features.tolist()
                single_artifact_list.append((History.FEATURES, features, None, IO.JSON))
            is_raw = explanation.is_raw

        if LocalExplanation._does_quack(explanation):
            single_artifact_list.append((History.LOCAL_IMPORTANCE_VALUES, explanation.local_importance_values,
                                         None, IO.JSON))

        if ExpectedValuesMixin._does_quack(explanation):
            single_artifact_list.append((History.EXPECTED_VALUES, explanation.expected_values,
                                         None, IO.JSON))

        if GlobalExplanation._does_quack(explanation):
            global_importance_rank = explanation.global_importance_rank
            ranked_global_values = explanation.get_ranked_global_values()
            global_length = top_k if top_k is not None else len(global_importance_rank)
            global_importance_rank = global_importance_rank[:global_length]
            ranked_global_values = ranked_global_values[:global_length]

            if classification and PerClassMixin._does_quack(explanation):
                per_class_rank = np.array(explanation.per_class_rank)
                ranked_per_class_values = np.array(explanation.get_ranked_per_class_values())
                per_class_length = top_k if top_k is not None else per_class_rank.shape[1]
                per_class_rank = per_class_rank[:, :per_class_length]
                ranked_per_class_values = ranked_per_class_values[:, :per_class_length]
            if explanation.features is not None:
                ranked_global_names = explanation.get_ranked_global_names()
                if isinstance(ranked_global_names[0], str):
                    global_ordered_features = ranked_global_names
                else:
                    global_ordered_features = _sort_values(explanation.features,
                                                           global_importance_rank).tolist()
                global_ordered_features = global_ordered_features[:global_length]
                sharded_artifact_list.append((History.GLOBAL_IMPORTANCE_NAMES, np.array(global_ordered_features)))

                if classification and PerClassMixin._does_quack(explanation):
                    ranked_per_class_names = explanation.get_ranked_per_class_names()
                    if isinstance(ranked_per_class_names[0][0], str):
                        per_class_ordered_features = ranked_per_class_names
                    else:
                        per_class_ordered_features = _sort_feature_list_multiclass(explanation.features,
                                                                                   per_class_rank)
                    per_class_ordered_features = np.array(per_class_ordered_features)
                    per_class_ordered_features = per_class_ordered_features[:, :per_class_length]
                    sharded_artifact_list.append((History.PER_CLASS_NAMES, per_class_ordered_features))
            sharded_artifact_list.append((History.GLOBAL_IMPORTANCE_RANK, np.array(global_importance_rank)))
            sharded_artifact_list.append((History.GLOBAL_IMPORTANCE_VALUES, np.array(ranked_global_values)))

            if classification and PerClassMixin._does_quack(explanation):
                sharded_artifact_list.append((History.PER_CLASS_RANK, np.array(per_class_rank)))
                sharded_artifact_list.append((History.PER_CLASS_VALUES, np.array(ranked_per_class_values)))

        if classification and explanation.classes is not None:
            classes = explanation.classes
            if isinstance(classes, np.ndarray):
                classes = classes.tolist()
            single_artifact_list.append((History.CLASSES, classes, {History.NUM_CLASSES: len(classes)}, IO.JSON))

        uploader.upload_single_artifact_list(summary_object, single_artifact_list, explanation.id)
        uploader.upload_sharded_artifact_list(summary_object, sharded_artifact_list, explanation.id)

        meta_dict = summary_object.get_metadata_dictionary()

        if init_dataset_id is not None:
            meta_dict[History.INIT_DATASET_ID] = init_dataset_id

        if eval_dataset_id is None and hasattr(explanation, History.EVAL_DATA) and upload_datasets:
            eval_dataset_id = self._upload_dataset_to_service(explanation.eval_data,
                                                              explanation,
                                                              'eval_dataset.json',
                                                              '_eval')
        if eval_dataset_id is not None:
            meta_dict[History.EVAL_DATASET_ID] = eval_dataset_id

        if ys_pred_dataset_id is None and hasattr(explanation, History.EVAL_Y_PRED) and upload_datasets:
            ys_pred_dataset_id = self._upload_dataset_to_service(explanation.eval_y_predicted,
                                                                 explanation,
                                                                 'ys_pred.json',
                                                                 '_ys_pred')
        if ys_pred_dataset_id is not None:
            meta_dict[History.EVAL_Y_PRED] = ys_pred_dataset_id

        if ys_pred_proba_dataset_id is None and hasattr(explanation, History.EVAL_Y_PRED_PROBA) and upload_datasets:
            ys_pred_proba_dataset_id = self._upload_dataset_to_service(explanation.eval_y_predicted_proba,
                                                                       explanation,
                                                                       'ys_pred_proba.json',
                                                                       '_ys_pred_proba')
        if ys_pred_proba_dataset_id is not None:
            meta_dict[History.EVAL_Y_PRED_PROBA] = ys_pred_proba_dataset_id

        if model_id is None and hasattr(explanation, History.MODEL_ID):
            model_id = explanation.model_id

        # upload rich metadata information
        upload_dir = uploader._create_upload_dir(explanation.id)
        uploader._upload_artifact(upload_dir, History.RICH_METADATA, meta_dict)
        artifact_list = summary_object.get_artifacts()
        artifact_path = os.path.normpath('{}/{}/{}/{}'.format(RUN_ORIGIN, self._run.id, upload_dir,
                                                              History.RICH_METADATA))

        artifact_list.append({History.PREFIX: artifact_path})

        try:
            experiment_id = self._run.experiment.id
        except AttributeError:
            experiment_id = ''

        assets_client.create_asset(
            History.EXPLANATION_ASSET,
            artifact_list,
            metadata_dict={
                ExplainType.MODEL: ExplainType.CLASSIFICATION if classification else ExplainType.REGRESSION,
                ExplainType.DATA: explainer_type,
                ExplainType.EXPLAIN: explanation.method,
                ExplainType.MODEL_TASK: explanation.model_task,
                ExplainType.METHOD: explanation.method,
                ExplainType.MODEL_CLASS: explanation.model_type,
                ExplainType.IS_RAW: is_raw,
                History.METADATA_ARTIFACT: artifact_path,
                History.VERSION: History.EXPLANATION_ASSET_TYPE_V5,
                History.EXPLANATION_ID: explanation.id,
                History.COMMENT: comment,
                History.MODEL_ID: model_id,
                History.EXPERIMENT_ID: experiment_id,
                History.GLOBAL: GlobalExplanation._does_quack(explanation),
                History.LOCAL: LocalExplanation._does_quack(explanation),
                History.INIT_DATASET_ID: init_dataset_id,
                History.EVAL_DATASET_ID: eval_dataset_id,
                History.EVAL_Y_PRED: ys_pred_dataset_id,
                History.EVAL_Y_PRED_PROBA: ys_pred_proba_dataset_id
            },
            run_id=self._run.id,
            properties={History.TYPE: History.EXPLANATION,
                        History.EXPLANATION_ID: explanation.id}
        )

    def download_model_explanation(self, explanation_id=None, top_k=None, comment=None, raw=None):
        """Download a model explanation that has been stored in run history.

        :param explanation_id: If specified, tries to download the asset from the run with the given explanation ID.
            If unspecified, returns the most recently uploaded explanation.
        :type explanation_id: str
        :param top_k: If specified, limit the ordered data returned to the most important features and values.
            If this is the case, global_importance_values and per_class_values will contain the top k sorted values
            instead of the usual full list of unsorted values.
        :type top_k: int
        :param comment: A string used to filter explanations based on the strings they were uploaded with. Requires an
            exact match. If multiple explanations share this string, the most recent will be returned.
        :type comment: str
        :param raw: If True or False, explanations will be filtered based on whether they are raw or not. If nothing
            is specified, this filter will not be applied.
        :type raw: bool or None
        :return: The explanation as it was uploaded to run history
        :rtype: BaseExplanation
        """
        if top_k is None:
            return self._download_explanation_as_batch(explanation_id=explanation_id, comment=comment, raw=raw)
        else:
            return self._download_explanation_top_k(explanation_id=explanation_id, top_k=top_k, comment=comment,
                                                    raw=raw)

    def _download_explanation_as_batch(self, explanation_id=None, comment=None, raw=None):
        """Get an explanation from run history.

        :param explanation_id: If specified, tries to download the asset from the run with the given explanation ID.
            If unspecified, returns the most recently uploaded explanation.
        :type explanation_id: str
        :param comment: A string used to filter explanations based on the strings they were uploaded with. Requires and
            exact match. If multiple explanations share this string, the most recent will be returned.
        :type comment: str
        :param raw: If True or False, explanations will be filtered based on whether they are raw or not. If nothing
            is specified, this filter will not be applied.
        :type raw: bool or None
        :return: The explanation as it was uploaded to run history
        :rtype: BaseExplanation
        """
        kwargs = {}
        download_dir = _create_download_dir()
        assets_client = AssetsClient(self._run.experiment.workspace.service_context)
        explanation_assets = assets_client.get_assets_by_run_id_and_name(self._run.id, History.EXPLANATION_ASSET)

        mli_extension = '.interpret.json'

        # in case there's some issue with asset service, check
        if len(explanation_assets) > 0:
            module_logger.debug('Found at least one explanation asset, taking the first one')
            if explanation_id is not None:
                explanation_asset = None
                for asset in explanation_assets:
                    if (History.EXPLANATION_ID in asset.additional_properties[History.PROPERTIES] and
                            asset.additional_properties[History.PROPERTIES][History.EXPLANATION_ID] == explanation_id):
                        explanation_asset = asset
                if explanation_asset is None:
                    error_string = 'Could not find an explanation asset with id ' + explanation_id
                    module_logger.debug(error_string)
                    raise UserErrorException(error_string)
                if comment is not None and explanation_asset.meta[History.COMMENT] != comment:
                    error_string = 'Explanation asset with id {} does not have comment {}'.format(explanation_id,
                                                                                                  comment)
                    module_logger.debug(error_string)
                    raise UserErrorException(error_string)
                if raw is not None and (explanation_asset.meta[ExplainType.IS_RAW] == 'true') != raw:
                    error_string = 'Explanation asset with id {} does not have raw={}'.format(explanation_id, raw)
                    module_logger.debug(error_string)
                    raise UserErrorException(error_string)
            else:
                if comment is not None:
                    explanation_assets = list(filter(lambda x: x.meta[History.COMMENT] == comment, explanation_assets))
                if raw is not None:
                    explanation_assets = list(filter(lambda x: (x.meta[ExplainType.IS_RAW] == 'true') == raw,
                                                     explanation_assets))
                if len(explanation_assets) == 0:
                    raise UserErrorException('Did not find any explanations matching comment or raw filters.')
                # sort assets by upload time and return latest
                explanation_assets = sorted(explanation_assets, key=lambda asset: asset.created_time)
                explanation_asset = explanation_assets[-1]
                properties = explanation_asset.additional_properties[History.PROPERTIES]
                if History.EXPLANATION_ID in properties:
                    explanation_id = properties[History.EXPLANATION_ID]

        else:
            # if no asset, we can't do anything
            module_logger.debug('Did not find any explanation assets for run ' + str(self._run.id))
            return None

        # everything that might be available from the asset for construction an explanation
        local_importance_vals = None

        is_v1_asset = (History.VERSION not in explanation_asset.meta and
                       History.VERSION_TYPE not in explanation_asset.additional_properties[History.PROPERTIES])
        # back compat as of March 2019
        is_v2_release_asset = History.VERSION_TYPE in explanation_asset.additional_properties[History.PROPERTIES]

        if not is_v1_asset:

            if is_v2_release_asset:
                version = explanation_asset.additional_properties[History.PROPERTIES][History.VERSION_TYPE]
                is_under_v3_asset = True
            else:
                version = explanation_asset.meta[History.VERSION]
                # because it can't be v1 or v2 release here
                is_under_v3_asset = version == History.EXPLANATION_ASSET_TYPE_V2
            is_under_v4_asset = is_under_v3_asset or version == History.EXPLANATION_ASSET_TYPE_V3
            is_under_v5_asset = is_under_v4_asset or version == History.EXPLANATION_ASSET_TYPE_V4
            if is_under_v5_asset:
                mli_extension = '.json'
            file_dict = _download_artifacts(self._run, download_dir, mli_extension, explanation_id=explanation_id)

            module_logger.debug('Explanation asset is version {}'.format(version))
            if ExplainType.EXPLAIN in explanation_asset.meta:
                explanation_method = explanation_asset.meta[ExplainType.EXPLAIN]
            else:
                # backwards compatibilty as of February 2019
                explanation_method = ExplainType.SHAP
            storage_metadata = _load_artifact(file_dict[History.RICH_METADATA] + mli_extension)
            # classification and local importances are stored differently in v2/3 assets than in v1
            if ExplainType.MODEL in explanation_asset.meta:
                classification = explanation_asset.meta[ExplainType.MODEL] == ExplainType.CLASSIFICATION
            elif is_v2_release_asset:
                classification = History.PER_CLASS_VALUES in storage_metadata
            if History.LOCAL_IMPORTANCE_VALUES in file_dict:
                module_logger.debug('Downloading local importance values from v2/3/4')
                local_importance_filename = file_dict[History.LOCAL_IMPORTANCE_VALUES] + mli_extension
                local_importance_vals = np.array(_load_artifact(local_importance_filename))
            elif is_v2_release_asset:
                module_logger.debug('Downloading local importance values from release v2')
                local_importance_vals = np.array(_load_artifact(file_dict[BackCompat.SHAP_VALUES] + mli_extension))
            if History.FEATURES in file_dict:
                kwargs[ExplainParams.FEATURES] = np.array(_load_artifact(file_dict[History.FEATURES] + mli_extension))
            else:
                try:
                    # v2 release asset back compat as of March 2019
                    kwargs[ExplainParams.FEATURES] = _download_artifact(self._run, download_dir, History.FEATURES,
                                                                        mli_extension, explanation_id=explanation_id)
                except UserErrorException:
                    kwargs[ExplainParams.FEATURES] = None
        else:
            # v1 asset backwards compatibility as of January 2019
            module_logger.debug('Explanation asset is v1 version')
            mli_extension = '.json'
            # shap was the only option at the time
            explanation_method = ExplainType.SHAP
            storage_metadata = self._get_v2_metadata_from_v1(explanation_asset.meta)
            classification = History.PER_CLASS_VALUES in storage_metadata
            module_logger.debug('Downloading local importance values from v1')
            local_importance_vals = np.array(_download_artifact(self._run, download_dir, BackCompat.SHAP_VALUES,
                                                                mli_extension))
            kwargs[ExplainParams.FEATURES] = _download_artifact(self._run, download_dir, BackCompat.FEATURE_NAMES,
                                                                mli_extension)
            is_under_v3_asset = True
            is_under_v4_asset = True
            is_under_v5_asset = True
            file_dict = _download_artifacts(self._run, download_dir, mli_extension, explanation_id=explanation_id)
            file_dict = self._get_v2_file_dict_from_v1(file_dict)

        if not is_under_v4_asset:
            kwargs[ExplainParams.MODEL_TYPE] = explanation_asset.meta[ExplainType.MODEL_CLASS]
            explanation_method = explanation_asset.meta[ExplainType.METHOD]
            is_raw = explanation_asset.meta.get(ExplainType.IS_RAW, 'false') == 'true'
            kwargs[ExplainParams.IS_RAW] = is_raw
            if History.INIT_DATASET_ID in storage_metadata:
                kwargs[History.INIT_DATA] = storage_metadata[History.INIT_DATASET_ID]
            if History.EVAL_DATASET_ID in storage_metadata:
                kwargs[History.EVAL_DATA] = storage_metadata[History.EVAL_DATASET_ID]
            if History.EVAL_Y_PRED in storage_metadata:
                kwargs[History.EVAL_Y_PRED] = storage_metadata[History.EVAL_Y_PRED]
            if History.EVAL_Y_PRED_PROBA in storage_metadata:
                kwargs[History.EVAL_Y_PRED_PROBA] = storage_metadata[History.EVAL_Y_PRED_PROBA]
            if History.MODEL_ID in explanation_asset.meta:
                kwargs[History.MODEL_ID] = explanation_asset.meta[History.MODEL_ID]

        kwargs[ExplainParams.METHOD] = explanation_method
        kwargs[ExplainParams.CLASSIFICATION] = classification
        if classification:
            kwargs[ExplainParams.MODEL_TASK] = ExplainType.CLASSIFICATION
        else:
            kwargs[ExplainParams.MODEL_TASK] = ExplainType.REGRESSION
        if History.EXPECTED_VALUES in file_dict or is_v2_release_asset:
            module_logger.debug('Downloading expected values')
            expected_values_artifact = _load_artifact(file_dict[History.EXPECTED_VALUES] + mli_extension)
            kwargs[ExplainParams.EXPECTED_VALUES] = np.array(expected_values_artifact)

        if local_importance_vals is not None:
            module_logger.debug('Creating local explanation')
            local_explanation = _create_local_explanation(local_importance_values=local_importance_vals,
                                                          explanation_id=explanation_id,
                                                          **kwargs)
            kwargs[ExplainParams.LOCAL_EXPLANATION] = local_explanation
            if History.GLOBAL_IMPORTANCE_VALUES not in storage_metadata:
                module_logger.debug('Global importance values not found, returning local explanation')
                return local_explanation

        # Include everything available on storage metadata
        if History.CLASSES in storage_metadata:
            module_logger.debug('Downloading class names')
            try:
                # v2 release asset back compat as of March 2019
                # TODO
                kwargs[ExplainParams.CLASSES] = _download_artifact(self._run, download_dir, History.CLASSES,
                                                                   mli_extension, explanation_id=explanation_id)
            except UserErrorException:
                kwargs[ExplainParams.CLASSES] = None

        download_list = [
            (History.GLOBAL_IMPORTANCE_NAMES, ExplainParams.GLOBAL_IMPORTANCE_NAMES),
            (History.GLOBAL_IMPORTANCE_RANK, ExplainParams.GLOBAL_IMPORTANCE_RANK),
            (History.GLOBAL_IMPORTANCE_VALUES, ExplainParams.GLOBAL_IMPORTANCE_VALUES),
            (History.PER_CLASS_NAMES, ExplainParams.PER_CLASS_NAMES),
            (History.PER_CLASS_RANK, ExplainParams.PER_CLASS_RANK),
            (History.PER_CLASS_VALUES, ExplainParams.PER_CLASS_VALUES)
        ]
        downloads = _load_sharded_data_from_list(download_list, storage_metadata, download_dir, file_dict,
                                                 mli_extension, explanation_id=explanation_id)
        kwargs[History.GLOBAL_IMPORTANCE_RANK] = downloads[History.GLOBAL_IMPORTANCE_RANK]

        if History.PER_CLASS_RANK in file_dict:
            kwargs[History.PER_CLASS_RANK] = downloads[History.PER_CLASS_RANK]

        global_rank_length = len(kwargs[History.GLOBAL_IMPORTANCE_RANK])
        # check that the full explanation is available in run history so that it can be unsorted
        if kwargs[History.FEATURES] is not None:
            full_available = global_rank_length == len(kwargs[History.FEATURES])
        else:
            full_available = max(kwargs[History.GLOBAL_IMPORTANCE_RANK]) == global_rank_length - 1

        if full_available:
            # if we retrieve the whole explanation, we can reconstruct unsorted value order
            global_importance_values_unsorted = _unsort_1d(downloads[History.GLOBAL_IMPORTANCE_VALUES],
                                                           downloads[History.GLOBAL_IMPORTANCE_RANK])
            kwargs[History.GLOBAL_IMPORTANCE_VALUES] = global_importance_values_unsorted

            if History.PER_CLASS_RANK in file_dict:
                per_class_importance_values_unsorted = _unsort_2d(downloads[History.PER_CLASS_VALUES],
                                                                  downloads[History.PER_CLASS_RANK])
                kwargs[History.PER_CLASS_VALUES] = per_class_importance_values_unsorted
        else:
            # if we only retrieve top k, unsorted values cannot be fully reconstructed
            if History.GLOBAL_IMPORTANCE_NAMES in file_dict:
                kwargs[History.RANKED_GLOBAL_NAMES] = downloads[History.GLOBAL_IMPORTANCE_NAMES]
            kwargs[History.RANKED_GLOBAL_VALUES] = downloads[History.GLOBAL_IMPORTANCE_VALUES]

            if History.PER_CLASS_RANK in file_dict:
                if History.PER_CLASS_NAMES in file_dict:
                    kwargs[History.RANKED_PER_CLASS_NAMES] = downloads[History.PER_CLASS_NAMES]
                kwargs[History.RANKED_PER_CLASS_VALUES] = downloads[History.PER_CLASS_VALUES]
        return _create_global_explanation(explanation_id=explanation_id, **kwargs)

    def _download_explanation_top_k(self, explanation_id=None, top_k=None, comment=None, raw=None):
        """Get an explanation from run history.

        :param explanation_id: If specified, tries to download the asset from the run with the given explanation ID.
            If unspecified, returns the most recently uploaded explanation.
        :type explanation_id: str
        :param top_k: If specified, limit the ordered data returned to the most important features and values.
            If this is the case, global_importance_values and per_class_values will contain the top k sorted values
            instead of the usual full list of unsorted values.
        :type top_k: int
        :param comment: A string used to filter explanations based on the strings they were uploaded with. Requires an
            exact match. If multiple explanations share this string, the most recent will be returned.
        :type comment: str
        :param raw: If True or False, explanations will be filtered based on whether they are raw or not. If nothing
            is specified, this filter will not be applied.
        :type raw: bool or None
        :return: The explanation as it was uploaded to run history
        :rtype: BaseExplanation
        """
        kwargs = {}
        download_dir = _create_download_dir()
        assets_client = AssetsClient(self._run.experiment.workspace.service_context)
        explanation_assets = assets_client.get_assets_by_run_id_and_name(self._run.id, History.EXPLANATION_ASSET)

        mli_extension = '.interpret.json'

        # in case there's some issue with asset service, check
        if len(explanation_assets) > 0:
            module_logger.debug('Found at least one explanation asset, taking the first one')
            if explanation_id is not None:
                explanation_asset = None
                for asset in explanation_assets:
                    if (History.EXPLANATION_ID in asset.additional_properties[History.PROPERTIES] and
                            asset.additional_properties[History.PROPERTIES][History.EXPLANATION_ID] == explanation_id):
                        explanation_asset = asset
                if explanation_asset is None:
                    error_string = 'Could not find an explanation asset with id ' + explanation_id
                    module_logger.debug(error_string)
                    raise UserErrorException(error_string)
                if comment is not None and explanation_asset.meta[History.COMMENT] != comment:
                    error_string = 'Explanation asset with id {} does not have comment {}'.format(explanation_id,
                                                                                                  comment)
                    module_logger.debug(error_string)
                    raise UserErrorException(error_string)
                if raw is not None and (explanation_asset.meta[ExplainType.IS_RAW] == 'true') != raw:
                    error_string = 'Explanation asset with id {} does not have raw={}'.format(explanation_id, raw)
                    module_logger.debug(error_string)
                    raise UserErrorException(error_string)
            else:
                if comment is not None:
                    explanation_assets = list(filter(lambda x: x.meta[History.COMMENT] == comment, explanation_assets))
                if raw is not None:
                    explanation_assets = list(filter(lambda x: (x.meta[ExplainType.IS_RAW] == 'true') == raw,
                                                     explanation_assets))
                if len(explanation_assets) == 0:
                    raise UserErrorException('Did not find any explanations matching comment or raw filters.')
                # sort assets by upload time and return latest
                explanation_assets = sorted(explanation_assets, key=lambda asset: asset.created_time)
                explanation_asset = explanation_assets[-1]
                properties = explanation_asset.additional_properties[History.PROPERTIES]
                if History.EXPLANATION_ID in properties:
                    explanation_id = properties[History.EXPLANATION_ID]

        else:
            # if no asset, we can't do anything
            module_logger.debug('Did not find any explanation assets for run ' + str(self._run.id))
            return None

        # everything that might be available from the asset for construction an explanation
        local_importance_vals = None

        is_v1_asset = (History.VERSION not in explanation_asset.meta and
                       History.VERSION_TYPE not in explanation_asset.additional_properties[History.PROPERTIES])
        # back compat as of March 2019
        is_v2_release_asset = History.VERSION_TYPE in explanation_asset.additional_properties[History.PROPERTIES]

        if not is_v1_asset:
            if is_v2_release_asset:
                version = explanation_asset.additional_properties[History.PROPERTIES][History.VERSION_TYPE]
                is_under_v3_asset = True
            else:
                version = explanation_asset.meta[History.VERSION]
                # because it can't be v1 or v2 release here
                is_under_v3_asset = version == History.EXPLANATION_ASSET_TYPE_V2
            is_under_v4_asset = is_under_v3_asset or version == History.EXPLANATION_ASSET_TYPE_V3
            is_under_v5_asset = is_under_v4_asset or version == History.EXPLANATION_ASSET_TYPE_V4
            if is_under_v5_asset:
                mli_extension = '.json'
            module_logger.debug('Explanation asset is version {}'.format(version))
            if ExplainType.EXPLAIN in explanation_asset.meta:
                explanation_method = explanation_asset.meta[ExplainType.EXPLAIN]
            else:
                # backwards compatibilty as of February 2019
                explanation_method = ExplainType.SHAP
            metadata_artifact_name = explanation_asset.meta[History.METADATA_ARTIFACT]
            storage_metadata = _download_artifact(self._run, download_dir, metadata_artifact_name, mli_extension,
                                                  explanation_id=explanation_id)
            # classification and local importances are stored differently in v2/3 assets than in v1
            if ExplainType.MODEL in explanation_asset.meta:
                classification = explanation_asset.meta[ExplainType.MODEL] == ExplainType.CLASSIFICATION
            elif is_v2_release_asset:
                classification = History.PER_CLASS_VALUES in storage_metadata
            if History.LOCAL_IMPORTANCE_VALUES in storage_metadata:
                module_logger.debug('Downloading local importance values from v2/3')
                local_importance_vals = np.array(_download_artifact(self._run,
                                                                    download_dir,
                                                                    History.LOCAL_IMPORTANCE_VALUES,
                                                                    mli_extension,
                                                                    explanation_id=explanation_id))
            elif is_v2_release_asset:
                module_logger.debug('Downloading local importance values from release v2')
                local_importance_vals = np.array(_download_artifact(self._run,
                                                                    download_dir,
                                                                    BackCompat.SHAP_VALUES,
                                                                    mli_extension,
                                                                    explanation_id=explanation_id))
            if History.FEATURES in storage_metadata:
                kwargs[ExplainParams.FEATURES] = _download_artifact(self._run,
                                                                    download_dir,
                                                                    History.FEATURES,
                                                                    mli_extension,
                                                                    explanation_id=explanation_id)
            else:
                try:
                    # v2 release asset back compat as of March 2019
                    kwargs[ExplainParams.FEATURES] = _download_artifact(self._run,
                                                                        download_dir,
                                                                        History.FEATURES,
                                                                        mli_extension,
                                                                        explanation_id=explanation_id)
                except UserErrorException:
                    kwargs[ExplainParams.FEATURES] = None
        else:
            # v1 asset backwards compatibility as of January 2019
            module_logger.debug('Explanation asset is v1 version')
            # shap was the only option at the time
            explanation_method = ExplainType.SHAP
            storage_metadata = self._get_v2_metadata_from_v1(explanation_asset.meta)
            classification = History.PER_CLASS_VALUES in storage_metadata
            module_logger.debug('Downloading local importance values from v1')
            local_importance_vals = np.array(_download_artifact(self._run, download_dir, BackCompat.SHAP_VALUES,
                                                                mli_extension))
            kwargs[ExplainParams.FEATURES] = _download_artifact(self._run, download_dir, BackCompat.FEATURE_NAMES,
                                                                mli_extension)
            is_under_v3_asset = True

        is_under_v4_asset = is_under_v3_asset or version == History.EXPLANATION_ASSET_TYPE_V3
        if not is_under_v4_asset:
            kwargs[ExplainParams.MODEL_TYPE] = explanation_asset.meta[ExplainType.MODEL_CLASS]
            is_raw = explanation_asset.meta.get(ExplainType.IS_RAW, 'false') == 'true'
            kwargs[ExplainParams.IS_RAW] = is_raw
            explanation_method = explanation_asset.meta[ExplainType.METHOD]
            if History.INIT_DATASET_ID in storage_metadata:
                kwargs[History.INIT_DATA] = storage_metadata[History.INIT_DATASET_ID]
            if History.EVAL_DATASET_ID in storage_metadata:
                kwargs[History.EVAL_DATA] = storage_metadata[History.EVAL_DATASET_ID]
            if History.EVAL_Y_PRED in storage_metadata:
                kwargs[History.EVAL_Y_PRED] = storage_metadata[History.EVAL_Y_PRED]
            if History.EVAL_Y_PRED_PROBA in storage_metadata:
                kwargs[History.EVAL_Y_PRED_PROBA] = storage_metadata[History.EVAL_Y_PRED_PROBA]
            if History.MODEL_ID in explanation_asset.meta:
                kwargs[History.MODEL_ID] = explanation_asset.meta[History.MODEL_ID]
        kwargs[ExplainParams.METHOD] = explanation_method
        kwargs[ExplainParams.CLASSIFICATION] = classification
        if classification:
            kwargs[ExplainParams.MODEL_TASK] = ExplainType.CLASSIFICATION
        else:
            kwargs[ExplainParams.MODEL_TASK] = ExplainType.REGRESSION
        if History.EXPECTED_VALUES in storage_metadata or is_v2_release_asset:
            module_logger.debug('Downloading expected values')
            expected_values_artifact = _download_artifact(self._run,
                                                          download_dir,
                                                          History.EXPECTED_VALUES,
                                                          mli_extension,
                                                          explanation_id=explanation_id)
            kwargs[ExplainParams.EXPECTED_VALUES] = np.array(expected_values_artifact)

        if local_importance_vals is not None:
            module_logger.debug('Creating local explanation')
            local_explanation = _create_local_explanation(local_importance_values=local_importance_vals,
                                                          explanation_id=explanation_id,
                                                          **kwargs)
            kwargs[ExplainParams.LOCAL_EXPLANATION] = local_explanation
            if History.GLOBAL_IMPORTANCE_VALUES not in storage_metadata:
                module_logger.debug('Global importance values not found, returning local explanation')
                return local_explanation

        # Include everything available on storage metadata
        if History.CLASSES in storage_metadata:
            module_logger.debug('Downloading class names')
            try:
                # v2 release asset back compat as of March 2019
                kwargs[ExplainParams.CLASSES] = _download_artifact(self._run,
                                                                   download_dir,
                                                                   History.CLASSES,
                                                                   mli_extension,
                                                                   explanation_id=explanation_id)
            except UserErrorException:
                kwargs[ExplainParams.CLASSES] = None

        download_list = [
            (History.GLOBAL_IMPORTANCE_NAMES, ExplainParams.GLOBAL_IMPORTANCE_NAMES),
            (History.GLOBAL_IMPORTANCE_RANK, ExplainParams.GLOBAL_IMPORTANCE_RANK),
            (History.GLOBAL_IMPORTANCE_VALUES, ExplainParams.GLOBAL_IMPORTANCE_VALUES),
            (History.PER_CLASS_NAMES, ExplainParams.PER_CLASS_NAMES),
            (History.PER_CLASS_RANK, ExplainParams.PER_CLASS_RANK),
            (History.PER_CLASS_VALUES, ExplainParams.PER_CLASS_VALUES)
        ]

        downloads = self._download_sharded_data_from_list(download_list,
                                                          storage_metadata,
                                                          download_dir,
                                                          mli_extension,
                                                          explanation_id=explanation_id,
                                                          top_k=top_k)
        kwargs[History.GLOBAL_IMPORTANCE_RANK] = downloads[History.GLOBAL_IMPORTANCE_RANK]

        if History.PER_CLASS_RANK in downloads:
            kwargs[History.PER_CLASS_RANK] = downloads[History.PER_CLASS_RANK]

        global_rank_length = len(kwargs[History.GLOBAL_IMPORTANCE_RANK])
        # check that the full explanation is available in run history so that it can be unsorted
        if kwargs[History.FEATURES] is not None:
            full_available = global_rank_length == len(kwargs[History.FEATURES])
        else:
            full_available = max(kwargs[History.GLOBAL_IMPORTANCE_RANK]) == global_rank_length - 1

        if top_k is None and full_available:
            # if we retrieve the whole explanation, we can reconstruct unsorted value order
            global_importance_values_unsorted = _unsort_1d(downloads[History.GLOBAL_IMPORTANCE_VALUES],
                                                           downloads[History.GLOBAL_IMPORTANCE_RANK])
            kwargs[History.GLOBAL_IMPORTANCE_VALUES] = global_importance_values_unsorted

            if History.PER_CLASS_RANK in downloads:
                per_class_importance_values_unsorted = _unsort_2d(downloads[History.PER_CLASS_VALUES],
                                                                  downloads[History.PER_CLASS_RANK])
                kwargs[History.PER_CLASS_VALUES] = per_class_importance_values_unsorted
        else:
            # if we only retrieve top k, unsorted values cannot be fully reconstructed
            if History.GLOBAL_IMPORTANCE_NAMES in downloads:
                kwargs[History.RANKED_GLOBAL_NAMES] = downloads[History.GLOBAL_IMPORTANCE_NAMES]
            kwargs[History.RANKED_GLOBAL_VALUES] = downloads[History.GLOBAL_IMPORTANCE_VALUES]

            if History.PER_CLASS_RANK in downloads:
                if History.PER_CLASS_NAMES in downloads:
                    kwargs[History.RANKED_PER_CLASS_NAMES] = downloads[History.PER_CLASS_NAMES]
                kwargs[History.RANKED_PER_CLASS_VALUES] = downloads[History.PER_CLASS_VALUES]
        return _create_global_explanation(explanation_id=explanation_id, **kwargs)

    def list_model_explanations(self, comment=None, raw=None):
        """Return a dictionary of metadata for all model explanations available.

        :param comment: A string used to filter explanations based on the strings they were uploaded with. Requires an
            exact match.
        :type comment: str
        :param raw: If True or False, explanations will be filtered based on whether they are raw or not. If nothing
            is specified, this filter will not be applied.
        :type raw: bool or None
        :return: A dictionary of explanation metadata such as id, data type, explanation method, model type,
            and upload time, sorted by upload time
        :rtype: dict
        """
        module_logger.debug('Listing model explanations')
        assets_client = AssetsClient(self._run.experiment.workspace.service_context)
        explanation_assets = assets_client.get_assets_by_run_id_and_name(self._run.id, History.EXPLANATION_ASSET)
        output_summary = []
        for asset in explanation_assets:
            if comment is not None:
                if History.COMMENT not in asset.meta or asset.meta[History.COMMENT] != comment:
                    continue
            if raw is not None:
                if ExplainType.IS_RAW not in asset.meta or (asset.meta[ExplainType.IS_RAW] == 'true') != raw:
                    continue
            meta_dict = {
                History.ID: asset.meta[History.EXPLANATION_ID] if History.EXPLANATION_ID in asset.meta else None,
                History.COMMENT: asset.meta[History.COMMENT] if History.COMMENT in asset.meta else None,
                ExplainType.DATA: asset.meta[ExplainType.DATA] if ExplainType.DATA in asset.meta else None,
                ExplainType.EXPLAIN: asset.meta[ExplainType.EXPLAIN] if ExplainType.EXPLAIN in asset.meta else None,
                ExplainType.MODEL: asset.meta[ExplainType.MODEL] if ExplainType.MODEL in asset.meta else None,
                ExplainType.IS_RAW: asset.meta[ExplainType.IS_RAW] if ExplainType.IS_RAW in asset.meta else None,
                History.UPLOAD_TIME: asset.created_time
            }
            output_summary.append(meta_dict)
        return sorted(output_summary, key=lambda meta: meta[History.UPLOAD_TIME])

    def _download_sharded_data(self, download_dir, storage_metadata, name, extension, explanation_id=None,
                               top_k=None):
        """Download and aggregate a chunk of data from its sharded storage format.

        :param download_dir: The directory to which the asset's files should be downloaded
        :type download_dir: str
        :param storage_metadata: The metadata dictionary for the asset's stored data
        :type storage_metadata: dict[str: dict[str: Union(str, int)]]
        :param name: The name/data type of the chunk to download_dir
        :type name: str
        :param extension: '.interpret.json' for v5, '.json' for earlier versions.
        :type extension: str
        :param explanation_id: The explanation ID the data is stored under.
            If None, it is assumed that the asset is using an old storage format.
        :type explanation_id: str
        :param top_k: If specified, limit the ordered data returned to the most important features and values
        :type top_k: int
        :return: The data chunk, anything from 1D to 3D, int or str
        """
        num_columns_to_return = int(storage_metadata[name][History.NUM_FEATURES])
        if top_k is not None:
            module_logger.debug('Top k is set, potentially reducing number of columns returned')
            num_columns_to_return = min(top_k, num_columns_to_return)
        num_blocks = int(storage_metadata[name][History.NUM_BLOCKS])
        if BackCompat.OLD_NAME in storage_metadata[name]:
            module_logger.debug('Working with constructed metadata from a v1 asset')
            # Backwards compatibility as of January 2019
            name = storage_metadata[name][BackCompat.OLD_NAME]
        # Backwards compatibility as of February 2019
        connector = '/' if explanation_id is not None else '_'
        artifact = _download_artifact(self._run, download_dir, '{}{}0'.format(name, connector), extension,
                                      explanation_id=explanation_id)
        full_data = np.array(artifact)
        concat_dim = full_data.ndim - 1
        # Get the blocks
        for idx in range(1, num_blocks):
            block_name = '{}{}{}'.format(name, connector, idx)
            block = np.array(_download_artifact(self._run, download_dir, block_name, extension))
            full_data = np.concatenate([full_data, block], axis=concat_dim)
            num_columns_read = full_data.shape[concat_dim]
            if num_columns_read >= num_columns_to_return:
                break
        full_data_list = full_data[..., :num_columns_to_return]
        return full_data_list

    def _download_sharded_data_from_list(self,
                                         data_tuples,
                                         storage_metadata,
                                         download_dir,
                                         extension,
                                         explanation_id=None,
                                         top_k=None):
        """Check each data name in the list.

        If available on the stored explanation, download the sharded chunks and reconstruct the explanation.

        :param data_tuples: A list of data names and dict key names for each kind of data to download
        :type data_tuples: list[(str, str)]
        :param storage_metadata: The metadata dictionary for the asset's stored data
        :type storage_metadata: dict[str: dict[str: Union(str, int)]]
        :param download_dir: The directory to which the asset's files should be downloaded
        :type download_dir: str
        :param extension: '.interpret.json' for v5, '.json' for earlier versions.
        :type extension: str
        :param explanation_id: The explanation ID the data is stored under.
            If None, it is assumed that the asset is using an old storage format.
        :type explanation_id: str
        :param top_k: If specified, limit the ordered data returned to the most important features and values
        :type top_k: int
        :return: A dictionary of the data that was able to be downloaded from run history
        :rtype: dict
        """
        output_kwargs = {}
        for history_name, key_name in data_tuples:
            if history_name in storage_metadata:
                module_logger.debug('Downloading ' + history_name)
                values = self._download_sharded_data(download_dir,
                                                     storage_metadata,
                                                     history_name,
                                                     extension,
                                                     explanation_id=explanation_id,
                                                     top_k=top_k)
                output_kwargs[key_name] = np.array(values)
        return output_kwargs

    def _get_v2_file_dict_from_v1(self, v1_file_dict):
        v1_dict_copy = v1_file_dict.copy()
        names_dict = {
            BackCompat.FEATURE_NAMES: History.FEATURES,
            BackCompat.OVERALL_FEATURE_ORDER: History.GLOBAL_IMPORTANCE_NAMES,
            BackCompat.OVERALL_IMPORTANCE_ORDER: History.GLOBAL_IMPORTANCE_RANK,
            BackCompat.OVERALL_SUMMARY: History.GLOBAL_IMPORTANCE_VALUES,
            BackCompat.PER_CLASS_FEATURE_ORDER: History.PER_CLASS_NAMES,
            BackCompat.PER_CLASS_IMPORTANCE_ORDER: History.PER_CLASS_RANK,
            BackCompat.PER_CLASS_SUMMARY: History.PER_CLASS_VALUES
        }

        for key in v1_dict_copy.keys():
            if key in names_dict:
                v1_file_dict[names_dict[key]] = v1_file_dict[key]

        return v1_file_dict

    def _get_v2_metadata_from_v1(self, v1_metadata):
        """Convert the v1 asset metadata dict to a v2 asset metadata dict.

        :param v1_metadata: a flat dict of v1 metadata
        :type v1_metadta: dict[str: int]
        :return: a rich dict of v2 metadata
        :rtype: dict[str: dict[str: Union(str, int)]]
        """
        storage_metadata = {
            History.GLOBAL_IMPORTANCE_NAMES: self._get_v2_shard_from_v1(v1_metadata,
                                                                        BackCompat.OVERALL_FEATURE_ORDER,
                                                                        History.GLOBAL_IMPORTANCE_NAMES),
            History.GLOBAL_IMPORTANCE_RANK: self._get_v2_shard_from_v1(v1_metadata,
                                                                       BackCompat.OVERALL_IMPORTANCE_ORDER,
                                                                       History.GLOBAL_IMPORTANCE_RANK),
            History.GLOBAL_IMPORTANCE_VALUES: self._get_v2_shard_from_v1(v1_metadata,
                                                                         BackCompat.OVERALL_SUMMARY,
                                                                         History.GLOBAL_IMPORTANCE_VALUES)
        }

        # these fields may or may not exist on v1 assets
        if History.BLOCK_SIZE + '_' + BackCompat.PER_CLASS_FEATURE_ORDER in v1_metadata:
            storage_metadata[History.PER_CLASS_NAMES] = \
                self._get_v2_shard_from_v1(v1_metadata, BackCompat.PER_CLASS_FEATURE_ORDER, History.PER_CLASS_NAMES)
            storage_metadata[History.PER_CLASS_RANK] = \
                self._get_v2_shard_from_v1(v1_metadata, BackCompat.PER_CLASS_IMPORTANCE_ORDER, History.PER_CLASS_RANK)
            storage_metadata[History.PER_CLASS_VALUES] = \
                self._get_v2_shard_from_v1(v1_metadata, BackCompat.PER_CLASS_SUMMARY, History.PER_CLASS_VALUES)
        if History.NUM_CLASSES in v1_metadata:
            class_dict = {
                BackCompat.NAME: History.CLASSES,
                History.NUM_CLASSES: v1_metadata[History.NUM_CLASSES]
            }
            storage_metadata[History.CLASSES] = class_dict
        return storage_metadata

    @staticmethod
    def _get_v2_shard_from_v1(v1_metadata, v1_name, v2_name):
        """Get specific metadata for v2 shards from v1 metadata.

        :param v1_metadata: a flat dict of v1 metadata
        :type v1_metadta: dict[str: int]
        :param v1_name: The v1 name for the chunked data
        :type v1_name: str
        :param v2_name: The v2 name for the chunked data
        :type v2_name: str
        :return: The dict of shard metadata
        :rtype: dict[str: str | int]
        """
        return {
            History.NAME: v2_name,
            BackCompat.OLD_NAME: v1_name,
            History.BLOCK_SIZE: v1_metadata[History.BLOCK_SIZE + '_' + v1_name],
            History.MAX_NUM_BLOCKS: v1_metadata[History.MAX_NUM_BLOCKS + '_' + v1_name],
            History.NUM_BLOCKS: v1_metadata[History.NUM_BLOCKS + '_' + v1_name],
            History.NUM_FEATURES: v1_metadata[History.NUM_FEATURES + '_' + v1_name]
        }

    def _upload_dataset_to_service(self, data, explanation, filename, dataset_suffix):
        """Upload data to the Dataset service.

        :param data: One of the data collections passed into an explainer.
        :type data: All the stuff we support there plus DatasetWrapper.
        :param explanation: An Explanation object.
        :type explanation: Explanation
        :param filename: The name the file should have on disk and in the Datastore.
        :type file: str
        :param dataset_suffix: The end of the dataset name.
        :type dataset_suffix: str
        :return: The ID of the Dataset if it could be uploaded, else None.
        :rtype: str or None
        """
        EXPLAIN_DATASETS_DIR = './explain_model_datasets/'
        DATASTORE_DIR = '{}{}/'.format(EXPLAIN_DATASETS_DIR, explanation.id)

        FILENAME = filename
        FILEPATH = EXPLAIN_DATASETS_DIR + FILENAME
        if data is not None:
            os.makedirs(EXPLAIN_DATASETS_DIR, exist_ok=True)
            with open(FILEPATH, 'w') as f:
                to_dump = data
                if isinstance(to_dump, DatasetWrapper) or isinstance(to_dump, DenseData):
                    to_dump = to_dump.original_dataset
                if isinstance(to_dump, pd.DataFrame):
                    to_dump = to_dump.values.tolist()
                if isinstance(to_dump, np.ndarray):
                    to_dump = to_dump.tolist()
                if sp.sparse.issparse(to_dump):
                    module_logger.warn('Cannot upload a sparse dataset to the Dataset service.')
                    return None
                json.dump(to_dump, f)
            ds = self._run.experiment.workspace.get_default_datastore()
            # local and datastore directories don't have to be the same
            # only the filename is kept from local - if you want directories, must go in target_path
            ds.upload_files([FILEPATH], target_path=DATASTORE_DIR, show_progress=False)
            dataset = Dataset.from_json_files(ds.path('{}{}'.format(DATASTORE_DIR, FILENAME)))
            dataset_obj = dataset.register(self._run.experiment.workspace, explanation.id[:12] + dataset_suffix,
                                           exist_ok=True, update_if_exist=True)
            return dataset_obj.id
        return None
