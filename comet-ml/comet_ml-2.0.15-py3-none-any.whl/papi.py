# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed
#  without the express permission of Comet ML Inc.
# *******************************************************

import logging
import re

from .config import get_config, get_rest_api_key
from .connection import get_rest_api_client
from .exceptions import QueryException
from .experiment import BaseExperiment
from .query import (  # noqa
    Metadata,
    Metric,
    Other,
    Parameter,
    QueryExpression,
    QueryVariable,
    Tag,
)

LOGGER = logging.getLogger(__name__)

__all__ = ["API", "APIExperiment", "Metadata", "Metric", "Other", "Parameter", "Tag"]


class APIExperiment(object):
    """
    The APIExperiment class is used to access data from the
    Comet.ml Python API.

    You can use an instance of the APIExperiment() class to easily
    access all of your logged experiment information
    at [Comet.ml](https://www.comet.ml), including metrics, parameters,
    tags, and assets.

    ```python
    >>> from comet_ml.papi import API, APIExperiment
    >>> comet_api = API(rest_api_key="08ac6a75a2be4d7c9aac2c39e0004f6e")

    ## Get an APIExperiment from the API:
    >>> experiment = comet_api.get("cometpublic/comet-notebooks/example 001")

    ## Make a new APIExperiment (assumes workspace and project_name configured):
    >>> experiment = APIExperiment(rest_api_key="08ac6a75a2be4d7c9aac2c39e0004f6e")

    ## Get an APIExperiment for a previous experiment (assumes workspace and project_name configured):
    >>> experiment = APIExperiment(previous_experiment="example 001")

    ## Get metrics:
    >>> experiment.get_metrics("train_accuracy")
    ```

    For more usage examples, see [Comet Python API examples](../Comet-Python-API/).
    """

    _ATTR_FIELD_MAP = [
        # Standard in json:
        ("id", "experiment_key"),
        ("duration_millis", "duration_millis"),
        ("start_server_timestamp", "start_server_timestamp"),
        ("end_server_timestamp", "end_server_timestamp"),
        ("has_images", "has_images"),
        # Inserted manually:
        ("archived", "archived"),
        ("project_id", "project_id"),
        ("project_name", "project_name"),
        ("workspace", "workspace"),
        # Optional in json:
        ("name", "experimentName"),
        ("code_sha", "code_sha"),
        ("file_name", "file_name"),
        ("file_path", "file_path"),
        ("optimization_id", "optimization_id"),
    ]

    def __init__(self, *args, **kwargs):
        """
        Create a new APIExperiment, or use a previous experiment key
        to access an existing experiment.

        Examples:
        ```python
        # Python API to create a new experiment:
        >>> experiment = APIExperiment([rest_api_key=KEY,]
                                       workspace=WORKSPACE,
                                       project_name=PROJECT)

        # Python API to access an existing experiment:
        >>> experiment = APIExperiment([rest_api_key=KEY,]
                                       previous_experiment=ID,
                                       workspace=WORKSPACE,
                                       project_name=PROJECT)
        ```

        Note: rest_api_key may be defined in environment (COMET_REST_API_KEY)
            or in a .comet.config file. Additional arguments will be
            given to API().
        """
        if "experiment_json" in kwargs:
            # System usage: APIExperiment(api=API, experiment_json=JSON)
            if "api" not in kwargs:
                raise ValueError("need APIExperiment(api=API) for this usage")
            else:
                self._api = kwargs["api"]
            self._set_from_json(kwargs["experiment_json"])
        elif "previous_experiment" in kwargs:
            # Parallel to ExistingExperiment(); APIExperiment(previous_exeriment=KEY)
            # api may be provided
            previous_experiment = kwargs.pop("previous_experiment")
            archived = kwargs.pop("archived", False)
            # To look up the previous_experiment without workspace and project is too expensive!
            workspace = kwargs.pop("workspace", None) or get_config("comet.workspace")
            project_name = kwargs.pop("project_name", None) or get_config(
                "comet.project_name"
            )
            if (workspace is None) or ((project_name is None)):
                raise ValueError(
                    "workspace and project names must be provided for previous_experiment APIExperiments()"
                )
            if "api" in kwargs:
                self._api = kwargs["api"]
            else:
                self._api = API(**kwargs)
            project_json = self._api._get_project_json(
                workspace, project_name, archived=archived
            )
            if project_json is None:
                raise ValueError(
                    "invalid workspace/project: %s/%s" % (workspace, project_name)
                )

            experiment_json = project_json["experiments"][previous_experiment]
            # Fill in missing pieces:
            experiment_json["project_id"] = project_json["project_id"]
            experiment_json["project_name"] = project_json["project_name"]
            experiment_json["workspace"] = project_json["team_name"]
            experiment_json["archived"] = archived
            self._set_from_json(experiment_json)
        else:
            # Parallel to Experiment(); APIExperiment(rest_api_key=KEY, workspace=WS, project_name=PJ)
            # api may be provided
            archived = kwargs.pop("archived", False)
            workspace = kwargs.pop("workspace", None) or get_config("comet.workspace")
            project_name = kwargs.pop("project_name", None) or get_config(
                "comet.project_name"
            )
            if (workspace is None) or ((project_name is None)):
                raise ValueError(
                    "workspace and project names must be provided for new APIExperiments()"
                )
            experiment_name = kwargs.pop("experiment_name", None)
            if "api" in kwargs:
                self._api = kwargs["api"]
            else:
                self._api = API(**kwargs)
            results = self._api._client.create_experiment(
                workspace, project_name, experiment_name
            )
            if self._check_results(results):
                result_json = results.json()
                # Need to get the processed experiment data back from server:
                project_json = self._api._get_project_json(
                    workspace, project_name, archived=archived
                )
                if project_json is None:
                    raise ValueError(
                        "invalid workspace/project: %s/%s" % (workspace, project_name)
                    )

                experiment_json = project_json["experiments"][
                    result_json["experimentKey"]
                ]
                # Fill in missing parts:
                experiment_json["project_id"] = project_json["project_id"]
                experiment_json["project_name"] = project_name
                experiment_json["workspace"] = workspace
                experiment_json["archived"] = archived
                self._set_from_json(experiment_json)

    def _check_results(self, results):
        return self._api._check_results(results)

    @property
    def url(self):
        """
        Get the url of the experiment.
        """
        return self._get_experiment_url()

    ## Just steal these two methods for now:
    _in_jupyter_environment = BaseExperiment._in_jupyter_environment
    display = BaseExperiment.display

    def end(self):
        """
        Method called at end of processing. This method in APIExperiment()
        doesn't actually do anything and is only provided to be analogous
        to Experiment, and OfflineExperiment.
        """
        # for compatibility with other Experiments
        pass

    def __repr__(self):
        return "<APIExperiment '%s/%s/%s'>" % (
            self.workspace,
            self.project_name,
            self.name if self.name else self.id,
        )

    def _set_from_json(self, experiment_json):
        # Set to the given value, or None
        for (attr, item) in self._ATTR_FIELD_MAP:
            setattr(
                self, attr, (experiment_json[item] if item in experiment_json else None)
            )

    def _update_from_json(self, experiment_json):
        # Set to the given value if given:
        for (attr, item) in self._ATTR_FIELD_MAP:
            if item in experiment_json:
                setattr(self, attr, experiment_json[item])

    def _get_experiment_url(self):
        if self.archived:
            return "/".join(
                [
                    self._api._get_url_server(),
                    self.workspace,
                    self.project_name,
                    "archived",
                    self.id,
                ]
            )
        else:
            return "/".join(
                [
                    self._api._get_url_server(),
                    self.workspace,
                    self.project_name,
                    self.id,
                ]
            )

    def to_json(self, full=False):
        """
        The experiment data in JSON-like format.
        """
        # Without further net access, full=False:
        retval = {
            "id": self.id,
            "name": self.name,
            "workspace": self.workspace,
            "project_name": self.project_name,
            "project_id": self.project_id,
            "archived": self.archived,
            "url": self.url,
            "code_sha": self.code_sha,
            "duration_millis": self.duration_millis,
            "start_server_timestamp": self.start_server_timestamp,
            "end_server_timestamp": self.end_server_timestamp,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "has_images": self.has_images,
            "optimization_id": self.optimization_id,
        }
        # Everything else, except individual assets, full=True:
        if full:
            retval.update(
                {
                    "asset_list": self.get_asset_list(),
                    "code": self.get_code(),
                    "environment_details": self.get_environment_details(),
                    "git_metadata": self.get_git_metadata(),
                    "git_patch": self.get_git_patch(),
                    "html": self.get_html(),
                    "installed_packages": self.get_installed_packages(),
                    "metrics": self.get_metrics(),
                    "metrics_summary": self.get_metrics_summary(),
                    "model_graph": self.get_model_graph(),
                    "os_packages": self.get_os_packages(),
                    "others_summary": self.get_others_summary(),
                    "output": self.get_output(),
                    "parameters_summary": self.get_parameters_summary(),
                    "system_details": self.get_system_details(),
                    "tags": self.get_tags(),
                }
            )
        return retval

    # Read methods:

    def get_html(self):
        """
        Get the HTML associated with this experiment.
        """
        results = self._api._client.get_experiment_html(self.id)
        if results:
            return results["html"]

    def get_code(self):
        """
        Get the associated source code for this experiment.
        """
        results = self._api._client.get_experiment_code(self.id)
        if results:
            return results["code"]

    def get_output(self):
        """
        Get the associated standard output for this experiment.
        """
        results = self._api._client.get_experiment_output(self.id)
        if results:
            return results["output"]

    def get_installed_packages(self):
        """
        Get the associated installed packages for this experiment.
        """
        results = self._api._client.get_experiment_installed_packages(self.id)
        if results:
            return results["packages"]

    def get_environment_details(self):
        """
        Return the list of installed OS packages at the
        time an experiment was run.
        """
        results = self._api._client.get_experiment_environment_details(self.id)
        if results:
            return results["envDetails"]

    def get_os_packages(self):
        """
        Get the associated installed packages for this experiment.
        """
        results = self._api._client.get_experiment_os_packages(self.id)
        return results

    def get_model_graph(self):
        """
        Get the associated graph/model description for this
        experiment.
        """
        results = self._api._client.get_experiment_model_graph(self.id)
        if results:
            return results["graph"]

    def get_tags(self):
        """
        Get the associated tags for this experiment.
        """
        results = self._api._client.get_experiment_tags(self.id)
        if results:
            return results["tags"]

    def get_parameters_summary(self, parameter=None):
        """
        Return the experiment parameters summary.  Optionally, also if you
        provide a parameter name, the method will only return the
        summary of the given parameter.

        Args:
            parameter: optional (string), name of a parameter

        Examples:

        ```python
        >>> from comet_ml.papi import API
        >>> comet_api = API()
        >>> x = comet_api.get("myworkspace/project1/experiment_key")
        >>> x.get_parameters_summary()
        [{'name': 'batch_size',
          'valueMax': '120',
          'valueMin': '120',
          'valueCurrent': '120',
          'timestampMax': 1558962363411,
          'timestampMin': 1558962363411,
          'timestampCurrent': 1558962363411},
         ...]

        >>> x.get_parameters_summary("batch_size")
        {'name': 'batch_size',
         'valueMax': '120',
         'valueMin': '120',
         'valueCurrent': '120',
         'timestampMax': 1558962363411,
         'timestampMin': 1558962363411,
         'timestampCurrent': 1558962363411}
        ```
        """
        results = self._api._client.get_experiment_parameters_summaries(self.id)
        if results:
            if parameter is not None:
                retval = [p for p in results["results"] if p["name"] == parameter]
                if retval:
                    return retval[0]
                else:
                    return []
            else:
                return results["results"]
        else:
            return []

    def get_metrics_summary(self, metric=None):
        """
        Return the experiment metrics summary.  Optionally, also if you
        provide the metric name, the function will only return the
        summary of the metric.

        Args:
            metric: optional (string), name of a metric

        Examples:

        ```python
        >>> from comet_ml.papi import API
        >>> comet_api = API()
        >>> x = comet_api.get("myworkspace/project1/experiment_key")
        >>> x.get_metrics_summary()
        [{'name': 'val_loss',
          'valueMax': '0.24951280827820302',
          'valueMin': '0.13101346811652184',
          'valueCurrent': '0.13101346811652184',
          'timestampMax': 1558962367938,
          'timestampMin': 1558962367938,
          'timestampCurrent': 1558962376383,
          'stepMax': 500,
          'stepMin': 1500,
          'stepCurrent': 1500},
         ...]

        >>> comet_api.get_metrics_summary("val_loss")
        {'name': 'val_loss',
         'valueMax': '0.24951280827820302',
         'valueMin': '0.13101346811652184',
         'valueCurrent': '0.13101346811652184',
         'timestampMax': 1558962367938,
         'timestampMin': 1558962367938,
         'timestampCurrent': 1558962376383,
         'stepMax': 500,
         'stepMin': 1500,
         'stepCurrent': 1500}
        ```
        """
        results = self._api._client.get_experiment_metrics_summaries(self.id)
        if results:
            if metric is not None:
                retval = [m for m in results["results"] if m["name"] == metric]
                if retval:
                    return retval[0]
                else:
                    return []
            else:
                return results["results"]
        else:
            return []

    def get_others_summary(self, other=None):
        """
        Get the other items logged in summary form.

        Args:
            other: optional, string, the name of the other item
                logged. If given, return the valueCurrent of
                the other item. Otherwise, return all other
                items logged.

        Examples:

        ```python
        >>> from comet_ml.papi import API
        >>> comet_api = API()
        >>> x = comet_api.get("myworkspace/project1/experiment_key")
        >>> x.get_others_summary()
        [{'name': 'trainable_params',
          'valueMax': '712723',
          'valueMin': '712723',
          'valueCurrent': '712723',
          'timestampMax': 1558962363411,
          'timestampMin': 1558962363411,
          'timestampCurrent': 1558962363411},
         ...]

        >>> x.get_others_summary("trainable_params")
        ['712723']
        ```
        """
        results = self._api._client.get_experiment_others_summaries(self.id)
        if results:
            if other is not None:
                retval = [
                    m["valueCurrent"]
                    for m in results["logOtherList"]
                    if m["name"] == other
                ]
                return retval
            else:
                return results["logOtherList"]
        else:
            return []

    def get_metrics(self, metric=None):
        """
        Get all of the logged metrics. Optionally, just get the given metric name.

        Args:
            metric: Optional. String. If given, filter the metrics by name.

        Examples:

        ```python
        >>> from comet_ml.papi import API
        >>> comet_api = API()
        >>> x = comet_api.get("myworkspace/project1/experiment_key")
        >>> x.get_metrics()
        [{'metricName': 'val_loss',
          'metricValue': '0.13101346811652184',
          'timestamp': 1558962376383,
          'step': 1500,
          'epoch': None,
          'runContext': None},
         {'metricName': 'acc',
          'metricValue': '0.876',
          'timestamp': 1564536453647,
          'step': 100,
          'epoch': None,
          'runContext': None},
         ...]

        >>> x.get_metrics("acc")
        [{'metricName': 'acc',
          'metricValue': '0.876',
          'timestamp': 1564536453647,
          'step': 100,
          'epoch': None,
          'runContext': None},
         ...]
        ```
        """
        results = self._api._client.get_experiment_metrics(self.id)
        if results:
            if metric is not None:
                retval = [m for m in results["metrics"] if m["metricName"] == metric]
            else:
                retval = results["metrics"]
            return retval
        else:
            return []

    def get_asset_list(self, asset_type="all"):
        """
        Get a list of assets associated with the experiment.

        Args:
            asset_type: Option String, type of asset to return. Can be
                "all", "image", "histogram_combined_3d", "video", or "audio".

        Returns a list of dictionaries of asset properties, like:

        ```python
        >>> from comet_ml.papi import API
        >>> comet_api = API()
        >>> x = comet_api.get("myworkspace/project1/experiment_key")
        >>> x.get_asset_list()
        [{'fileName': 'My Filename.png',
          'fileSize': 21113,
          'runContext': None,
          'step': None,
          'link': 'https://www.comet.ml/api/asset/download?experimentKey=KEY&assetId=ASSET_ID',
          'createdAt': 1565898755830,
          'dir': 'assets',
          'canView': False,
          'audio': False,
          'video': False,
          'histogram': False,
          'image': True,
          'type': 'image',
          'metadata': None,
          'assetId': ASSET_ID}, ...]

        >>> x.get_asset_list("image")
        [{'fileName': 'My Filename.png',
          'fileSize': 21113,
          'runContext': None,
          'step': None,
          'link': 'https://www.comet.ml/api/asset/download?experimentKey=KEY&assetId=ASSET_ID',
          'createdAt': 1565898755830,
          'dir': 'assets',
          'canView': False,
          'audio': False,
          'video': False,
          'histogram': False,
          'image': True,
          'type': 'image',
          'metadata': None,
          'assetId': ASSET_ID}, ...]
        ```
        """
        results = self._api._client.get_experiment_asset_list(self.id, asset_type)
        # results is the list directly
        return results

    def get_asset(self, asset_id, return_type="binary"):
        """
        Get an asset, given the asset_id.

        Args:
            asset_id: the asset ID
            return_type: the type of object returned. Default is
                "binary". Options: "binary" or "text"
        """
        results = self._api._client.get_experiment_asset(
            self.id, asset_id, return_type=return_type
        )
        # Return directly
        return results

    def get_system_details(self):
        """
        Get the system details associated with this experiment.
        """
        results = self._api._client.get_experiment_system_details(self.id)
        # Return directly
        return results

    def get_git_patch(self):
        """
        Get the git-patch associated with this experiment.
        """
        results = self._api._client.get_experiment_git_patch(self.id)
        # Return directly
        return results

    def get_git_metadata(self):
        """
        Get the git-metadata associated with this experiment.
        """
        results = self._api._client.get_experiment_git_metadata(self.id)
        # Return directly
        return results

    # Write methods:

    def create_symlink(self, project_name):
        """
        Create a copy of this experiment in another project
        in the workspace.
        """
        results = self._api._client.create_experiment_symlink(self.id, project_name)
        if self._check_results(results):
            return results.json()

    def set_code(self, code):
        """
        Set the code for this experiment.
        """
        results = self._api._client.set_experiment_code(self.id, code)
        if self._check_results(results):
            return results.json()

    def set_model_graph(self, graph):
        """
        Set the model graph for this experiment.
        """
        results = self._api._client.set_experiment_model_graph(self.id, str(graph))
        if self._check_results(results):
            return results.json()

    def set_os_packages(self, os_packages):
        """
        Set the OS packages for this experiment.
        """
        results = self._api._client.set_experiment_os_packages(self.id, os_packages)
        if self._check_results(results):
            return results.json()

    def update_status(self):
        """
        Update the status for this experiment. Sends the keep-alive
        status for it in the UI.
        """
        results = self._api._client.update_experiment_status(self.id)
        if self._check_results(results):
            return results.json()

    def set_start_time(self, start_server_timestamp):
        """
        Set the start time of an experiment.

        Note: time is in milliseconds.
        """
        results = self._api._client.set_experiment_start_end(
            self.id, start_server_timestamp, None
        )
        if self._check_results(results):
            exps = self._api._client.get_experiment_jsons_from_project_id(
                self.project_id, archived=self.archived
            )["experiments"]
            experiment_json = [
                ejson
                # Get the low-level experiment json:
                for ejson in exps
                if ejson["experiment_key"] == self.id
            ][0]
            self._update_from_json(experiment_json)
            return results.json()

    def set_end_time(self, end_server_timestamp):
        """
        Set the start/end time of an experiment.

        Note: times are in milliseconds.
        """
        results = self._api._client.set_experiment_start_end(
            self.id, None, end_server_timestamp
        )
        if self._check_results(results):
            exps = self._api._client.get_experiment_jsons_from_project_id(
                self.project_id, archived=self.archived
            )["experiments"]
            experiment_json = [
                ejson
                # Get the low-level experiment json:
                for ejson in exps
                if ejson["experiment_key"] == self.id
            ][0]
            self._update_from_json(experiment_json)
            return results.json()

    def log_output(self, lines, context=None, stderr=False, timestamp=None):
        """
        Log output line(s).
        """
        results = self._api._client.log_experiment_output(
            self.id, lines, context, stderr, timestamp
        )
        if self._check_results(results):
            return results.json()

    def log_other(self, key, value, timestamp=None):
        """
        Set an other key/value pair for an experiment.
        """
        results = self._api._client.log_experiment_other(self.id, key, value, timestamp)
        if self._check_results(results):
            return results.json()

    def log_parameter(self, parameter, value, step=None, timestamp=None):
        """
        Set a parameter name/value pair for an experiment.
        """
        results = self._api._client.log_experiment_parameter(
            self.id, parameter, value, step, timestamp
        )
        if self._check_results(results):
            return results.json()

    def log_metric(self, metric, value, step=None, timestamp=None):
        """
        Set a metric name/value pair for an experiment.
        """
        results = self._api._client.log_experiment_metric(
            self.id, metric, value, step, timestamp
        )
        if self._check_results(results):
            return results.json()

    def log_html(self, html, overwrite=False, timestamp=None):
        """
        Set, or append onto, an experiment's HTML.
        """
        results = self._api._client.log_experiment_html(
            self.id, html, overwrite, timestamp
        )
        if self._check_results(results):
            return results.json()

    def add_tags(self, tags):
        """
        Append onto an experiment's list of tags.
        """
        results = self._api._client.add_experiment_tags(self.id, tags)
        return results.json()

    def log_asset(self, filename, step=None, overwrite=None, context=None):
        """
        Upload an asset to an experiment.
        """
        results = self._api._client.log_experiment_asset(
            self.id, filename, step, overwrite, context
        )
        if self._check_results(results):
            # Don't turn this into json
            return results.json()

    def log_image(
        self, filename, image_name=None, step=None, overwrite=None, context=None
    ):
        """
        Upload an image asset to an experiment.
        """
        results = self._api._client.log_experiment_image(
            self.id, filename, image_name, step, overwrite, context
        )
        if self._check_results(results):
            self.has_images = True
            # Don't turn this into json
            return results.json()


