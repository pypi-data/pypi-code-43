"""
This module wraps the ElasticSearch query functionality provided by
the ANTARES portal.

Downloading an ES result-set works as follows:

    1) The client POSTs to ``/alerts/search/download`` with the ES
       query;

    2) The server submits the query to another thread for processing.
       The server stores the name of this thread, along with the job's
       status, progress, etc., in Redis. The server responds to the
       client with a JSON representation of this ``job`` object.

    3) The server creates a file in a temporary directory named
       ``{job.id}.results.csv.gz``;

    4) The server incrementally queries for paged results from the
       ESDB and writes them into ``{job.id}.results.csv.gz``.

Any point after step (2), the client can GET the
``/alerts/search/downloads/<str:job_id>/status`` route to check the
status of the job.

The response from the server has the following format:

.. code:: json

   {
     "job": {
       "id": UUID4,
       "status": "submited" | "processing" | "ready" | "errored"
       "format": "json" | "csv",
       "created_at": <str>,
       "updated_at": <str>,
       "recordsTotal": <int>,
       "recordsProcessed": <int>,
       "urls": {
         "status": <str>,
         "download": <str>
       }
     }
   }

Once ``job["status"] == "ready"`` the client may GET the
``/alerts/search/download/<str:job_id>`` route to download the result
set.

"""

import enum
import gzip
import json
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


class SearchError(Exception):
    """Error evaluating ElasticSearch query"""


class JobStatus(enum.Enum):
    """Status messages for progress callbacks"""

    SUBMITTED = "submitted"  #: Job has been submitted to the server
    PROCESSING = (
        "processing"
    )  #: Job has been received by the server and is being processed
    READY = "ready"  #: Job has been finished processing by the server
    DOWNLOADING = "downloading"  #: Job is being downloaded from the server
    COMPLETED_DOWNLOADING = (
        "completed_downloading"
    )  #: Job is finished downloading from the server
    ERRORED = "errored"  #: An error occured either client- or server-side


BASE_URL = "https://antares.noao.edu"
NOOP = (
    lambda *args, **kwargs: None
)  #: Noop function that accepts arbitrary ``args``, ``kwargs``
REQUESTS_RETRIES = 2
REQUESTS_BACKOFF_FACTOR = 0.1
REQUESTS_STATUS_FORCELIST = (500, 502, 504)

REQUESTS_POLL_FREQUENCY = 3


def configure_requests_session(
    session=None,
    retries=REQUESTS_RETRIES,
    backoff_factor=REQUESTS_BACKOFF_FACTOR,
    status_forcelist=REQUESTS_STATUS_FORCELIST,
):
    """
    Configure or create a ``requests.session`` to use an intelligent
    retry strategy.

    Notes
    ----------
    Peter Bengtsson
    https://www.peterbe.com/plog/best-practice-with-retries-with-requests

    """
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


SESSION = configure_requests_session()


def search(query, progress_callback=NOOP):
    """
    Retrieves an ElasticSearch query resultset from the ANTARES portal.

    Parameters
    ----------
    query: dict
        ElasticSearch query.
    progress_callback: callable
        Called periodically throughout the processing of ``query``, first
        argument will be an enum member of ``antares_client.search.JobStatus``.
        Should also accept ``*args``.  and ``**kwargs``.

    Raises
    ----------
    MaxRetryError
        If the server returns ``REQUESTS_STATUS_FORCELIST`` status codes
        more than ``REQUESTS_RETRIES`` times.
    ConnectionError
        If a connection to the server cannot be established.
    antares_client.search.SearchError
        If the server encounters an error processing the search query.

    Returns
    ----------
    result_set: [dict]

    """
    result_set = _raw_search(
        query,
        output_format="json",
        decompress=True,
        progress_callback=progress_callback,
    )
    result_set = json.loads(result_set.decode("utf-8"))
    return result_set


def download(
    query, path, output_format="json", decompress=False, progress_callback=NOOP
):
    """
    Downloads an ElasticSearch query result set from the ANTARES portal.

    Parameters
    ----------
    query: dict
        ElasticSearch query.
    path: str
        Path to write the result set to.
    output_format: {"json", "csv"}
        Output format of the result set (default, json).
    decompress: bool
        Un-gzip the result set (default, False).
    progress_callback: callable
        Called periodically throughout the processing of ``query``, first
        argument will be an enum member of ``antares_client.search.JobStatus``.
        Should also accept ``*args``.  and ``**kwargs``.

    Raises
    ----------
    MaxRetryError
        If the server returns ``REQUESTS_STATUS_FORCELIST`` status codes
        more than ``REQUESTS_RETRIES`` times.
    ConnectionError
        If a connection to the server cannot be established.
    antares_client.search.SearchError
        If the server encounters an error processing the search query.

    Returns
    ----------
    None

    """
    result_set = _raw_search(
        query,
        output_format=output_format,
        decompress=decompress,
        progress_callback=progress_callback,
    )
    with open(path, "wb") as f:
        f.write(result_set)


def _raw_search(query, output_format="json", decompress=False, progress_callback=NOOP):
    if output_format not in {"json", "csv"}:
        raise ValueError("output_format must be one of {'json', 'csv'}")
    job = _submit_search_job(query, output_format, progress_callback=progress_callback)
    job = _block_until_search_job_is_done(job, progress_callback=progress_callback)
    result_set = _download_search_result_set(
        job, decompress=decompress, progress_callback=progress_callback
    )
    return result_set


def _submit_search_job(query, output_format="json", progress_callback=NOOP):

    response = SESSION.post(
        BASE_URL + "/alerts/search/download/",
        {"es_query": json.dumps(query), "format": output_format},
    )
    response.raise_for_status()
    job = response.json()["job"]
    progress_callback(JobStatus.SUBMITTED, job=job)
    return job


def _block_until_search_job_is_done(job, timeout=float("inf"), progress_callback=NOOP):
    """
    Blocks until the server has finished preparing the result set
    for download.

    Parameters
    ----------
    timeout: float

    Raises
    ----------
    ConnectionError
    MaxRetryError
    TimeoutError
        If polling takes more than ``timeout`` seconds

    """
    start = time.time()
    while (time.time() - start) <= timeout:
        response = SESSION.get(job["urls"]["status"])
        response.raise_for_status()
        job = response.json()["job"]
        if job["status"] == "errored":
            progress_callback(JobStatus.ERRORED, job=job)
            raise SearchError
        if job["status"] == "processing":
            progress_callback(JobStatus.PROCESSING, job=job)
        elif job["status"] == "ready":
            progress_callback(JobStatus.READY, job=job)
            return job
        time.sleep(REQUESTS_POLL_FREQUENCY)
    else:  # pylint: disable=useless-else-on-loop
        raise TimeoutError


def _download_search_result_set(job, decompress=False, progress_callback=NOOP):
    """
    Downloads the query resultset (i.e. GETs the data from the server).

    Parameters
    ----------
    timeout: float

    Returns
    ----------
    bytes

    Raises
    ----------
    ConnectionError
    MaxRetryError

    """
    progress_callback(JobStatus.DOWNLOADING, job=job)
    response = SESSION.get(job["urls"]["download"])
    response.raise_for_status()
    result_set = response.content
    if decompress:
        result_set = gzip.decompress(result_set)
    progress_callback(JobStatus.COMPLETED_DOWNLOADING, job=job)
    return result_set
