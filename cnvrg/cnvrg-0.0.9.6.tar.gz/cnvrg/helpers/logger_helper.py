import click
import logging
import os
import json

LEVEL_INFO='blue'
LEVEL_ERROR="red"
LEVEL_SUCCESS="greed"

os.makedirs(os.path.join(os.path.expanduser("~"), '.cnvrg'), exist_ok=True)
logging.basicConfig(filename=os.path.join(os.path.expanduser("~"), '.cnvrg', 'cnvrg.log'), filemode='w', format='%(name)s - %(levelname)s - %(message)s')

def log_message(message, level=LEVEL_INFO, *args, **kwargs):
    try:
        click.secho(message, *args, **{"color": level, **kwargs})
    except Exception as e:
        print(message)
    logging.info(message)

def log_cnvrg_log(log):
    log_type = log.get("type")
    if log_type == "cnvrg-info":
        level = LEVEL_INFO
    elif log_type == "cnvrg-error":
        level = LEVEL_ERROR
    else:
        level = None
    log_message(log.get("message").strip(), level=level)


def log_bad_response(url, data=None, headers=None):
    logging.error("Got bad response to {url}, \nwith data: {data}, \nwith headers: {headers}".format(url=url, data=json.dumps(data or {}), headers=json.dumps(headers or {})))

def log_error(exception: Exception):
    logging.exception(exception)