class API(object):
    """
    The API class is used as a Python interface to the Comet.ml Python
    API.

    You can use an instance of the API() class to quickly and easily
    access all of your logged information at [comet.ml](https://comet.ml),
    including metrics, parameters, tags, and assets.

    Example calls to get workspace, project, and experiment data:

    * API.get(): gets all of your personal workspaces
    * API.get(WORKSPACE): gets all of your projects from WORKSPACE
    * API.get(WORKSPACE, PROJECT_NAME): get all APIExperiments in WORKSPACE/PROJECT
    * API.get_experiment(WORKSPACE, PROJECT_NAME, EXPERIMENT_ID): get an APIExperiment
    * API.get_experiments(WORKSPACE): (generator) get all APIExperiments in WORKSPACE
    * API.get_experiments(WORKSPACE, PROJECT_NAME): (generator) get all APIExperiments in WORKSPACE/PROJECT
    * API.get_experiments(WORKSPACE, PROJECT_NAME, PATTERN): (generator) get all APIExperiments in WORKSPACE/PROJECT/PATTERN

    Examples:
    ```python
    >>> import comet_ml
    >>> comet_api = comet_ml.papi.API()

    ## Return all of my workspace names in a list:
    >>> comet_api.get()

    ## Get an APIExperiment:
    >>>  experiment = comet_api.get("cometpublic/comet-notebooks/example 001")

    ## Get metrics:
    >>> experiment.get_metrics("train_accuracy")
    ```

    The API instance also gives you access to the low-level Python API function
    calls:

    ```python
    >>> comet_api.delete_experiment(experiment_key)
    ```

    For more usage examples, see [Comet Python API examples](../Comet-Python-API/).
    """

    def __init__(self, rest_api_key=None, cache=True, version="v1"):
        """
        Application Programming Interface to the Comet Python interface.

        Args:
            rest_api_key: Optional. Your private COMET_REST_API_KEY.
            cache: Bool, whether to cache on values or not.
            version: Optional. The version of the REST API to use.

        Note: rest_api_key may be defined in environment (COMET_REST_API_KEY)
            or in a .comet.config file.

        Example:
        ```python
        >>> from comet_ml.papi import API
        >>> comet_api = API(rest_api_key="08ac6a75a2be4d7c9aac2c39e0004f6e")
        >>> comet_api.get("my-workspace")
        ['project1', 'project2', ...]
        ```
        """
        config = get_config()
        rest_api_key = get_rest_api_key(rest_api_key, config)
        self._client = get_rest_api_client(
            version, rest_api_key=rest_api_key, comet_api_key=None, use_cache=cache
        )

    def _check_results(self, results):
        return results is not None

    def update_cache(self):
        """
        Used when cache is on, but you have added/changed
        data outside of this API instance.

        Note: you could also just start with no cache.

        ```python
        >>> api = API(cache=False)
        ```

        Or, if you had started with cache, turn it off:

        ```python
        >>> api = API(cache=True)
        >>> api.use_cache = False
        ```
        """
        self._client.reset()

    def get(self, workspace=None, project_name=None, experiment=None):
        """
        Get the following items:

        * list of workspace names, given no arguments
        * list of project names, given a workspace name
        * list of experiment names/keys, given workspace and project names
        * an experiment, given workspace, project, and experiemnt name/key

        `workspace`, `project_name`, and `experiment` can also be given as a single
        string, delimited with a slash.
        """
        ## First, we check for delimiters:
        if workspace is not None and "/" in workspace:
            if project_name is not None:
                raise SyntaxError(
                    "Can't use slash format in workspace name "
                    + "and provide project name"
                )
            workspace, project_name = workspace.split("/", 1)
        if project_name is not None and "/" in project_name:
            if experiment is not None:
                raise SyntaxError(
                    "Can't use slash format in project name "
                    + "and provide experiment key/name"
                )
            project_name, experiment = project_name.split("/", 1)
        ## Now, return the appropriate item:
        if workspace is None:
            return self.get_workspaces()
        elif project_name is None:
            return self.get_projects(workspace)
        elif experiment is None:
            return self.get_experiments(workspace, project_name)
        else:
            return self.get_experiment(workspace, project_name, experiment)

    def query(self, workspace, project_name, query, archived=False):
        """
        Perform a query on a workspace/project to find matching
        APIExperiment. Queries are composed of

        Args:
            workspace: String, the name of the workspace
            project_name: String, the name of the project
            query: a query expression (see below)
            archived: (optional boolean), query the archived experiments if True

        ```python
        ((QUERY-VARIABLE OPERATOR VALUE) & ...)

        # or:

        (QUERY-VARIABLE.METHOD(VALUE) & ...)
        ```

        where:

        `QUERY-VARIABLE` is `Metric(NAME)`, `Parameter(NAME)`, `Other(NAME)`,
        `Metadata(NAME)`, or `Tag(VALUE)`.

        `OPERATOR` is any of the standard mathematical operators
        `==`, `<=`, `>=`, `!=`, `<`, `>`.

        `METHOD` is `between()`, `contains()`, `startswith()`, or `endswith()`.

        You may also place the bitwise `~` not operator in front of an expression
        which means to invert the expression. Use `&` to combine additional
        criteria. Currently, `|` (bitwise or) is not supported.

        `VALUE` can be any query type, includeing `string`, `boolean`, `double`,
        `datetime`, or `timenumber` (number of seconds). `None` and `""` are special
        values that mean `NULL` and `EMPTY`, respectively. Use
        `API.get_query_variables(WORKSPACE, PROJECT_NAME)` to see query variables
        and types for a project.

        When using `datetime`, be aware that the backend is using UTC datetimes. If you
        do not receive the correct experiments via a datetime query, please check with
        the web UI query builder to verify timezone of the server.

        `query()` returns a list of matching `APIExperiments()`.

        Examples:

        ```python
        # Find all experiments that have an acc metric value > .98:
        >>> api.query("workspace", "project", Metric("acc") > .98)
        [APIExperiment(), ...]

        # Find all experiments that have a loss metric < .1 and
        # a learning_rate parameter value >= 0.3:
        >>> loss = Metric("loss")
        >>> lr = Parameter("learning_rate")
        >>> query = ((loss < .1) & (lr >= 0.3))
        >>> api.query("workspace", "project", query)
        [APIExperiment(), ...]

        # Find all of the experiments tagged "My simple tag":
        >>> tagged = Metric("My simple tag")
        >>> api.query("workspace", "project", tagged)
        [APIExperiment(), ...]

        # Find all experiments started before Sept 24, 2019 at 5:00am:
        >>> q = Metadata("start_server_timestamp") < datetime(2019, 9, 24, 5)
        >>> api.query("workspace", "project", q)
        [APIExperiment(), ...]

        # Find all experiments lasting more that 2 minutes (in seconds):
        >>> q = Metadata("duration") > (2 * 60)
        >>> api.query("workspace", "project", q)
        [APIExperiment(), ...]
        ```

        Notes:

        * Use `~` for `not` on any expression
        * Use `~QUERY-VARIABLE.between(2,3)` for values not between 2 and 3
        * Use `(QUERY-VARIABLE == True)` for truth
        * Use `(QUERY-VARIABLE == False)` for not true
        * Use `(QUERY-VARIABLE == None)` for testing null
        * Use `(QUERY-VARIABLE != None)` or `~(QUERY-VARIABLE == None)` for testing not null
        * Use `(QUERY-VARIABLE == "")` for testing empty
        * Use `(QUERY-VARIABLE != "")` or `~(QUERY-VARIABLE == "")` for testing not empty
        * Use Python's datetime(YEAR, MONTH, DAY, HOUR, MINUTE, SECONDS) for comparing datetimes, like
            `Metadata("start_server_timestamp")` or `Metadata("end_server_timestamp")`
        * Use seconds for comparing timenumbers, like `Metadata("duration")`
        * Use `API.get_query_variables(WORKSPACE, PROJECT_NAME)` to see query variables
            and types.

        Do not use 'and', 'or', 'not', 'is', or 'in'. These
        are logical operators and you must use mathematical
        operators for queries. For example, always use '=='
        where you might usually use 'is'.
        """
        project_json = self._get_project_json(workspace, project_name)
        if project_json is None:
            raise ValueError(
                "invalid workspace/project: %s/%s" % (workspace, project_name)
            )

        project_id = project_json["project_id"]
        columns = self._client.get_project_columns(project_id)
        print("COLUMNS", columns)
        if isinstance(query, QueryVariable):
            raise Exception(
                "invalid query expression: you must use an operator, such as '==' or QueryVariable.contains('substring')"
            )
        if not isinstance(query, QueryExpression):
            raise Exception(
                "invalid query expression: do not use 'and', 'or', 'not', 'is', or 'in'"
            )

        try:
            predicates = query.get_predicates(columns)
        except QueryException as exc:
            LOGGER.info(str(exc) + "; ignoring query, returning no matches")
            return []
        results = self._client.query_project(project_id, predicates, archived)
        if results:
            results_json = results.json()
            return [
                self._get_experiment(
                    workspace, project_name, key, archived, project_json
                )
                for key in results_json["experimentKeys"]
            ]

    def get_archived_experiment(self, workspace, project_name, experiment):
        """
        Get a single archived APIExperiment by workspace, project, experiment.
        """
        return self._get_experiment(workspace, project_name, experiment, archived=True)

    def get_experiment(self, workspace, project_name, experiment):
        """
        Get a single APIExperiment by workspace, project, experiment.
        """
        return self._get_experiment(workspace, project_name, experiment, archived=False)

    def get_archived_experiments(self, workspace, project_name=None, pattern=None):
        """
        Get archived APIExperiments by workspace, workspace + project, or
        workspace + project + regular expression pattern.
        """
        return list(
            self._gen_experiments(workspace, project_name, pattern, archived=True)
        )

    def get_experiments(self, workspace, project_name=None, pattern=None):
        """
        Get APIExperiments by workspace, workspace + project, or
        workspace + project + regular expression pattern.
        """
        return list(
            self._gen_experiments(workspace, project_name, pattern, archived=False)
        )

    def gen_experiments(self, workspace, project_name=None, pattern=None):
        """
        Get APIExperiments by workspace, workspace + project, or
        workspace + project + regular expression pattern.
        """
        return self._gen_experiments(workspace, project_name, pattern, archived=False)

    # Private methods:

    def _get_experiment(
        self, workspace, project_name, experiment, archived, project_json=None
    ):
        if project_json is None:
            project_json = self._get_project_json(workspace, project_name)
        if project_json is None:
            return None

        project_id = project_json["project_id"]
        exps = project_json["experiments"]
        if experiment in exps:
            experiment_json = exps[experiment]
            experiment_json["project_id"] = project_id
            experiment_json["project_name"] = project_name
            experiment_json["workspace"] = workspace
            experiment_json["archived"] = archived
            return APIExperiment(api=self, experiment_json=experiment_json)

    def _gen_experiments(
        self, workspace, project_name=None, pattern=None, archived=False
    ):
        if project_name is None:
            if pattern is not None:
                raise ValueError("Must provide project_name when providing pattern")
            # Return all experiments in a workspace:
            for project_name in self.get_projects(workspace):
                for exp in self._gen_experiments(
                    workspace, project_name, archived=archived
                ):
                    yield exp
            return
        elif pattern is None:
            project_json = self._get_project_json(
                workspace, project_name, include_names=False, archived=archived
            )
            if project_json is None:
                raise ValueError(
                    "invalid workspace/project: %s/%s" % (workspace, project_name)
                )

            project_id = project_json["project_id"]
            for exp_json in project_json["experiments"].values():
                exp_json["project_id"] = project_id
                exp_json["project_name"] = project_name
                exp_json["workspace"] = workspace
                exp_json["archived"] = archived
                yield APIExperiment(api=self, experiment_json=exp_json)
            return
        else:
            project_json = self._get_project_json(
                workspace, project_name, include_names=False, archived=archived
            )
            if project_json is None:
                raise ValueError(
                    "invalid workspace/project: %s/%s" % (workspace, project_name)
                )

            for api_exp in project_json["experiments"].values():
                if re.match(pattern, api_exp["experiment_key"]) or (
                    "experimentName" in api_exp
                    and api_exp["experimentName"] is not None
                    and re.match(pattern, api_exp["experimentName"])
                ):
                    api_exp["project_name"] = project_name
                    api_exp["project_id"] = project_json["project_id"]
                    api_exp["workspace"] = workspace
                    api_exp["archived"] = archived
                    yield APIExperiment(api=self, experiment_json=api_exp)
            return

    def _get_project_json(
        self, workspace, project_name, include_names=True, archived=False
    ):
        # Get the project details:
        project_json = self._client.get_project_json(workspace, project_name)
        if project_json is None:
            return
        # Get the experiment details:
        exp_jsons = self._client.get_experiment_jsons_from_project_id(
            project_json["project_id"], archived=archived
        )
        exps_by_key = {
            exp_json["experiment_key"]: exp_json
            for exp_json in exp_jsons["experiments"]
        }
        exps = {}
        exps.update(exps_by_key)
        if include_names:
            exps_by_name = {
                exp_json["experimentName"]: exp_json
                for exp_json in exp_jsons["experiments"]
                if "experimentName" in exp_json
            }
            exps.update(exps_by_name)
        project_json["experiments"] = exps
        return project_json

    def _get_experiment_keys(self, project_id, archived=False):
        """
        Get the experiment_keys given a project id.
        """
        return self._client.get_keys_from_project_id(project_id, archived)

    def _get_url_server(self, version=None):
        """
        Returns the URL server for this version of the API.
        """
        return self._client.server_url

    def _create_experiment(
        self, workspace, project_name="general", experiment_name=None
    ):
        """
        Create an experiment and return its associated APIExperiment.
        """
        return APIExperiment(
            api=self,
            workspace=workspace,
            project_name=project_name,
            experiment_name=experiment_name,
        )

    ## ---------------------------------------------------------
    # Public Read Methods
    ## ---------------------------------------------------------

    def get_workspaces(self):
        """
        Return a list of names of the workspaces for this user.
        """
        results = self._client.get_workspaces()
        if self._check_results(results):
            return results["workspaces"]

    def get_projects(self, workspace):
        """
        Return the ids of the projects in a workspace.

        Args:
            workspace: String, the name of the workspace
            project_name: String, the name of the project

        Returns a list of project names in workspace.
        """
        # Lower call does not get experiments:
        results = self._client.get_project_jsons(workspace)
        if self._check_results(results):
            return [
                project_name["project_name"] for project_name in results["projects"]
            ]

    def get_query_variables(self, workspace, project_name):
        """
        Return the query variables of a project in a workspace. Used
        with `API.query()`.

        Args:
            workspace: String, the name of the workspace
            project_name: String, the name of the project

        Returns a list of QueryVariables, like:

        ```python
        [Metadata('user_name'),
         Metadata('start_server_timestamp'),
         ...]
        ```
        """
        project_json = self._get_project_json(workspace, project_name)
        if project_json is None:
            raise ValueError(
                "invalid workspace/project: %s/%s" % (workspace, project_name)
            )

        project_id = project_json["project_id"]
        columns = self._client.get_project_columns(project_id)
        if columns:
            return [self._make_query_var(column) for column in columns["columns"]]
        else:
            return []

    def _make_query_var(self, column):
        if column["source"] == "metadata":
            return Metadata(column["name"], qtype=column["type"])
        elif column["source"] == "metrics":
            return Metric(column["name"], qtype=column["type"])
        elif column["source"] == "log_other":
            return Other(column["name"], qtype=column["type"])
        elif column["source"] == "params":
            return Parameter(column["name"], qtype=column["type"])
        elif column["source"] == "tag":
            return Tag(column["name"])
        else:
            raise Exception("unknown query variable type: %r" % column["source"])

    ## ---------------------------------------------------------
    # Public Write Methods
    ## ---------------------------------------------------------

    def delete_experiment(self, experiment_key):
        """
        Delete one experiment.
        """
        results = self._client.delete_experiment(experiment_key)
        return results

    def delete_experiments(self, experiment_keys):
        """
        Delete list of experiments.
        """
        results = self._client.delete_experiments(experiment_keys)
        return results

    def archive_experiment(self, experiment_key):
        """
        Archive one experiment.
        """
        results = self._client.archive_experiment(experiment_key)
        return results

    def archive_experiments(self, experiment_keys):
        """
        Archive list of experiments.
        """
        results = self._client.archive_experiments(experiment_keys)
        return results

    def get_metrics_for_chart(
        self, experiment_keys, metrics, independent=True, full=False
    ):
        """
        Get multiple metrics from a set of experiments. This method
        is designed to make custom charting easier.

        Args:
            experiment_keys: a list of experiment keys
            metrics: a list of metric names (e.g., "loss")
            independent: Bool, get independent results?
            full: Bool, fetch the full result?

        Returns: a dictionary of experiment keys with the following
        structure:

        ```python
        >>> from comet_ml.papi import API
        >>> comet_api = API()
        >>> comet_api.get_metrics_for_chart([experiment_key1, experiment_key2, ...],
                                            ["loss"])
        {EXPERIMENT_KEY: {
           'experiment_key': EXPERIMENT_KEY,
           'steps': STEPS,
           'epochs': None,
           'metrics': [
              {'metricName': 'loss',
               'values': [VALUE, ...],
               'steps': [STEP, ...],
               'epochs': [EPOCH, ...],
               'timestamps': [TIMESTAMP, ...],
               'durations': [DURATION, ...],
              }]
        }, ...}
        ```
        """
        results = self._client.get_experiment_multi_metrics(
            experiment_keys, metrics, independent, full
        )
        if self._check_results(results):
            results_json = results.json()
            # Also: results_json["empty"] indicates results_json["experiments"] or not
            return results_json["experiments"]
        else:
            return []

    def do_cache(self, *endpoints):
        """
        Cache the given endpoints.

        Example:

        ```python
        >>> from comet_ml.papi import API
        >>> comet_api = API()
        >>> comet_api.do_cache("experiments", "projects")
        ```
        """
        self._client.do_cache(*endpoints)

    def do_not_cache(self, *endpoints):
        """
        Do not cache the given endpoints.

        Example:

        ```python
        >>> from comet_ml.papi import API
        >>> comet_api = API()
        >>> comet_api.do_not_cache("experiments", "projects")
        ```
        """
        self._client.do_not_cache(*endpoints)
