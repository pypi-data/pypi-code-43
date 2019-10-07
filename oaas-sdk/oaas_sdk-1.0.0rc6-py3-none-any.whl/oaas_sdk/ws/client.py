"""
Low-level interface with Webservice. Should not be used directly, instead, use the abstraction available in the `oaas_sdk.sdk` module.
"""
import pandas as pd
import pyarrow as pa
import requests
from requests import HTTPError
from typing import Iterable, Optional, Union, Set, List

from oaas_sdk.objects import UnknownLabelingTask, ResultNotReady
from oaas_sdk.util import configuration
from oaas_sdk.objects import WebServiceException

MAX_RETRIES = 4


def _raise_custom_exception_for_status(r):
    http_error_msg = None
    if 400 <= r.status_code < 500:
        http_error_msg = u'%s Client Error: %s for url: %s' % (r.status_code, r.reason, r.url)

    elif 500 <= r.status_code < 600:
        http_error_msg = u'%s Server Error: %s for url: %s' % (r.status_code, r.reason, r.url)

    if http_error_msg:
        try:
            error_dict = r.json()
        except ValueError:
            raise HTTPError(http_error_msg)
        if error_dict is None:
            raise HTTPError(http_error_msg)
        else:
            raise WebServiceException(
                message = http_error_msg,
                title = error_dict.get('title', None),
                description = error_dict.get('description', None)
            )


def get_labeling_tasks(limit: int = None) -> pd.DataFrame:
    """
    Gets previously submitted labeling tasks.
    Args:
        limit: If specified, only return `limit` previous tasks. Otherwise, return the service's default.

    Returns:
        Dataframe of previous labeling tasks
    """
    if limit is not None:
        r = requests.get("{}/labelingtasks".format(configuration.webservice_root), auth = (configuration.user, configuration.password),
                         params = {'count': limit})
    else:
        r = requests.get("{}/labelingtasks".format(configuration.webservice_root), auth = (configuration.user, configuration.password))

    _raise_custom_exception_for_status(r)

    # success! build dataframe and return
    ret = r.json()
    return pd.DataFrame(ret['labeling_tasks'])


def get_labeling_task_status(labeling_task_id: str) -> str:
    """
    Gets the status of a labeling task
    Args:
        labeling_task_id
    Returns:
        One of [submitted, processed, failed, skipped, purged]
    """

    # Query
    r = requests.get("{}/labelingtask/{}".format(configuration.webservice_root, labeling_task_id), auth = (configuration.user, configuration.password))

    # Handle error cases
    if r.status_code == 404:
        raise UnknownLabelingTask("Unknown labeling task with id: {}".format(labeling_task_id))
    _raise_custom_exception_for_status(r)

    # Success! return correct information
    ret = r.json()
    return ret['status']


def get_labeling_task_content(labeling_task_id: str) -> Union[str, pd.DataFrame]:
    """
    Gets the content of a labeling task
    Args:
        labeling_task_id
    Returns:
        String of json/csv, or DataFrame
    """
    # Query
    r = requests.get("{}/labelingtask/{}/content".format(configuration.webservice_root, labeling_task_id), auth = (configuration.user, configuration.password))

    # Handle error cases
    if r.status_code == 404:
        raise UnknownLabelingTask("Unknown labeling task with id: {}".format(labeling_task_id))
    if r.status_code == 425:
        raise ResultNotReady
    _raise_custom_exception_for_status(r)

    # Success! return data
    if 'Content-Type' not in r.headers:
        raise RuntimeError("Content-Type not returned with webservice call. Unable to determine response type.")

    content_type = r.headers['Content-Type']
    if content_type in ('text/csv', 'application/json'):
        return r.text
    elif content_type == 'application/arrow':
        bites = r.content
        # noinspection PyTypeChecker
        df = pa.deserialize(bites)
        return df
    else:
        raise RuntimeError("Unknown Content-Type returned: {}".format(content_type))


