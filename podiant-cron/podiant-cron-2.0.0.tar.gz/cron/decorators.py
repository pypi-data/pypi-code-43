from .helpers import build_cron_string, get_scheduler


def interval(
    minutes=None,
    hours=None,
    days=None,
    months=None,
    weekday=None,
    queue_name=None,
    timeout='30s'
):
    scheduler = get_scheduler(queue_name)
    cron_string = build_cron_string(minutes, hours, days, months, weekday)

    def wrapper(f):
        scheduler.cron(
            cron_string,
            func=f,
            queue_name=queue_name
        )

        return f

    return wrapper


def weekly(weekday=0, queue_name=None, timeout='30s'):
    scheduler = get_scheduler(queue_name)
    cron_string = build_cron_string(weekday=0)

    def wrapper(f):
        scheduler.cron(
            cron_string,
            func=f,
            queue_name=queue_name
        )

        return f

    return wrapper


def daily(queue_name=None, timeout='30s'):
    scheduler = get_scheduler(queue_name)
    cron_string = build_cron_string(hours=0)

    def wrapper(f):
        scheduler.cron(
            cron_string,
            func=f,
            queue_name=queue_name
        )

        return f

    return wrapper


def hourly(queue_name=None, timeout='30s'):
    scheduler = get_scheduler(queue_name)
    cron_string = build_cron_string(minutes=0)

    def wrapper(f):
        scheduler.cron(
            cron_string,
            func=f,
            queue_name=queue_name
        )

        return f

    return wrapper
