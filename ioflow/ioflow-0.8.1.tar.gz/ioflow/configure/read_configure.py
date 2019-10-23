import pprint

from pconf import Pconf
import os

from ioflow.configure.get_configure_path_from_argv import get_configure_path_from_argv


def guess_configure_file_type(file_name):
    file_extension_mapping = {".json": "json", ".yaml": "yaml", ".yml": "yaml"}

    _, file_extension = os.path.splitext(file_name)

    if file_extension in file_extension_mapping:
        return file_extension_mapping[file_extension]

    raise ValueError(file_extension)


def find_best_file_candidate(candidate_list):
    for candidate in candidate_list:
        if os.path.exists(candidate):
            return candidate

    return None


def read_configure(return_empty=False) -> dict:
    # set return_empty to True for not read config from env
    # which can prevent unexpected result
    # e.g. './configure.json' is not for this app, but for other using
    if return_empty:
        return {}

    default_configure_candidate = [
        ".".join(["./configure", ext]) for ext in ["yaml", "yml", "json"]
    ]
    builtin_configure_candidate = [
        ".".join(["./builtin_configure", ext]) for ext in ["yaml", "yml", "json"]
    ]

    default_configure = find_best_file_candidate(default_configure_candidate)
    builtin_configure = find_best_file_candidate(builtin_configure_candidate)

    active_configure_file = get_configure_path_from_argv()
    if not active_configure_file:
        active_configure_file = os.getenv("_DEFAULT_CONFIG_FILE", default_configure)

    builtin_configure_file = os.getenv("_BUILTIN_CONFIG_FILE", builtin_configure)

    # Note: this is a safeguard, before using any Pconf function, do execute this
    # In case former Pconf usage influence current usage
    # which will lead to a hidden and wired bug
    Pconf.clear()

    # disable read configure from environment
    # Pconf.env()

    active_configure_file_abs_path = os.path.realpath(active_configure_file)

    if not os.path.exists(active_configure_file):
        msg = "default configure file is not found! CWD: {}; activate_config: {}; builtin_configure: {}".format(
            os.getcwd(), active_configure_file, builtin_configure_file
        )
        print(msg)
        raise ValueError(msg)
    else:
        print(
            ">>> Using configure read from file: {}".format(
                active_configure_file_abs_path
            )
        )

    file_encoding = guess_configure_file_type(active_configure_file_abs_path)
    Pconf.file(active_configure_file, file_encoding)

    # try loading builtin configure file
    if builtin_configure_file and os.path.exists(builtin_configure_file):
        print("loading builtin configure from {}".format(builtin_configure_file))
        file_encoding = guess_configure_file_type(builtin_configure_file)
        Pconf.file(builtin_configure_file, encoding=file_encoding)
    else:
        print(">>> builtin configure file is not found!")

    # Get all the config values parsed from the sources
    config = Pconf.get()

    # NOTE: clean Pconf for later brand new use
    Pconf.clear()

    print("++" * 8, "configure", "++" * 8)
    pprint.pprint(config)

    return config

    # sys.exit(0)

    # return {
    #     'corpus': {
    #         'train': './data/train.conllz',
    #         'test': './data/test.conllz'
    #     },
    #     'model': {
    #         'shuffle_pool_size': 10,
    #         'batch_size': 32,
    #         'epochs': 20,
    #         'arch': {}
    #      }
    # }


read_config = read_configure  # alias
