import requests
from atp import logger


def get(url, **kwargs):
    # get method
    params = kwargs.get("params")
    headers = kwargs.get("headers")
    try:
        res = requests.get(url=url, params=params, headers=headers)
        logger.log_info("request info : %s " % url)
        logger.log_info("response info : %s" % res.json())
        logger.log_info("response status code : %s " % res.status_code)
        return res
    except Exception as e:
        logger.log_error("get request error : %s" % e)
