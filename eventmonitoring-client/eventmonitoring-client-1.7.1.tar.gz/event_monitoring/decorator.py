import os
import traceback

from .utils import get_list_values, get_values, ColorPrint, _check_lambda_args
from .event import Event


def event(keys=None, description_key=None, custom_description=None, list_value=None, iter_key=None):
    def decorator(function, *args, **kwargs):
        def push_function_results(*args, **kwargs):
            pushed = False
            name = ""
            description = ""
            var_names = function.__code__.co_varnames
            init_kwargs = {
                "system_name": os.environ.get("SYSTEM_EVENT_NAME", ""),
                "system_url": os.environ.get("SYSTEM_EVENT_URL", ""),
                "execute_token": os.environ.get("SYSTEM_EVENT_TOKEN", ""),
                "em_notifier": os.environ.get("SYSTEM_EM_NOTIFIER", False),
                "debug": os.environ.get("SYSTEM_EM_NOTIFIER", False),
            }
            event = Event(**init_kwargs)
            try:
                if list_value:
                    list_values = get_list_values(
                        keys, description_key, list_value, iter_key, var_names, *args, **kwargs
                    )
                    name = list_values["name"]
                    description = list_values["description"]
                elif keys is not None:
                    values = get_values(keys, var_names, *args, **kwargs)
                    name = values["name"]

                if not description and custom_description:
                    description = custom_description

                pushed = True
                if not name:
                    name = function.__name__
                    description = function.__doc__ or function.__name__
                event.push_to_event(name=name, description=description, status=False)
            except IndexError:
                pass
            # print(pushed)
            try:
                args = _check_lambda_args(args)
                if args or kwargs:
                    func_result = function(*args, **kwargs)
                else:
                    func_result = function()
            except Exception as exc_description:
                t = traceback.format_exc()
                t = t.replace("func_result = function", function.__name__)
                return event.log_exception(name, description=str(exc_description), trb=t)
            if pushed:
                event.push_to_event(name=name, description=description, status=True)
            return func_result
        return push_function_results
    return decorator

