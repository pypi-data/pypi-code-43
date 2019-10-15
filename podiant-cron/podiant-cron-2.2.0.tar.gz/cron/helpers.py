from django.conf import settings
from imp import find_module
from importlib import import_module
import django_rq
import rq_scheduler


def build_cron_string(minutes=None, hours=None, days=None, months=None, weekday=None):
    if hours is not None:
        if minutes is None:
            minutes = 0

    if days is not None:
        if hours is None:
            hours = 0

            if minutes is None:
                minutes = 0

    if months is not None:
        if days is None:
            days = 1

            if hours is None:
                hours = 0

                if minutes is None:
                    minutes = 0

    return ' '.join(
        (
            minutes is None and '*' or str(minutes),
            hours is None and '*' or str(hours),
            days is None and '*' or str(days),
            months is None and '*' or str(months),
            weekday is None and '*' or str(weekday)
        )
    )


def get_scheduler(queue_name=None):
    return rq_scheduler.Scheduler(
        queue_name=queue_name or 'default',
        connection=django_rq.get_connection()
    )


def autodiscover(schedule=False):
    for app in settings.INSTALLED_APPS:
        import_module(app)
        name = '%s.cron' % app

        try:
            import_module(name)
        except ImportError as ex:
            try:
                find_module(name)
            except ImportError:
                continue

            raise ex  # pragma: no cover

    if schedule:
        from .registry import jobs

        jobs.schedule()
