from typing import Dict

from tb.core.exc import TbError


def validate_attribute(app, name: str, flags: str, values: Dict):
    error_msg = "argument {}: invalid choice: '{}' (choose from {})"

    pargs = app.pargs

    if _is_invalid_attribute(pargs, name, values.get):
        raise TbError(error_msg.format(flags,
                                       getattr(pargs, name),
                                       str([r for r in values.keys()])))


def _is_invalid_attribute(obj, field_name, is_valid):
    if not hasattr(obj, field_name):
        return False

    field = getattr(obj, field_name)
    return field and not is_valid(field)
