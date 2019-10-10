import traceback


def _sanitize_stacktrace_for_json_fields(type, value, tb) -> str:
    return "".join(traceback.format_exception(type, value, tb))
