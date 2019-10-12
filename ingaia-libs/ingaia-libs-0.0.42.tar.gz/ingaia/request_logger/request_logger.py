import logging
import time
import os
import requests
import threading
import jwt

from werkzeug.exceptions import HTTPException
from werkzeug.http import HTTP_STATUS_CODES
from flask import request, Response, make_response
from decorator import decorator

from ingaia.gcloud import SchedulerUtil, QueueUtil
from .helper import convert_dict_value_to_str
from .config import config
from .exceptions import IngaiaRLTokenNotDefinedException

# limit to show the response
RESPONSE_STR_LIMIT = 100


def generate_rl_token(project_id):
    """
    Generate a JWT Token
    :param project_id: Project identification
    :return: JWT Token
    """
    iat = int(time.time())
    exp = iat + config.JWT_LIFETIME_SECONDS
    payload = {
        "iss": config.JWT_ISSUER,  # "iss" (Issuer) Claim
        "iat": iat,  # "iat" (Issued At) Claim
        "exp": exp,  # "exp" (Expiration Time) Claim
        "sub": str(project_id),  # "sub" (Subject) Claim
    }

    try:
        return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM).decode("utf-8")
    except Exception:
        return None


def save_request(project_id, log_entry):
    """
    Save the request into database. It sends a request to a cloud function to do this.
    :param project_id: Project Id
    :param log_entry: Request log information
    """
    headers = {
        "Ingaia-Project": project_id,
        "Ingaia-RLToken": generate_rl_token(project_id)
    }

    response = requests.post(url=config.REQUEST_LOGGER_DATA_STORE_URL,
                             json=log_entry,
                             headers=headers)
    # log the result
    logging.info(response.text)


class RequestLogger:
    """
    Request Logger Class
    Save the request and response properties on database
    """

    def __init__(self, module_name=None):
        self._module_name = module_name if module_name else __name__

    def log(self, db_store=config.DB_STORE, **kwargs):
        """
        Creates a log entry into google cloud datastore

        :param db_store:    defines if store data on database
        :param kwargs:      function parameters
        :return:            request log entry
        """
        func = kwargs.get('func', None)
        func_args = kwargs.get('func_args', None)
        func_resp_status = kwargs.get('func_resp_status', None)
        func_resp = str(kwargs.get('func_resp', None))

        headers = None
        request_ip = None
        request_remote_port = None
        if request:
            # main headers to store
            headers_to_find = ['Host', 'X-Appengine-User-Ip', 'User-Agent', 'Content-Type', 'X-Forwarded-For',
                               'Forwarded', 'Authorization']
            headers_to_find += SchedulerUtil.CRON_HEADERS
            headers_to_find += QueueUtil.QUEUE_HEADERS
            headers = dict(h for h in request.headers if h[0] in headers_to_find)

            request_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            if 'X-Appengine-User-Ip' in headers:
                request_ip = headers['X-Appengine-User-Ip']

            # gets http remote port
            request_remote_port = request.environ['REMOTE_PORT'] if 'REMOTE_PORT' in request.environ else None

        # gets the project id from environment
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', 'not-set-or-local')

        log_entry = {
            'project_id': project_id,
            'func': func,
            'func_args': func_args,
            'module': self._module_name,
            'request_ip': request_ip,
            'request_remote_port': request_remote_port,
            'request_url': request.base_url,
            'request_method': request.method,
            'request_headers': headers,
            'request_values': request.values,
            'response': func_resp,
            'response_status': func_resp_status,
            'response_status_name': HTTP_STATUS_CODES.get(func_resp_status, "Unknown Error"),
            'timestamp': int(time.time())
        }

        if db_store:
            # validate the request logger token
            if os.environ.get('INGAIA_RL_TOKEN', None):
                # uses a thread to make the process more performative
                threading.Thread(target=save_request, args=(project_id, log_entry)).start()
            else:
                self._only_trace(log_entry)

        return log_entry

    def trace(self, fn, db_store=config.DB_STORE, *args, **kw):
        """
        @trace - Traces the function responsible for the request (endpoint)

        :param fn:          The function decorated
        :param db_store:    Store the request on database
        :param args:        Args
        :param kw:          KWArgs
        :return:            The same response of the function
        """
        # get function properties
        func_name = f'{fn.__module__}.{fn.__name__}'
        request_url = f'{request.method} {request.base_url}'

        # get the response
        _exception = None
        try:
            _resp = fn(*args, **kw)
        except HTTPException as e:
            _resp = make_response(e, e.code)
            _exception = e

        # verify flask response
        response_status = None
        if isinstance(_resp, Response):
            response_str = _resp.json if _resp.is_json else str(_resp.data)
            response_status = _resp.status_code
        else:
            response_str = str(_resp)
            logging.warning(f'{response_str} (No Flask Response object)')

        log_kwargs = {
            'func': fn.__name__,
            'func_args': {
                'args': convert_dict_value_to_str(list(args)),
                'kwargs': convert_dict_value_to_str(kw)
            },
            'func_resp': response_str,
            'func_resp_status': response_status
        }

        # save the request into google cloud datastore
        log_entry = self.log(db_store, **log_kwargs)

        if not db_store:
            self._only_trace(log_entry)

        if _exception:
            raise _exception

        return _resp

    def __str__(self):
        return f'{self.__class__.__name__}("{self._module_name}")'

    @staticmethod
    def _only_trace(log_entry):
        func_resp = log_entry['func_resp'] if 'func_resp' in log_entry else ''
        if len(func_resp) > RESPONSE_STR_LIMIT:
            log_entry['func_resp'] = func_resp[:RESPONSE_STR_LIMIT] + '[...]'

        logging.info(f'[{log_entry["func"]}] {log_entry["request_url"]} :: {log_entry["response_status"]} {log_entry}')


@decorator
def trace(fn, db_store=config.DB_STORE, *args, **kw):
    return RequestLogger(fn.__module__).trace(fn, db_store, *args, **kw)
