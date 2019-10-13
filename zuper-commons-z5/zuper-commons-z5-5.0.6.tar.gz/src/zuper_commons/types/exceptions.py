import os
from typing import Callable, ClassVar, Dict, Optional

__all__ = ["ZException", 'ZValueError', 'ZTypeError', 'ZAssertionError',
           'ZNotImplementedError']


class ZException(Exception):
    msg: Optional[str] = None
    info: Optional[Dict[str, object]] = None

    entries_formatter: ClassVar[Callable[[object], str]] = repr

    def __init__(self, msg: Optional[str] = None, **info: object):
        assert isinstance(msg, (str, type(None))), msg
        self.msg = msg
        self.info = info

    def __str__(self) -> str:
        from zuper_commons.text import pretty_dict

        entries = {}
        for k, v in self.info.items():
            # noinspection PyCallByClass
            entries[k] = ZException.entries_formatter(v)
        if not self.msg:
            self.msg = "\n"
        if entries:
            s = pretty_dict(self.msg, entries)
        else:
            s = self.msg

        s = sanitize_circle_ci(s)
        return s

    def __repr__(self) -> str:
        return self.__str__()


def disable_colored() -> bool:
    circle_job = os.environ.get("CIRCLE_JOB", None)
    return circle_job is not None


def sanitize_circle_ci(s: str) -> str:
    if disable_colored():
        from zuper_commons.text.coloring import remove_escapes

        s = remove_escapes(s)
        difficult = ["┋"]
        for c in difficult:
            s = s.replace(c, "")
        return s
    else:
        return s


class ZTypeError(ZException, TypeError):
    pass


class ZValueError(ZException, ValueError):
    pass


class ZAssertionError(ZException, AssertionError):
    pass


class ZNotImplementedError(ZException, NotImplementedError):
    pass
