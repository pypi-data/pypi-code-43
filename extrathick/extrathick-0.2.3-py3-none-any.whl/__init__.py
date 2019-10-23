import os
import logging
import steov

def anonify (obj):
    if isinstance(obj, dict):
        return steov.Anon({k: anonify(v) for k, v in obj.items()})
    if isinstance(obj, (list, set, tuple)):
        return type(obj)(map(anonify, obj))
    return obj

def unanonify (obj):
    if isinstance(obj, steov.Anon):
        obj = vars(obj)
    if isinstance(obj, dict):
        return {k: unanonify(v) for k, v in obj.items()}
    if isinstance(obj, (list, set, tuple)):
        return type(obj)(map(unanonify, obj))
    return obj


def dictstat (st):
    return {attr: getattr(st, "st_"+attr) for attr in [
        "mode",
        "ino",
        "dev",
        "nlink",
        "uid",
        "gid",
        "size",
        "atime",
        "mtime",
        "ctime",
    ]}

def anonstat (st):
    return steov.Anon(dictstat(st))



# http://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
class memoized:
    """
    Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    """
    def __init__ (self, function):
        self._function = function
        self._cache = dict()

    def __call__ (self, *args):
        import collections
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self._function(*args)
        if args in self._cache:
            return self._cache[args]
        else:
            value = self._cache[args] = self._function(*args)
            return value

    def reload (self):
        self._cache.clear()

    # TODO I don't understand this just yet. look up python descriptors
    def __get__ (self, obj, objtype):
        import functools
        """Support instance methods."""
        return functools.partial(self.__call__, obj)



@memoized
def _get_dt_pattern ():
    import re
    return re.compile(r"\A(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6})(\d{3})(?:([\+\-]\d{2}):(\d{2}))?\Z")

_dt_fmt = "%Y-%m-%dT%H:%M:%S.%f"
def dt_serialize (dt):
    fmt = _dt_fmt
    if dt.tzinfo is None:
        tz = ""
    else:
        hours, minutes = divmod(int(dt.utcoffset().total_seconds()/60.0), 60)
        tz = "{hours:+03}:{minutes:02}".format(**locals())
    return "{dt:{fmt}}000{tz}".format(**locals())

def dt_deserialize (dt_str):
    from datetime import datetime, timedelta, timezone
    m = _get_dt_pattern().search(dt_str)
    if not m:
        error = ValueError("dt_str: incorrect format. must match regex: " + _get_dt_pattern().pattern)
        error.dt_str = dt_str
        raise error
    dt_str, nanosec_str, hours_str, minutes_str = m.groups()
    dt = datetime.strptime(dt_str, _dt_fmt)
    if hours_str:
        dt = dt.replace(tzinfo=timezone(timedelta(hours=int(hours_str), minutes=int(minutes_str))))
    return dt



def json_default (obj):
    if isinstance(obj, bytes):
        import base64
        return base64.b64encode(obj).decode("ascii")
    import datetime
    if isinstance(obj, datetime.datetime):
        return dt_serialize(obj)
    if isinstance(obj, datetime.date):
        return obj.strftime("%Y-%m-%d")
    if isinstance(obj, datetime.time):
        # TODO copy/pasted from dt_serialize lol
        if obj.tzinfo is None:
            tz = ""
        else:
            hours, minutes = divmod(int(obj.utcoffset().total_seconds()/60.0), 60)
            tz = f"{hours:+03}:{minutes:02}"
        return f"{obj:%H:%M:%S.%f}000{tz}"
    if isinstance(obj, datetime.timedelta):
        return obj.total_seconds()
    import uuid
    if isinstance(obj, uuid.UUID):
        return str(obj)
    import decimal
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")



def safecall (function, *args, **kwargs):
    try:
        value = function(*args, **kwargs)
    except Exception as ex:
        return False, (ex, steov.format_exc())
    else:
        return True, value

def passthru (function, *args, **kwargs):
    return function(*args, **kwargs)

def always (value):
    def factory (*args, **kwargs):
        return value
    return factory

