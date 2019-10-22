
from celery import Celery


def get_active_tasks_id(app: Celery):
    ping = app.control.inspect().ping()
    if ping is None:
        return None

    workers = ping.keys()
    i = app.control.inspect(list(workers))
    ids = []

    for key, tasks in i.active().items():
        ids += [task['id'] for task in tasks]

    for key, tasks in i.reserved().items():
        ids += [task['id'] for task in tasks]

    for key, tasks in i.scheduled().items():
        ids += [task['request']['id'] for task in tasks]

    return ids
