import logging
import requests
import json
from django.core.management import call_command
from django.conf import settings

logger = logging.getLogger(__name__)


class Proxy(object):
    def __init__(self, method):
        self._method = method

    def __call__(self, *args, **kwargs):
        self._method(*args, **kwargs)

    def delay(self, *args, **kwargs):
        task_name = f"{self._method.__module__}.{self._method.__name__}"
        arguments = json.dumps({"args": args, "kwargs": kwargs})
        command_args = [task_name, f"'{arguments}'"]

        if getattr(settings, "DEFERRED_TASKS_ALWAYS_EAGER", False):
            call_command("deferred_task", task_name, arguments)
            logger.debug("Running method synchronously %s", self._method.__name__)
        else:
            arguments_separated = " ".join(command_args)
            request_kwargs = {
                "url": f"https://api.heroku.com/apps/{settings.HEROKU_APP_NAME}/dynos",
                "headers": {
                    "Accept": "application/vnd.heroku+json; version=3",
                    "Authorization": f"Bearer {settings.HEROKU_API_KEY}",
                },
                "json": {
                    "size": "hobby",
                    "time_to_live": 60 * 60 * 15,  # 15 minutes before cancelling (max is 24)
                    "type": "run",
                    "command": f"./manage.py deferred_task {arguments_separated}",
                },
            }
            if settings.DEBUG:
                logger.debug(
                    "Mock run method asynchronously %s %s",
                    self._method.__name__,
                    json.dumps(request_kwargs),
                )
            else:
                logger.debug("Running method asynchronously %s", self._method.__name__)
                response = requests.post(**request_kwargs)
                response.raise_for_status()


def shared_task(f):
    return Proxy(f)
