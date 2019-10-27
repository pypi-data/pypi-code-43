import logging
import os

import pandas as pd
import numpy as np
import decorator
import loguru
import pytest
# noinspection PyUnresolvedReferences
from _pytest.logging import caplog as _caplog

from logsensei import logger

LOG_PATH = "test/log"


def clean_folder(path):
    files = os.listdir(path)
    for f in files:
        if not f.startswith("."):
            os.remove(os.path.join(path, f))


def cleanup_test(func):
    def wrapper(func, *args, **kwargs):
        logger.reset()
        clean_folder(LOG_PATH)
        result = func(*args, **kwargs)
        clean_folder(LOG_PATH)
        logger.reset()
        return result

    return decorator.decorator(wrapper, func)


@pytest.fixture
def caplog(_caplog):
    class PropogateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    handler_id = loguru.logger.add(PropogateHandler(), format="{message}")
    yield _caplog
    loguru.logger.remove(handler_id)


@cleanup_test
def test_setup():
    logger.setup("test_setup", LOG_PATH)
    f = [x for x in os.listdir(LOG_PATH) if not x.startswith(".")]
    print(f)
    assert len(f) == 1
    assert f[0].startswith("test_setup")


@cleanup_test
def test_setup_reset(caplog):
    logger.info("Hello 0")
    logger.setup("test_reset_1", LOG_PATH)
    logger.info("Hello 1")
    logger.reset()
    logger.setup("test_reset_2", LOG_PATH)
    logger.info("Hello 2")
    logger.reset()
    logger.info("Hello 3")
    assert caplog.record_tuples == [
        ("test.test_logsensei", logging.INFO, "Hello 0"),
        ("test.test_logsensei", logging.INFO, "Hello 1"),
        ("test.test_logsensei", logging.INFO, "Hello 2"),
        ("test.test_logsensei", logging.INFO, "Hello 3"),
    ]
    files = [x for x in os.listdir(LOG_PATH) if not x.startswith(".")]
    assert len(files) == 2
    for file in files:
        if "test_reset_1" in file:
            with open(os.path.join(LOG_PATH, file)) as f:
                lines = f.readlines()
                assert len(lines) == 1
                assert "Hello 1" in lines[0]
        else:
            with open(os.path.join(LOG_PATH, file)) as f:
                lines = f.readlines()
                assert len(lines) == 1
                assert "Hello 2" in lines[0]


def test_debug(caplog):
    logger.debug("Hello debug")
    assert caplog.record_tuples == [("test.test_logsensei", logging.DEBUG, "Hello debug")]


def test_info(caplog):
    logger.info("Hello info")
    assert caplog.record_tuples == [("test.test_logsensei", logging.INFO, "Hello info")]


def test_warning(caplog):
    logger.warning("Hello warning")
    assert caplog.record_tuples == [("test.test_logsensei", logging.WARNING, "Hello warning")]


def test_error(caplog):
    logger.error("Hello error")
    assert caplog.record_tuples == [("test.test_logsensei", logging.ERROR, "Hello error")]


def test_critical(caplog):
    logger.critical("Hello critical")
    assert caplog.record_tuples == [("test.test_logsensei", logging.CRITICAL, "Hello critical")]


def test_log(caplog):
    logger.log("Hello debug", logging.DEBUG)
    logger.log("Hello info", logging.INFO)
    logger.log("Hello warning", logging.WARNING)
    logger.log("Hello error", logging.ERROR)
    logger.log("Hello critical", logging.CRITICAL)
    assert caplog.record_tuples == [
        ("test.test_logsensei", logging.DEBUG, "Hello debug"),
        ("test.test_logsensei", logging.INFO, "Hello info"),
        ("test.test_logsensei", logging.WARNING, "Hello warning"),
        ("test.test_logsensei", logging.ERROR, "Hello error"),
        ("test.test_logsensei", logging.CRITICAL, "Hello critical"),
    ]


def test_log_fail():
    with pytest.raises(ValueError):
        logger.log("Hello fail", 0)


@cleanup_test
def test_template(caplog):
    logger.create('template', 'template : {}')
    logger.apply('template', 'old')
    logger.create('template', 'template : {} {}')
    logger.apply('template', 'new', 'world')
    assert caplog.record_tuples == [
        ("test.test_logsensei", logging.INFO, "template : old"),
        ('logsensei', logging.WARNING, 'Replacing the template message in template'),
        ("test.test_logsensei", logging.INFO, "template : new world"),
    ]

#
# def test_df(caplog):
#     df = pd.DataFrame({
#         'a': [1,2,3,4,np.nan],
#         'b': ['foo', 'bar', 'baz', np.nan, np.nan],
#         'c': [True, True, False, np.nan, np.nan],
#         'd': [1.0, 2.0, 3.0, 4.0, np.nan]
#     })
#     logger.df(df, 'test_df')
#     assert caplog.record_tuples == [
#         ("test.test_logsensei", logging.INFO, )
#     ]
#
#