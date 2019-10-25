import logging
import sys
from datetime import datetime
from typing import Any, List, Optional

from pythonjsonlogger import jsonlogger


class _CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        log_record["timestamp"] = log_record.get("timestamp", now)

        severity = log_record.get("level", record.levelname)
        log_record["severity"] = severity.upper()

        source_location = {
            "file": record.filename,
            "function": record.funcName,
            "line": record.lineno,
            "loggerName": record.name,
            "threadName": record.threadName,
            "thread": record.thread,
        }
        log_record["sourceLocation"] = source_location


def _get_standard_text_formatter():
    return logging.Formatter(
        "%(asctime)s.%(msecs)03d [%(levelname)-8s] %(threadName)s. %(message)s (%(filename)s:%(lineno)s)",
        "%Y-%m-%d %H:%M:%S",
    )


def configure_logger(
    logger_name: Optional[str] = None,
    log_level: str = "DEBUG",
    log_json: bool = True,
    replace_handler: bool = True,
    filters: List = None,
    filename: str = None,
    stream: Any = None,
) -> logging.Logger:
    """
    Configure logger

    Args:
        logger_name (str, optional): Name of the logger. Defaults to root logger.
        log_level (str, optional): Log level. Defaults to "DEBUG".
        log_json (bool, optional): Flag for logging json or not. Defaults to True.
        replace_handler (bool, optional): Flag to determine if new handler should replace any already on the logger.
            Defaults to True.
        filters (List, optional): List of filters to add to log handler. Defaults to no filters.
        filename (str): Set to filename if logging should be done to file.
        stream (Any): Stream to log to. Defaults to sys.stdout.

    Returns:
        Logger: The created logger
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    if filename is None:
        if stream is None:
            stream = sys.stdout
        log_handler = logging.StreamHandler(stream)
    else:
        log_handler = logging.FileHandler(filename)

    if log_json:
        formatter = _CustomJsonFormatter()
    else:
        formatter = _get_standard_text_formatter()
    log_handler.setFormatter(formatter)

    if filters:
        for current in filters:
            log_handler.addFilter(current)

    if replace_handler:
        logger.handlers = []
        logger.propagate = False
    logger.addHandler(log_handler)

    return logger
