from os import path, environ, makedirs
import yaml
import platform
from typing import Dict

if platform.system() == "Windows":
    HOME = environ.get("HOMEPATH")
    SETTINGS_FOLDER = path.join(environ.get("APPDATA"), "beadpull")
else:
    HOME = environ.get("HOME")
    XDG_CONFIG_HOME = environ.get("XDG_CONFIG_HOME")
    if XDG_CONFIG_HOME is None:
        XDG_CONFIG_HOME = path.join(HOME, ".config")
    SETTINGS_FOLDER = path.join(XDG_CONFIG_HOME, "beadpull")


def _load(packagedir: str, name: str) -> Dict:
    """load settings from YAML

    Settings are either packagedir/name/defaults.yaml
    or SETTINGS_FOLDER/name.yaml"""
    sfile = path.join(SETTINGS_FOLDER, name + ".yaml")
    if not path.exists(sfile):
        sfile = path.join(packagedir, name, "defaults.yaml")
    defaults = yaml.load(open(sfile, "r"), Loader=yaml.FullLoader)
    return defaults


def _save(name: str, defaults: Dict) -> bool:
    """save settings to YAML

    Settings are saved to SETTINGS_FOLDER/name.yaml"""
    sfile = path.join(SETTINGS_FOLDER, name + ".yaml")
    try:
        if not path.exists(SETTINGS_FOLDER):
            makedirs(SETTINGS_FOLDER, exist_ok=True)
        with open(sfile, "w") as f:
            f.write(yaml.dump(defaults))
        return True
    except PermissionError:
        return False


def load_defaults_motor(basedir: str) -> Dict:
    return _load(basedir, "motor")


def save_defaults_motor(defaults: Dict) -> bool:
    return _save("motor", defaults)


def load_defaults_analyzer(basedir: str) -> Dict:
    return _load(basedir, "analyzer")


def save_defaults_analyzer(defaults: Dict) -> bool:
    return _save("analyzer", defaults)


def load_defaults_ui(basedir: str) -> Dict:
    return _load(basedir, "ui")


def save_defaults_ui(defaults: Dict) -> bool:
    return _save("ui", defaults)


def load_defaults_equation(basedir: str) -> Dict:
    return _load(basedir, "equation")


def save_defaults_equation(defaults: Dict) -> bool:
    return _save("equation", defaults)
