import requests
import json
import os
from cnvrg.modules.errors import CnvrgError
import cnvrg.helpers.auth_helper as auth_helper
import cnvrg.helpers.logger_helper as logger_helper
from cnvrg.helpers.url_builder_helper import url_join


JSON_HEADERS = {
    "Content-Type": "application/json"
}

def verify_logged_in():
    if not credentials.logged_in:
        raise CnvrgError("Not authenticated")

def __parse_resp(resp, **kwargs):
    try:
        r_j = resp.json()
        return r_j
    except Exception as e:
        logger_helper.log_error(e)
        logger_helper.log_bad_response(**kwargs)



def get(url, data=None):
    verify_logged_in()
    get_url = url_join(base_url, url)
    resp = session.get(get_url, params=data)
    return __parse_resp(resp, url=url, data=data)

def post(url, data=None, files=None):
    verify_logged_in()
    get_url = url_join(base_url, url)
    resp = session.post(get_url, data=json.dumps(data), files=files)
    return __parse_resp(resp, url=url, data=data)

def send_file(url, data=None, files=None):
    verify_logged_in()
    get_url = url_join(base_url, url)
    resp = requests.post(get_url, files=files, data=data, headers={"AUTH-TOKEN": credentials.token})
    return __parse_resp(resp, url=url, data=data)

def put(url, data=None):
    verify_logged_in()
    get_url = url_join(base_url, url)
    resp = session.put(get_url, data=json.dumps(data))
    return __parse_resp(resp, url=url, data=data)

def download_file(url):
    resp = requests.get(url)
    return resp.text

def download_raw_file(url):
    resp = requests.get(url)
    return resp.content

def update_credentials():
    global credentials
    credentials = auth_helper.CnvrgCredentials()

credentials = auth_helper.CnvrgCredentials()
session = requests.session()
session.headers = {
    "AUTH-TOKEN": credentials.token,
    **JSON_HEADERS
}
base_url = url_join(credentials.api_url, "v1")

