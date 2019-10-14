# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""mlflow helper functions."""

import logging
import os
import re

from azureml.core.authentication import (ArmTokenAuthentication, AzureMLTokenAuthentication,
                                         InteractiveLoginAuthentication)
from .authentication import DBTokenAuthentication
from azureml._restclient.service_context import ServiceContext

from mlflow.exceptions import MlflowException

from six.moves.urllib import parse

_IS_REMOTE = "is-remote"
_REGION = "region"
_SUB_ID = "sub-id"
_RES_GRP = "res-grp"
_WS_NAME = "ws-name"
_EXP_NAME = "experiment"
_RUN_ID = "runid"
_AUTH_HEAD = "auth"
_AUTH_TYPE = "auth-type"
_TRUE_QUERY_VALUE = "True"

_TOKEN_PREFIX = "Bearer "
_TOKEN_QUERY_NAME = "token"

_ARTIFACT_PATH = "artifact_path"

logger = logging.getLogger(__name__)

_ARTIFACT_URI_EXP_RUN_REGEX = r".*/([^/]+)/runs/([^/]+)(/artifacts.*)?"

_WORKSPACE_INFO_REGEX = r".*/subscriptions/(.+)/resourceGroups/(.+)" \
    r"/providers/Microsoft.MachineLearningServices/workspaces/([^/]+)"

_ARTIFACT_URI_REGEX = _WORKSPACE_INFO_REGEX + r"/experiments/([^/]+)/runs/([^/]+)(/artifacts.*)?"


def tracking_uri_decomp(tracking_uri):
    """
    Parse the tracking URI into a dictionary.

    The tracking URI contains the scope information for the workspace.

    :param tracking_uri: The tracking_uri to parse.
    :type tracking_uri: str
    :return: Dictionary of the parsed workspace information
    :rtype: dict[str, str]
    """

    parsed_url_path = parse.urlparse(tracking_uri).path

    pattern = re.compile(_WORKSPACE_INFO_REGEX)
    mo = pattern.match(parsed_url_path)

    ret = {}
    ret[_SUB_ID] = mo.group(1)
    ret[_RES_GRP] = mo.group(2)
    ret[_WS_NAME] = mo.group(3)

    return ret


def artifact_uri_decomp(tracking_uri):
    """
    Parse the artifact URI into a dictionary.

    The artifact URI contains the scope information for the workspace, the experiment and the run_id.

    :param tracking_uri: The tracking_uri to parse.
    :type tracking_uri: str
    :return: Dictionary of the parsed experiment name, and run id and workspace information if available.
    :rtype: dict[str, str]
    """

    parsed_url_path = parse.urlparse(tracking_uri).path
    ret = {}
    path_match = None
    try:
        mo = re.compile(_ARTIFACT_URI_REGEX).match(parsed_url_path)
        ret[_SUB_ID] = mo.group(1)
        ret[_RES_GRP] = mo.group(2)
        ret[_WS_NAME] = mo.group(3)
        ret[_EXP_NAME] = mo.group(4)
        ret[_RUN_ID] = mo.group(5)
        path_match = mo.group(7)
    except Exception:
        mo = re.compile(_ARTIFACT_URI_EXP_RUN_REGEX).match(parsed_url_path)
        ret[_EXP_NAME] = mo.group(1)
        ret[_RUN_ID] = mo.group(2)
        path_match = mo.group(3)

    if path_match is not None and path_match != "/artifacts":
        path = path_match[len("/artifacts"):]
        ret[_ARTIFACT_PATH] = path if not path.startswith("/") else path[1:]
    return ret


