import logging
from easilyb.json_min_db import JsonMinConnexion
from threading import Lock

logger = logging.getLogger(__name__)
NOTHING = object()


def get_config_path(filename='config.yaml', appname=None, appauthor=None, appversion=None,
                    dirpath=None, app_root_config=None, user_config=None, system_config=None,
                    approot_config_dirname='config'):
    from os.path import join, dirname

    # There are 4 options for dirpath:
    #   0- given in dirpath argument
    #   1- application root dir
    #   2- user config dir
    #   3- system config dir
    if dirpath is None:
        if app_root_config is False and user_config is False and system_config is False:
            raise ValueError("Required one of: app_root_config, user_config, and system_config be True or None")
        if app_root_config is True or not (user_config or system_config):
            import sys
            dirpath = join(dirname(sys.modules['__main__'].__file__), approot_config_dirname)

        elif user_config is True or not system_config:
            import appdirs
            dirpath = appdirs.user_config_dir(appname, appauthor, appversion)
        else:
            import appdirs
            dirpath = appdirs.site_config_dir(appname, appauthor, appversion)

    return join(dirpath, filename)


class EasyConfig:
    def __init__(self, appname=None, appauthor=None, appversion=None,
                 filename=None, dirpath=None, app_root_config=None, user_config=None,
                 system_config=None,approot_config_dirname='config',
                 filepath=None, create=True, template=None, template_file=None, indent=3, driver="yaml"):
        if filepath is None:
            if filename is None:
                raise ValueError('Argument required: filepath or filename')
            filepath = get_config_path(filename, appname, appauthor, appversion, dirpath,
                                       app_root_config, user_config, system_config,
                                       approot_config_dirname)

        self.db = JsonMinConnexion(filepath, create=create, template=template, template_file=template_file,
                                   indent=indent, driver=driver)
        self._lock = Lock()
        self._save = True

    def get(self, key, default=NOTHING, set_default=True, save=True):
        try:
            return self.db[key]
        except:
            if default == NOTHING:
                raise KeyError(key)
            else:
                if set_default:
                    self.set(key, default, save=save)
                return default

    def set(self, key, value, save=True):
        if self._save:
            with self._lock:
                self.db[key] = value
                if save:
                    self.db.save()
        else:
            self.db[key] = value

    def save(self):
        self.db.save()

    def __enter__(self):
        self._lock.acquire()
        self._save = False
        self.db.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.db.__exit__(exc_type, exc_val, exc_tb)
        finally:
            self._save = True
            self._lock.release()
