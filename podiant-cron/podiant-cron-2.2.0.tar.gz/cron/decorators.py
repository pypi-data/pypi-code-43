from .helpers import build_cron_string
from .registry import jobs


def _register(queue_name, cron_string):
    def wrapper(f):
        jobs.register(f, queue_name, cron_string)
        return f

    return wrapper


def interval(
    minutes=None,
    hours=None,
    days=None,
    months=None,
    weekday=None,
    queue_name=None,
    timeout='30s'
):
    cron_string = build_cron_string(minutes, hours, days, months, weekday)
    return _register(queue_name, cron_string)


def weekly(weekday=0, queue_name=None, timeout='30s'):
    cron_string = build_cron_string(weekday=0)
    return _register(queue_name, cron_string)


def daily(queue_name=None, timeout='30s'):
    cron_string = build_cron_string(hours=0)
    return _register(queue_name, cron_string)


def hourly(queue_name=None, timeout='30s'):
    cron_string = build_cron_string(minutes=0)
    return _register(queue_name, cron_string)
