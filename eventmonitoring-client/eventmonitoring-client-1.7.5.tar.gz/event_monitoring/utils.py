import requests


def notify_telegram(system_name: str, name: str, desc: str, trb: str) -> None:
    """
    :param system_name: str
    :param name: str
    :param desc: str
    :param trb: str
    :return: None
    """
    data = {"system_name": system_name, "name": name, "desc": desc, "trb": trb}
    url = "https://2lme7p5k92.execute-api.eu-west-2.amazonaws.com/em_notifier/listener"
    try:
        _ = requests.post(url, json=data)
    except ConnectionError:
        pass


def _create_name(keys: any, data: dict) -> str:
    """
    :param keys: str or list/tuple
    :param data: dict
    :return: str
    """
    name = ""
    if isinstance(keys, str):
        name = f"{keys}:{data[keys]}"
    elif isinstance(keys, (list, tuple)):
        for k in keys:
            if name:
                name = f"{name}, {k}:{data[k]}"
            else:
                name = f"{k}:{data[k]}"
    return name


# CREATE EVENT data
def get_list_values(keys: any, description_key: str, list_value: str,
                    iter_key: str, var_names: list, *args, **kwargs) -> dict:
    """
    :param keys: str or list/tuple
    :param description_key: str
    :param list_value: string
    :param iter_key: string
    :param var_names: list
    :param args: tuple
    :param kwargs: dict
    :return: dict
    """
    description = ""
    name = ""
    # prepare title and description
    if list_value in kwargs and iter_key in kwargs:
        list_ = kwargs[list_value]
        index = kwargs[iter_key]
        data = list_[index]
        name = _create_name(keys, data)
        if description_key in kwargs:
            description = kwargs[description_key]
    elif list_value in var_names and iter_key in var_names:
        list_ = args[var_names.index(list_value)]
        index = args[var_names.index(iter_key)]
        data = list_[index]
        name = _create_name(keys, data)
        if description_key in var_names:
            description = args[var_names.index(description_key)]
    return {"name": name, "description": description}


# for creating default name
def get_values(keys: any, var_names: list, *args, **kwargs) -> dict:
    """
    :param keys: str or list/tuple
    :param var_names: list
    :param args: tuple
    :param kwargs: dict
    :return: dict
    """
    name = ""
    if isinstance(keys, str):
        if keys in kwargs:
            name = f"{keys}:{kwargs[keys]}"
        elif keys in var_names:
            name = args[var_names.index(keys)]
        else:
            name = keys
    else:
        for key in keys:
            if key in kwargs:
                value = kwargs[key]
            elif key in var_names:
                value = args[var_names.index(key)]
            if name:
                name = f"{name}, {key}:{value}"
            else:
                name = f"{key}:{value}"
    return {"name": name}


def create_event_name(keys, values: any = None, key: any = None) -> str:
    """
    :param keys: str or list/tuple
    :param values: dict or list None
    :param key: int or None
    :return: str
    """
    if isinstance(values, list) and isinstance(key, int):
        data = values[key]
    else:
        data = values
    try:
        return get_values(keys, [], **data)["name"]
    except IndexError:
        pass


class ColorPrint:
    # Foreground:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    # Formatting
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    # End colored text
    END = "\033[0m"
    NC = "\x1b[0m"  # No Color


def _check_lambda_args(args):
    for arg in args:
        if arg.__class__.__name__ == "LambdaContext":
            return tuple()
    return args