def _logging_format_time (self, record, datefmt=None):
    import datetime
    created_utc = datetime.datetime.utcfromtimestamp(record.created)
    if datefmt is not None:
        return created_utc.strftime(datefmt)
    else:
        return dt_serialize(created_utc) + "Z"

def logging_basic_config (logfile, level=logging.DEBUG):
    from os import makedirs
    from os.path import abspath, dirname
    makedirs(dirname(abspath(logfile)), exist_ok=True)
    logging.Formatter.formatTime = _logging_format_time
    logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s %(thread)d %(message)s", level=level, filename=logfile)

def logging_adv_config (dir, name, file_level=logging.DEBUG, console_level=logging.INFO):
    from os import makedirs
    from os.path import abspath, dirname, join
    from datetime import datetime as dt
    from logging.config import dictConfig
    dir = abspath(dir)
    if "/" in name:
        raise ValueError("name must not be a path containing parent directories")
    file = join(dir, name + ".log." + dt.utcnow().strftime("%Y-%m-%d"))
    makedirs(dir, exist_ok=True)
    logging.Formatter.formatTime = _logging_format_time

    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "full": {
                "format": "%(asctime)s %(levelname)s %(name)s %(thread)d %(message)s",
            },
            "simple": {
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "file": {
                # TODO someday, make this a proper rotating file handler
                "class": "logging.FileHandler",
                "filename": file,
                "level": file_level,
                "formatter": "full",
                "encoding": "utf-8",
            },
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
                "level": console_level,
                "formatter": "simple",
            },
        },
        "root": {
            "handlers": [
                "file",
                "console",
            ],
            "level": min(file_level, console_level),
        },
    })

def log_exception (logger, level, label, exception, stacktrace=None):
    if label is not None:
        prefix = label + "."
    else:
        prefix = ""
    if stacktrace is None:
        stacktrace = steov.format_exc(1)
    for line in stacktrace.splitlines(keepends=False):
        logger.log(level, prefix + "stacktrace.line: " + line)
    for k, v in getattr(exception, "__dict__", {}).items():
        logger.log(level, prefix + "exception." + k + ": " + ascii(v))

def get_type_name (t):
    return t.__module__ + "." + t.__name__

def get_function_name (f):
    if not callable(f):
        raise TypeError("Not callable: " + str(f))
    try:
        module = f.__module__
        if module is None:
            return get_type_name(type(f.__self__)) + "." + f.__name__
        if module == "__main__":
            prefix = ""
        else:
            prefix = module + "."
        return prefix + f.__qualname__
    except Exception as ex:
        log_exception(logging.getLogger(__name__), logging.WARN, "get_function_name", ex)
        return str(f)

def trace (logger, level, exception_level, function, *args, **kwargs):
    import os
    import types
    if exception_level is None:
        exception_level = level

    self = getattr(function, "__self__", None)

    params_as_strings = []
    if self is not None and not isinstance(self, types.ModuleType):
        params_as_strings.append(ascii(self))
    params_as_strings.extend(map(ascii, args))
    params_as_strings.extend(key+"="+ascii(value) for key, value in kwargs.items())

    logger.log(level, "fcall.start: %s(%s)", get_function_name(function), ", ".join(params_as_strings))
    try:
        before = os.times()[-1]
        retval = function(*args, **kwargs)
        after = os.times()[-1]
    except Exception as ex:
        log_exception(logger, exception_level, "fcall", ex)
        raise
    else:
        logger.log(level, "fcall.elapsed: %f", after - before)
        # TODO maybe if retval is a generator or stream, wrap it in a tracer?
        logger.log(level, "fcall.retval: %a", retval)
        return retval
    finally:
        logger.log(level, "fcall.finish")

def groupby (iterable, key_func=steov.iden):
    import collections
    retval = collections.defaultdict(list)
    for item in iterable:
        retval[key_func(item)].append(item)
    return retval

