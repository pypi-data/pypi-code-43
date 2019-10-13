import requests
import time
from common_utils.new_log import NewLog


class HttpOperate:

    log = NewLog(__name__)
    logger = log.get_log()
    interval_time = 0.5
    session = requests.Session()

    @classmethod
    def http_get(cls, url, headers, params=None, **kwargs):
        cookies = kwargs.get('cookies')
        response = cls.session.get(url=url, headers=headers, cookies=cookies, params=params, **kwargs)
        time.sleep(cls.interval_time)
        return response.text, response.status_code

    @classmethod
    def http_post(cls, url, headers, params=None, cookies=None, data=None,  **kwargs):
        response = cls.session.post(url=url, headers=headers, cookies=cookies, params=params, data=data, **kwargs)
        time.sleep(cls.interval_time)
        return response.text, response.status_code

    @classmethod
    def http_put(cls, url, headers, cookies=None, data=None, **kwargs):
        response = cls.session.put(url=url, headers=headers, cookies=cookies, data=data, **kwargs)
        time.sleep(cls.interval_time)
        return response.text, response.status_code

    @classmethod
    def http_delete(cls, url, headers, cookies=None, **kwargs):
        response = cls.session.delete(url=url, headers=headers, cookies=cookies, **kwargs)
        time.sleep(cls.interval_time)
        return response.text, response.status_code
