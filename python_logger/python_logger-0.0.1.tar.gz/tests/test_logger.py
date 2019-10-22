# pylint: disable=too-many-public-methods
import copy
import json
import logging
import re
import time
from datetime import datetime, timezone

import pytest

import python_logger.logger
from python_logger import critical, debug, error, get_logger, info, initialize, warning


def sort_dict(input_dict):
    return dict(sorted(input_dict.items(), key=lambda kv: kv[0]))


MOCK_DATE = datetime.strptime("2019-08-18T11:55:26.000000+0000", "%Y-%m-%dT%H:%M:%S.%f%z")
MOCK_SERVICE = "test_service"
MOCK_MESSAGE = "this is the logged message."
MOCK_LOGGED_MESSAGE = {
    "timestamp": "2019-08-18T11:55:26.000000+0000",
    "service": MOCK_SERVICE,
    "message": MOCK_MESSAGE,
    "log_level": "DEBUG",
}


@pytest.fixture
def patch_time(monkeypatch):
    def mytime():
        return MOCK_DATE.timestamp()

    monkeypatch.setattr(time, "time", mytime)


class TestLogging:
    @staticmethod
    @pytest.fixture(autouse=True)
    def run_around_tests(patch_time):  # pylint: disable=unused-argument, redefined-outer-name
        yield
        python_logger.logger._LOGGER = None  # pylint: disable=protected-access

    @staticmethod
    def test_log_message_debug(capsys):
        initialize(MOCK_SERVICE, "DEBUG")
        log_msg = copy.deepcopy(MOCK_LOGGED_MESSAGE)
        debug(MOCK_MESSAGE)
        debug(message=MOCK_MESSAGE)
        out, _ = capsys.readouterr()
        out_lines = out.split("\n")
        assert out_lines[0] == json.dumps(sort_dict(log_msg))
        assert out_lines[1] == json.dumps(sort_dict(log_msg))

    @staticmethod
    def test_log_message_info(capsys):
        initialize(MOCK_SERVICE, "DEBUG")
        log_msg = copy.deepcopy(MOCK_LOGGED_MESSAGE)
        log_msg["log_level"] = "INFO"
        info(MOCK_MESSAGE)
        info(message=MOCK_MESSAGE)
        out, _ = capsys.readouterr()
        out_lines = out.split("\n")
        assert out_lines[0] == json.dumps(sort_dict(log_msg))
        assert out_lines[1] == json.dumps(sort_dict(log_msg))

    @staticmethod
    def test_log_message_warning(capsys):
        initialize(MOCK_SERVICE, "DEBUG")
        log_msg = copy.deepcopy(MOCK_LOGGED_MESSAGE)
        log_msg["log_level"] = "WARN"
        warning(MOCK_MESSAGE)
        warning(message=MOCK_MESSAGE)
        out, _ = capsys.readouterr()
        out_lines = out.split("\n")
        assert out_lines[0] == json.dumps(sort_dict(log_msg))
        assert out_lines[1] == json.dumps(sort_dict(log_msg))

    @staticmethod
    def test_log_message_error(capsys):
        initialize(MOCK_SERVICE, "DEBUG")
        log_msg = copy.deepcopy(MOCK_LOGGED_MESSAGE)
        log_msg["log_level"] = "ERROR"
        error(MOCK_MESSAGE)
        error(message=MOCK_MESSAGE)
        out, _ = capsys.readouterr()
        out_lines = out.split("\n")
        assert out_lines[0] == json.dumps(sort_dict(log_msg))
        assert out_lines[1] == json.dumps(sort_dict(log_msg))

    @staticmethod
    def test_log_message_critical(capsys):
        initialize(MOCK_SERVICE, "DEBUG")
        log_msg = copy.deepcopy(MOCK_LOGGED_MESSAGE)
        log_msg["log_level"] = "FATAL"
        critical(MOCK_MESSAGE)
        critical(message=MOCK_MESSAGE)
        out, _ = capsys.readouterr()
        out_lines = out.split("\n")
        assert out_lines[0] == json.dumps(sort_dict(log_msg))
        assert out_lines[1] == json.dumps(sort_dict(log_msg))

    @staticmethod
    def test_log_dictionary_with_more_params(capsys):
        initialize(MOCK_SERVICE, "DEBUG")
        log_msg = copy.deepcopy(MOCK_LOGGED_MESSAGE)
        log_msg["param_a"] = "a"
        log_msg["param_b"] = "b"
        debug(param_a="a", param_b="b", message=MOCK_MESSAGE)
        out, _ = capsys.readouterr()
        assert out[:-1] == json.dumps(sort_dict(log_msg))  # [:-1] removes the newline

    @staticmethod
    def test_log_of_deep_structure(capsys):
        initialize(MOCK_SERVICE, "DEBUG")
        log_msg = copy.deepcopy(MOCK_LOGGED_MESSAGE)
        dictionary = {"param_a": "aa", "param_b": "bb"}
        log_msg["dict"] = dictionary
        debug(dict=dictionary, message=MOCK_MESSAGE)
        out, _ = capsys.readouterr()
        assert out[:-1] == json.dumps(sort_dict(log_msg))  # [:-1] removes the newline

    @staticmethod
    def test_suppression_of_lover_level_messages(capsys):
        initialize(MOCK_SERVICE, "ERROR")
        info(MOCK_MESSAGE)
        out, _ = capsys.readouterr()
        assert out[:-1] == ""

    @staticmethod
    def test_basic_mdc(capsys):
        initialize(MOCK_SERVICE, "DEBUG")
        log_msg = copy.deepcopy(MOCK_LOGGED_MESSAGE)
        log_msg["mdc_param"] = "MDC"
        get_logger().mdc()["mdc_param"] = "MDC"
        debug(MOCK_MESSAGE)
        get_logger().mdc().pop("mdc_param")
        debug(MOCK_MESSAGE)
        out, _ = capsys.readouterr()
        out_lines = out.split("\n")
        assert out_lines[0] == json.dumps(sort_dict(log_msg))
        log_msg.pop("mdc_param")
        assert out_lines[1] == json.dumps(sort_dict(log_msg))

    @staticmethod
    def test_scoped_mdc(capsys):
        initialize(MOCK_SERVICE, "DEBUG")
        log_msg = copy.deepcopy(MOCK_LOGGED_MESSAGE)
        log_msg["added_mdc"] = "added_value"
        with get_logger().add_mdc(added_mdc="added_value"):
            debug(MOCK_MESSAGE)
        debug(MOCK_MESSAGE)
        out, _ = capsys.readouterr()
        out_lines = out.split("\n")
        assert out_lines[0] == json.dumps(sort_dict(log_msg))
        log_msg.pop("added_mdc")
        assert out_lines[1] == json.dumps(sort_dict(log_msg))

    @staticmethod
    def test_added_mdc_in_scoped_block_is_purged_after_the_block(capsys):
        initialize(MOCK_SERVICE, "DEBUG")
        log_msg = copy.deepcopy(MOCK_LOGGED_MESSAGE)
        log_msg["in_block_added"] = True
        log_msg["added_mdc"] = "added_value"
        with get_logger().add_mdc(added_mdc="added_value"):
            get_logger().mdc()["in_block_added"] = True
            debug(MOCK_MESSAGE)
        debug(MOCK_MESSAGE)
        out, _ = capsys.readouterr()
        out_lines = out.split("\n")
        assert out_lines[0] == json.dumps(sort_dict(log_msg))
        log_msg.pop("added_mdc")
        log_msg.pop("in_block_added")
        assert out_lines[1] == json.dumps(sort_dict(log_msg))

    @staticmethod
    def test_exception_formatting(capsys):
        initialize(MOCK_SERVICE, "DEBUG")
        log_msg = copy.deepcopy(MOCK_LOGGED_MESSAGE)
        log_msg["log_level"] = "ERROR"
        try:
            open("rubbish/path")
        except FileNotFoundError as ex:
            error(exc_info=ex, message=MOCK_MESSAGE)
        log_msg["exception"] = {
            "class": "FileNotFoundError",
            "message": "No such file or directory",
        }
        out, _ = capsys.readouterr()
        out_json = json.loads(out)
        trace_wo_newline = "".join(out_json["exception"].pop("stacktrace").split("\n"))
        assert json.dumps(out_json) == json.dumps(sort_dict(log_msg))
        assert re.search(
            r"Traceback \(most recent call last\).*\/tests\/test_logger\.py.*in test"
            + r".*open\(\"rubbish\/path\"\).*No such file or directory: "
            + r"'rubbish\/path'",
            trace_wo_newline,
        )

    @staticmethod
    def test_tuple_exception_formatting(capsys):
        initialize(MOCK_SERVICE, "DEBUG")
        log_msg = copy.deepcopy(MOCK_LOGGED_MESSAGE)
        log_msg["log_level"] = "ERROR"
        try:
            log_msg["INCORRECT"]
        except KeyError as ex:
            error(exc_info=ex, message=MOCK_MESSAGE)
        log_msg["exception"] = {"class": "KeyError", "message": "'INCORRECT'"}
        out, _ = capsys.readouterr()
        out_json = json.loads(out)
        trace_wo_newline = "".join(out_json["exception"].pop("stacktrace").split("\n"))
        assert json.dumps(out_json) == json.dumps(sort_dict(log_msg))
        assert re.search(
            r"Traceback \(most recent call last\).*\/tests\/test_logger\.py.*in test"
            + r"_tuple_exception_formatting.*KeyError: 'INCORRECT'",
            trace_wo_newline,
        )

    @staticmethod
    def test_uninitialized_logger_raises_an_error():
        with pytest.raises(RuntimeError):  # TODO: better error
            info("test")

    @staticmethod
    def test_multiple_logger_initialization_raises_an_error():
        with pytest.raises(RuntimeError):  # TODO: better error
            logging.getLogger(MOCK_SERVICE + "a")
            initialize(MOCK_SERVICE + "a", "DEBUG")

    @staticmethod
    def test_multiple_logger_initialisation_raises_an_error():
        with pytest.raises(RuntimeError):  # TODO: better error
            initialize(MOCK_SERVICE, "DEBUG")
            get_logger().__class__(MOCK_SERVICE + "2")

    @staticmethod
    def test_logger_service_cannot_be_reinitialised():
        with pytest.raises(RuntimeError):  # TODO: better error
            initialize(MOCK_SERVICE, "DEBUG")
            initialize(MOCK_SERVICE + "2", "INFO")

    @staticmethod
    def test_only_logge_object_exists():
        initialize(MOCK_SERVICE, "DEBUG")
        logger = get_logger()
        logger2 = get_logger().__class__(MOCK_SERVICE)
        assert id(logger) == id(logger2)

    @staticmethod
    def test_merging_dictionaries_in_mdc(capsys):
        initialize(MOCK_SERVICE, "DEBUG")
        log_msg = copy.deepcopy(MOCK_LOGGED_MESSAGE)
        dictionary = {"param_b": "bb", "param_c": "cc"}
        get_logger().mdc()["dict"] = {"param_a": "aa"}
        debug(dict=dictionary, message=MOCK_MESSAGE)
        log_msg["dict"] = {"param_a": "aa", "param_b": "bb", "param_c": "cc"}
        out, _ = capsys.readouterr()
        assert out[:-1] == json.dumps(sort_dict(log_msg))  # [:-1] removes the newline

    @staticmethod
    def test_protected_mdc_field_raises_an_error():
        initialize(MOCK_SERVICE, "DEBUG")
        with pytest.raises(ValueError):
            with get_logger().add_mdc(message="alternative message"):
                pass

    @staticmethod
    def test_logger_raises_error_for_incorrect_log_level():
        with pytest.raises(ValueError):
            initialize(MOCK_SERVICE, "nonsence")


class TestLoggingInUTC:
    @staticmethod
    def test_logging_in_utc(capsys):
        initialize("test", "DEBUG")
        info("message")
        out, _ = capsys.readouterr()
        logged_timestamp = datetime.strptime(json.loads(out)["timestamp"], "%Y-%m-%dT%H:%M:%S.%f%z")
        current_timestamp = datetime.now(timezone.utc)
        assert current_timestamp.timestamp() - logged_timestamp.timestamp() < 10
