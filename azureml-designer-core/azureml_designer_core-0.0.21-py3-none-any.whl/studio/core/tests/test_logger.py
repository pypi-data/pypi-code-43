import logging
import sys

import pytest

from azureml.studio.core.logger import logger, time_profile, _LoggerContext, LOGGER_TAG, LogHandler, get_logger
from azureml.studio.core.logger import log_dict_values, log_list_values


def test_logging_level(caplog):
    logger.debug("Module debug is allowed")

    root_logger = logging.getLogger()
    root_logger.debug("Debug is disabled")
    root_logger.info("Info is disabled")
    root_logger.warning("Warning is expected")

    other_logger = logging.getLogger("other_logger")
    other_logger.debug("Debug is disabled")
    other_logger.info("Info is disabled")
    other_logger.warning("Warning is expected")

    assert "Module debug is allowed" in caplog.text
    assert 'Debug is disabled' not in caplog.text
    assert 'Info is disabled' not in caplog.text


@time_profile
def func1():
    return


@time_profile
def func2():
    return func1()


def test_logging_context(capsys):
    hdl = LogHandler(sys.stdout)
    logger.addHandler(hdl)
    func2()
    out, err = capsys.readouterr()
    lines = out.split('\n')[:-1]
    func2_pos = lines[0].find('func2')

    assert all((LOGGER_TAG in line for line in lines))
    assert func2_pos > 0
    assert func2_pos == lines[-1].find('func2')
    func1_pos = lines[1].find('func1')
    assert func1_pos > 0
    assert func1_pos == lines[-2].find('func1')
    assert func1_pos == func2_pos + _LoggerContext.INDENT_SIZE
    logger.removeHandler(hdl)


def test_get_logger():
    from azureml.studio.core.logger import root_logger
    assert get_logger() == root_logger

    with pytest.raises(ValueError, match="Invalid log name 'Uppercase'. Should only contains lowercase letters"):
        assert get_logger('Uppercase')

    valid_logger = get_logger('valid')
    assert valid_logger is not None


def test_log_list_values(capsys):
    hdl = LogHandler(sys.stdout)
    logger.addHandler(hdl)
    list_value = ['aaa', 'bbb', 'ccc']
    list_name = 'A List'
    log_list_values(list_name, list_value)
    out, err = capsys.readouterr()
    lines = out.split('\n')
    assert list_name in lines[0]
    for i, (val, line) in enumerate(zip(list_value, lines[1:])):
        assert f'|   [{i}] = {val}' in line


def test_log_list_values_empty(capsys):
    hdl = LogHandler(sys.stdout)
    logger.addHandler(hdl)
    log_list_values('Empty', None)
    out, err = capsys.readouterr()
    assert '(empty)' in out


def test_log_dict_values(capsys):
    hdl = LogHandler(sys.stdout)
    logger.addHandler(hdl)
    dict_value = {'k1': 'aaa', 'k2': 'bbb'}
    dict_name = 'A Dict'
    log_dict_values(dict_name, dict_value)
    out, err = capsys.readouterr()
    lines = out.split('\n')
    assert dict_name in lines[0]
    for (key, val), line in zip(dict_value.items(), lines[1:]):
        assert f'|   {key} = {val}' in line


def test_log_dict_values_empty(capsys):
    hdl = LogHandler(sys.stdout)
    logger.addHandler(hdl)
    log_dict_values('Empty', None)
    out, err = capsys.readouterr()
    assert '(empty)' in out