def get_service_context_from_artifact_url(parsed_url):
    parsed_artifacts_path = artifact_uri_decomp(parsed_url.path)
    logger.debug("Creating service context from the artifact uri")
    subscription_id = parsed_artifacts_path[_SUB_ID]
    resource_group_name = parsed_artifacts_path[_RES_GRP]
    workspace_name = parsed_artifacts_path[_WS_NAME]
    queries = dict(parse.parse_qsl(parsed_url.query))
    if _TOKEN_QUERY_NAME not in queries:
        raise MlflowException("An authorization token was not set in the artifact uri")

    auth = AzureMLTokenAuthentication(
        queries[_TOKEN_QUERY_NAME],
        host=parsed_url.netloc,
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name)

    return ServiceContext(subscription_id=subscription_id,
                          resource_group_name=resource_group_name,
                          workspace_name=workspace_name,
                          workspace_id=None,
                          authentication=auth)


def get_service_context_from_tracking_url(parsed_url):
    """Create a Service Context object out of a parsed URL."""
    logger.debug("Creating a Service Context object from the tracking uri")
    parsed_path = tracking_uri_decomp(parsed_url.path)
    subscription_id = parsed_path[_SUB_ID]
    resource_group_name = parsed_path[_RES_GRP]
    workspace_name = parsed_path[_WS_NAME]

    queries = dict(parse.parse_qsl(parsed_url.query))
    from mlflow.tracking.utils import _TRACKING_TOKEN_ENV_VAR
    token = os.environ.get(_TRACKING_TOKEN_ENV_VAR)
    has_auth_info = _AUTH_HEAD in queries or token is not None
    if queries.get(_AUTH_TYPE) == InteractiveLoginAuthentication.__name__ or not has_auth_info:
        logger.debug("Using the default InteractiveLoginAuthentication. "
                     "Auth Type was set to {} and {}".format(queries.get(_AUTH_TYPE),
                                                             "{} token was found in the environment".format(
                                                                 "a" if has_auth_info else "no")))
        auth = InteractiveLoginAuthentication()
    elif queries.get(_AUTH_TYPE) == AzureMLTokenAuthentication.__name__:
        logger.debug("Using AzureMLTokenAuthentication")
        auth = AzureMLTokenAuthentication(
            queries[_AUTH_HEAD],
            host=parsed_url.netloc,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
        )
    elif queries.get(_AUTH_TYPE) == DBTokenAuthentication.__name__:
        logger.debug("Using DBTokenAuthentication")
        auth = DBTokenAuthentication(queries[_AUTH_HEAD])
    else:
        logger.debug("Using ArmTokenAuthentication")
        if token is not None:
            logger.debug("The _TRACKING_TOKEN_ENV_VAR is set.")
        else:
            token = queries[_AUTH_HEAD]
        auth = ArmTokenAuthentication(token)

    return ServiceContext(subscription_id=subscription_id,
                          resource_group_name=resource_group_name,
                          workspace_name=workspace_name,
                          workspace_id=None,
                          authentication=auth)


def get_aml_experiment_name(exp_name):
    """Extract the actual experiment name from the adb experiment name format."""
    regex = "\\/Users\\/(.+)\\/(.+)"
    pattern = re.compile(regex)
    mo = pattern.match(exp_name)
    if mo is not None:
        return mo.group(2)
    else:
        return exp_name


def handle_exception(operation, store, e):
    msg = "Failed to {} from the {} store with exception {}".format(operation, store.__class__.__name__, e)
    raise MlflowException(msg)


def execute_func(func, stores, operation, *args, **kwargs):
    """
    :param func: func to call with store as first param
    :type func: function with store as the first param and inputs to the
        store func as the rest
    :param operation: Identifier for the operation
    :type operation: str
    :param args: arguments for func after store
    :param kwargs: kwargs for func
    :return: list of store returns of func per store
    :rtype: list[< - func]
    """
    store = stores[0]
    try:
        out = func(store, *args, **kwargs)
    except Exception as e:
        handle_exception(operation, store, e)
    for other_store in stores[1:]:
        try:
            func(other_store, *args, **kwargs)
        except Exception as e:
            handle_exception(operation, other_store, e)
    return out
