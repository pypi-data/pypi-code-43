import getpass
import json
import os

pypi = "https://pypi.org"


def load_settings(args):
    settings = {
        "tag": "default",
        "username": None,
        "api_key": None,
        "index": "https://index.pydist.com",
        "backup_index": pypi,
    }

    # Look in .pydist.json files, with CWD taking priority.
    home = os.environ.get("XDG_HOME") or os.environ.get("HOME")
    home_conf_file = os.path.join(home, ".pydist.json")
    for path in [home_conf_file, ".pydist.json"]:
        if os.path.exists(path):
            try:
                with open(path) as fp:
                    settings.update(json.load(fp))
            except json.decoder.JSONDecodeError:
                pass  # don't load settings if file is corrupt

    # Handle environment variables, which take priority over file settings.
    for setting in settings:
        env_variable = "PYDIST_" + setting.upper()
        if env_variable in os.environ:
            settings[setting] = os.environ[env_variable]

    # Handle command-line arguments, which are highest priority.
    for setting in settings:
        value = getattr(args, setting)
        if value is not None:
            settings[setting] = value
    if args.public:
        settings["index"] = pypi

    if settings["index"] == pypi:
        if settings["username"] is None:
            settings["username"] = input("PyPI username: ")
        # Always prompt for password, since the provided API key is presumably for PyDist.
        # TODO: refactor .pydist.json to save per-index credentials.
        settings["api_key"] = getpass.getpass("PyPI password: ")

    if settings["api_key"] is None and "pydist" in settings["index"]:
        settings["api_key"] = input("PyDist API Key: ")
        yesno = input("Save key in ~/.pydist.json? (y/N): ")
        if yesno.lower() == "y":
            with open(home_conf_file, "w") as fp:
                json.dump(settings, fp, indent=4)

    return settings
