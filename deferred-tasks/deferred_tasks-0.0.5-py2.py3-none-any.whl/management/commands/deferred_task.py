import json
from importlib import import_module

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Run deferred task."

    def add_arguments(self, parser):
        parser.add_argument("method", nargs="+", type=str)
        parser.add_argument("argkwargs", nargs="+", type=str)

    def handle(self, *args, **options):
        method_components = options["method"][0]
        module_name, method_name = method_components.rsplit(".", 1)
        argkwargs = json.loads(options["argkwargs"][0])

        args = argkwargs.get("args", [])
        kwargs = argkwargs.get("kwargs", {})

        module = import_module(module_name)
        method = getattr(module, method_name)
        return_value = method(*args, **kwargs)

        if not settings.UNIT_TESTING:
            self.stdout.write(
                self.style.SUCCESS(
                    "Ran task: {}, Result: {}".format(method_name, return_value)
                )
            )
