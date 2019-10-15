from logging import getLogger
from .helpers import build_cron_string, get_scheduler


def _register(queue_name, cron_string):
    scheduler = get_scheduler(queue_name)
    logger = getLogger('podiant.cron')

    def wrapper(f):
        scheduler.cron(
            cron_string,
            func=f,
            queue_name=queue_name
        )

        logger.debug(
            'Scheduled job \'%s\' with cron string \'%s\'' % (
                f.__name__,
                cron_string
            )
        )

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
