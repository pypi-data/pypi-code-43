import json
import logging

from .utils import _sanitize_stacktrace_for_json_fields


class ConsoleFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        level = record.levelname
        timestamp = self.formatTime(record, "%H:%M:%S")
        message = record.getMessage()
        extra_fields = self._extract_extra_fields(record)
        extra_txt = " ".join([f"{k}={v}" for k, v in extra_fields.items()])
        funcname = f"{record.module}.{record.funcName}"

        return f"[{level}] -- {timestamp} :: (#{funcname}) :: {message} [{extra_txt}]"

    def _extract_extra_fields(self, record: logging.LogRecord) -> dict:
        dummy_record = logging.LogRecord(*["dummy"] * 7)
        default_fields = dummy_record.__dict__.keys()
        return {k: v for k, v in record.__dict__.items() if k not in default_fields}


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        json_dict = {}

        if record.exc_info:
            json_dict["stack_trace"] = _sanitize_stacktrace_for_json_fields(
                *record.exc_info
            )

            # mark exception info as none to consume the exception here and stop propogation
            # where it might get logged to sys.stderr.
            # If we need to reraise it we can log it as an exception on the root logger
            record.exc_info = None

        json_dict.update(record.__dict__)

        # Already replaced this with 'stack_trace', no longer needed
        assert json_dict["exc_info"] is None
        del json_dict["exc_info"]

        # We don't need these 2 fields as message field has msg % args now
        json_dict["message"] = record.getMessage()
        del json_dict["msg"]
        del json_dict["args"]

        json_dict["level"] = json_dict["levelname"]
        del json_dict["levelname"]

        try:
            return json.dumps(json_dict)
        except (TypeError, OverflowError):
            return json.dumps(
                {"message": "An unrecoverable exception occured while logging"}
            )