def create_new_labeling_task(labeling_solution_category: str, labeling_solution_name: str, data: pd.DataFrame, *,
                             companies: Optional[Iterable[str]] = None, output_format: str = 'arrow', tags: Optional[List[str]] = None):
    """
    Submits a new labeling task to be processed in the webservice. See the corresponding function in the SDK layer for expected values.
    Args:
        labeling_solution_category:
        labeling_solution_name:
        data:
        companies:
        output_format:
        tags:
    Returns:
        Newly created labeling task's ID.
    """
    try:
        validate_input_dataframe(data)
    except ValueError as e:
        raise e

    # Build params dictionary
    parameters = {}
    if companies:
        parameters['companies'] = list(companies)

    # Build arrow object
    _tuple = (data, parameters, tags or [])
    bites = bytes(pa.serialize(_tuple).to_buffer())

    # Query
    headers = {'Content-Type': 'application/arrow'}
    params = {'output_format': output_format}
    r = requests.post("{}/labelingtask/new/{}/{}".format(configuration.webservice_root, labeling_solution_category,
                                                         labeling_solution_name),
                      auth = (configuration.user, configuration.password), data = bites, headers = headers, params = params)

    # Check and return
    _raise_custom_exception_for_status(r)

    # Success! return id
    ret = r.json()
    return ret['labeling_task_id']


def validate_input_dataframe(df):
    ALLOWED_COLUMNS = ['product_description', 'document_id', 'from_email']
    if df.shape[0] == 0:  # if DataFrame has no rows
        raise ValueError("Input DataFrame is empty. {}".format(df.head(3)))
    if df.shape[1] > 3:  ## DataFrame has too many columns
        raise ValueError("Input DataFrame has too many columns. Allowed columns are {}, {} and {}" \
                         .format("document_id", "from_email", "product_description"))
    if "product_description" not in df.columns:
        raise ValueError("Input DataFrame requires {} column. {} were found.".format("product_description", df.columns))  # TODO
    for column in df.columns:
        if column not in ALLOWED_COLUMNS:
            raise ValueError("Input DataFrame has invalid column '{}'. Valid input columns are {}".format(column, ALLOWED_COLUMNS))
    if "product_description" not in df.columns:
        raise ValueError("Input DataFrame requires {} column. {} were found.".format("product_description", df.columns))  # TODO


def get_company_set(labeling_solution_category: str, labeling_solution_name: str) -> Set[str]:
    """
    Request the list of all possible company results for the specified labeling_solution_category and labeling_solution_name
    Args:
        labeling_solution_category:
        labeling_solution_name:
    Returns:
        List of Companies available for the specified solution
    """
    # Query

    url = "{host}/companies/{category}/{name}".format(host = configuration.webservice_root,
                                                      category = labeling_solution_category,
                                                      name = labeling_solution_name)

    r = requests.get(url, auth = (configuration.user, configuration.password))
    # Check and return
    _raise_custom_exception_for_status(r)
    ret = r.json()
    return set(ret['companies'])


def get_labeling_solutions():
    """
    Requests the dictionary of all possible service types available.
    Returns:
        Dict of labeling solutions available
    """
    # Query

    url = "{host}/solutions".format(host = configuration.webservice_root)

    r = requests.get(url, auth = (configuration.user, configuration.password))
    # Check and return
    _raise_custom_exception_for_status(r)
    ret = r.json()
    return ret['solutions']


def get_company_categories(labeling_solution_category: str, labeling_solution_name: str) -> Set[str]:
    """
    Get a list of company sectory/category aliases that can be passed to the service.
    Returns:
        Set of company categories
       """
    # Query

    url = "{host}/categories/{category}/{name}".format(host = configuration.webservice_root,
                                                       category = labeling_solution_category,
                                                       name = labeling_solution_name)

    r = requests.get(url, auth = (configuration.user, configuration.password))
    # Check and return
    _raise_custom_exception_for_status(r)
    # Success! return id
    ret = r.json()
    return set(ret['categories'])


def get_logs(labeling_task_id: str):
    """
    Get the logs for a given labeling task.
    Args:
        labeling_task_id: Submitted labeling task id. Can be processing, processed, or failed.

    Returns:
        List of dicts; each dictionary is a log entry
    """
    url = "{host}/labelingtask/{labeling_task_id}/logs".format(host = configuration.webservice_root,
                                                               labeling_task_id = labeling_task_id)

    r = requests.get(url, auth = (configuration.user, configuration.password))
    # Check and return
    _raise_custom_exception_for_status(r)
    # Success! return id
    return r.json()
