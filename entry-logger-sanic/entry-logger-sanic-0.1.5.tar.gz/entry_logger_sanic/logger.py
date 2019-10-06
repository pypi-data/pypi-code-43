import json
import logging
import os
import requests
import traceback
from datetime import datetime

from sanic import Sanic, request, response
from sanic.log import logger as sanic_logger

SERVICE_NAME = str()


class JSONLogFormatter(logging.Formatter):
    def __init__(self, webhook, maintainer):
        self.webhook = webhook
        self.maintainer = maintainer
        super().__init__()

    def format(self, record):
        log = {
            "level": record.levelname,
            "issued_at": _iso_time_format(datetime.utcnow()),
            "logger": record.name,
            "thread": record.threadName,
            "module": record.module,
            "filename": record.filename,
            "line_no": record.lineno,
            "msg": record.getMessage(),
            "exec_info": "".join(traceback.format_exception(*record.exc_info))
            if record.exc_info
            else "",
        }
        if self.webhook and record.exc_info:
            requests.post(
                self.webhook,
                json={
                    "attachments": [
                        {
                            "fallback": "an error occurred",
                            "color": "#FB0000",
                            "author_name": SERVICE_NAME,
                            "title": record.getMessage(),
                            "text": f"단 하나의 진실을 꿰뚫는 겉 보기엔 어린이, 두뇌는 어른! 그 이름은 명탐정 코난!\n<@{self.maintainer}>! *범인은 바로 당신이야!*\nException in detail:\n```{''.join(traceback.format_exception(*record.exc_info))}```",
                            "mrkdwn_in": ["text"],
                            "fields": [
                                {
                                    "title": "Priority",
                                    "value": "High",
                                    "short": False
                                }
                            ],
                            "ts": int(datetime.now().timestamp())
                        }
                    ]
                }
            )
        return json.dumps(log)


def _create_handler(log_path, formatter=None):
    handler = logging.FileHandler(f"{log_path}/{SERVICE_NAME}.log")
    handler.setFormatter(formatter)

    return handler


def _iso_time_format(dt):
    return "%04d-%02d-%02dT%02d:%02d:%02d.%03dZ" % (
        dt.year,
        dt.month,
        dt.day,
        dt.hour,
        dt.minute,
        dt.second,
        int(dt.microsecond / 1000),
    )


def set_logger(app: Sanic, log_path: str):
    log_path += "/log"

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    if not isinstance(app, Sanic):
        raise RuntimeError("Invalid app was given")

    global SERVICE_NAME

    SERVICE_NAME = app.name

    sanic_logger.info(
        f"Service log will saved at {os.path.abspath(f'{log_path}/{SERVICE_NAME}.log')}"
    )

    webhook = app.config.get("SLACK_WEBHOOK_URL")
    maintainer = app.config.get("SLACK_MAINTAINER_ID")

    if not webhook:
        sanic_logger.info("Slack integration was not set")

    _set_sanic_logger(log_path, webhook, maintainer)
    logger = _set_request_logger(log_path)

    @app.middleware("request")
    def request_log(req: request.Request):
        req["request_time"] = datetime.utcnow()

    @app.middleware("response")
    def response_log(req: request.Request, res: response.HTTPResponse):
        log = {
            "level": "INFO" if res.status == 200 else "WARN",
            "issued_at": _iso_time_format(req["request_time"]),
            "tracking_id": dict(req.headers).get("X-Tracking-ID"),
            "url": req.url,
            "method": req.method,
            "path": req.path,
            "path_template": req.uri_template,
            "request_header": dict(req.headers),
            "request_body": req.body.decode(),
            "request_query_string": req.args,
            "request_ip": req.ip,
            "request_received_at": _iso_time_format(req["request_time"]),
            "response_sent_at": _iso_time_format(datetime.utcnow()),
            "response_status": res.status,
            "response_content_type": res.content_type,
            "response_body": res.body.decode(),
            "response_body_length": len(res.body),
            "duration_time": str(datetime.utcnow() - req["request_time"]),
        }
        logger.info(json.dumps(log))


def _set_sanic_logger(log_path, webhook, maintainer):
    handler = _create_handler(log_path, JSONLogFormatter(webhook, maintainer))

    sanic_logger.addHandler(handler)


def _set_request_logger(log_path):
    handler = _create_handler(log_path)

    logger = logging.getLogger("sanic-request-log")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger
