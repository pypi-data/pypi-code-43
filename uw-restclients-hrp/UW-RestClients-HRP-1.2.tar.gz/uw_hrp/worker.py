"""
This is the interface for interacting with the HRP Web Service.
"""

from datetime import datetime
import logging
import json
import re
from urllib.parse import urlencode
from restclients_core.exceptions import InvalidRegID, InvalidNetID,\
    InvalidEmployeeID
from uw_hrp import get_resource
from uw_hrp.models import Worker, WorkerRef


logger = logging.getLogger(__name__)
re_netid = re.compile(r'^[a-z][a-z0-9\-\_\.]{,127}$', re.I)
re_regid = re.compile(r'^[A-F0-9]{32}$', re.I)
re_employee_id = re.compile(r'^\d{9}$')
URL_PREFIX = "/hrp/v2/worker"
CURRENT_FUTURE_SUFFIX = "workerpositionstate=current,future"


def get_worker_by_employee_id(employee_id, current_future=True):
    if not valid_employee_id(employee_id):
        raise InvalidEmployeeID(employee_id)
    return _get_worker(employee_id, current_future)


def get_worker_by_netid(netid, current_future=True):
    if not valid_uwnetid(netid):
        raise InvalidNetID(netid)
    return _get_worker(netid, current_future)


def get_worker_by_regid(regid, current_future=True):
    if not valid_uwregid(regid):
        raise InvalidRegID(regid)
    return _get_worker(regid, current_future)


def _get_worker(id, current_future):
    """
    Return a restclients.models.hrp.WorkerPerson object
    """
    url = "{0}/{1}.json".format(URL_PREFIX, id)
    if current_future:
        url = "{0}?{1}".format(url, CURRENT_FUTURE_SUFFIX)
    return Worker(data=json.loads(get_resource(url)))


def worker_search(**kwargs):
    """
    Returns a list of WorkerRef objects
    Parameters can be:
      legal_first_name_contains: string
      legal_first_name_starts_with: string
      legal_last_name_contains: string
      legal_last_name_starts_with: string
      preferred_first_name_contains: string
      preferred_first_name_starts_with: string
      preferred_last_name_contains: string
      preferred_last_name_starts_with: string
      is_current_faculty: string
      cost_center_id: string
      workday_person_type: string
      ascii_only: string
      location_id: string
      changed_since: string
      page_start: string (default: 1)
    """
    url = "{0}.json?{1}&page_size=200".format(URL_PREFIX, urlencode(kwargs))
    workerefs = []
    while True:
        data = json.loads(get_resource(url))
        if len(data["Workers"]) > 0:
            for wkr_data in data.get("Workers"):
                workerefs.append(WorkerRef(data=wkr_data))
        if data.get("Next") is not None and len(data["Next"]["Href"]) > 0:
            url = data["Next"]["Href"]
        else:
            break
    return workerefs


def valid_uwnetid(netid):
    return (netid is not None and
            re_netid.match(str(netid)) is not None)


def valid_uwregid(regid):
    return (regid is not None and
            re_regid.match(str(regid)) is not None)


def valid_employee_id(employee_id):
    return (employee_id is not None and
            re_employee_id.match(str(employee_id)) is not None)
