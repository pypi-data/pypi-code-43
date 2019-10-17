import os
from builtins import FileNotFoundError
from pathlib import Path

from settingscascade import ElementSchema, SettingsManager
from toml import TomlDecodeError, loads

from rye.default_config import default


class Task(ElementSchema):
    isolate: bool
    target_environments: list
    commands: list


class Environment(ElementSchema):
    python: str
    location: list
    depends_files: list
    setup_commands: list
    create_command: list
    install_command: list
    clean_existing: bool


def pyproject():  # pragma: no cover
    file_location = os.environ.get("RYE_FILE", "pyproject.toml")
    try:
        return loads(Path(file_location).read_text())["tool"]["rye"]
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find config file at {file_location}")
    except TomlDecodeError:
        raise FileNotFoundError(f"File at {file_location} is invalid toml")
    except KeyError:
        raise FileNotFoundError(
            f"File at {file_location} does not contain a 'tool.rye' secion"
        )


def list_to_path(parts):
    return Path(*parts)


def join(args):
    sep, *terms = args
    return sep.join([term for term in terms if term])


def current_venv(_):
    try:
        return os.environ["VIRTUAL_ENV"]
    except KeyError:  # pragma: no cover
        raise RuntimeError(
            "You used the current_venv function "
            "without an activated virtual environment"
        )


def get_config(data=None):
    config = SettingsManager(data or [default, pyproject()], [Task, Environment])
    config.add_filter("list_to_path", list_to_path)
    config.add_filter("join", join)
    config.add_filter("current_venv", current_venv)
    return config