# returns: decorator `d`. `d` is meant to be applied to a function `g`, such
# that the result of `g(...)` will be passed to `d`, and result of *that* will
# be returned. Good for doing filtering of sorts
def post (f):
    def d (g):
        def new_g (*args, **kwargs):
            return f(g(*args, **kwargs))
        return new_g
    return d

class IteratorStream:
    _linesep = os.linesep.encode()
    def __init__ (self, iterable):
        self._iterator = iter(iterable)
        self._buffer = b""
        self._done = False
        self._closed = False

    def __enter__ (self):
        if self._closed:
            raise ValueError("I/O operation on closed stream.")
        return self

    def read (self, size=None):
        if self._closed:
            raise ValueError("I/O operation on closed stream.")
        if self._done and not self._buffer:
            return b""
        if size is None:
            condition = lambda: True
        else:
            condition = lambda: not self._buffer
        while condition():
            try:
                self._buffer += next(self._iterator)
            except StopIteration:
                self._done = True
                break
        if size is None:
            retval = self._buffer
            self._buffer = b""
        else:
            retval = self._buffer[:size]
            self._buffer = self._buffer[size:]
        return retval

    def readline (self):
        if self._closed:
            raise ValueError("I/O operation on closed stream.")
        if self._done and not self._buffer:
            return b""
        while True:
            retval, linesep, buffer = self._buffer.partition(self._linesep)
            if linesep:
                retval += linesep
                break
            try:
                self._buffer += next(self._iterator)
            except StopIteration:
                self._done = True
                break
        self._buffer = buffer
        return retval

    def __exit__ (self, type, value, traceback):
        self.close()

    def close (self):
        self._closed = True

# nabbed from the OG steve.py lololol

_ch = list(reversed([ # remember: we're going largest to smallest unit
    ("second",  1),
    ("minute",  1 * 60),
    ("hour",    1 * 60 * 60),
    ("day",     1 * 60 * 60 * 24),
   #("week",    1 * 60 * 60 * 24 * 7),
    ("month",   1 * 60 * 60 * 24 * 30),
    ("year",    1 * 60 * 60 * 24 * 365),
]))
def _timedelta_approx (delta):
    # assumes delta >= 0
    sec = delta.total_seconds()
    if sec < 1.0:
        return ("microsecond", int(sec * 1000000)) # one million
    sec = float(int(sec))
    for unit, units_per_sec in _ch:
        quantity_f = sec / units_per_sec
        if quantity_f >= 1.0:
            return (unit, int(quantity_f))

_cchh = {
    "week":    7,
    "month":  30,
    "year":  365,
}
def _approx_2_timedelta (unit, quantity):
    # does NOT assume quantity >= 0
    import datetime
    units_per_day = _cchh.get(unit)
    if units_per_day:
        unit = "day"
        quantity *= units_per_day
    return datetime.timedelta(**{unit+"s": quantity})

_tinies = {
    "microsecond": "\u00b5s",
    "month": "mo",
}
def _tiny_approx_2_str (unit, quantity):
    return format(quantity, ",") +  _tinies.get(unit, unit[0])
def _full_approx_2_str (unit, quantity):
    return format(quantity, ",") + " " + (unit if quantity == 1 else unit+"s")

_approx_formatters = {
    "tiny": (_tiny_approx_2_str, " "),
    "full": (_full_approx_2_str, ", "),
}

_td0 = None
def timedelta_format (delta, formatter="full", levels=1, texts=("ago", "just now", "from now")):
    global _td0
    import datetime
    _td0 = _td0 or datetime.timedelta(0)
    past, present, future = texts
    adelta = abs(delta)
    approxes = []
    for _ in range(levels):
        unit, quantity = _timedelta_approx(adelta)
        if quantity == 0:
            break
        approxes.append((unit, quantity))
        extra = _approx_2_timedelta(unit, quantity)
        adelta -= extra
    if not approxes:
        return present
    if delta < _td0:
        suffix = past
    else:
        suffix = future
    # if formatter is not in _approx_formatters, assume it is callable
    formatter_function, sep = _approx_formatters.get(formatter, formatter)
    return sep.join(formatter_function(u, q) for u, q in approxes) + " " + suffix
