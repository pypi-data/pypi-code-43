from threading import RLock as Lock
import os
import easilyb.json_serialize as jsons
import json
import yaml
from collections import MutableMapping

TREE_DB_META_TEMPLATE = {}


def _load_json(path, driver=jsons):
    with open(path) as fin:
        return driver.load(fin)


def _save_json(data, path, indent=None, driver=jsons):
    with open(path, 'w') as fou:
        if driver == yaml:
            driver.dump(data, fou, indent=indent, default_flow_style=False)
        else:
            driver.dump(data, fou, indent=indent)


class JsonMinConnexion:
    """Minimalistic Json Database Connexion class."""

    def __init__(self, path, create=True, template=None, template_file=None, indent=3, readonly=False, driver="jsons",
                 load=True):
        """JsonMinDb constructor.

        :param path: json file path.
        :type path: str.
        :param create: Create if json file does not exist.
        :type create: bool.
        :param template: if create is True, create from template.
        :type template: dict.
        :param template_file: if create is True and template is None, create from template_file.
        :type template_file: str.
        :param indent: if create is True, create from template.
        :type indent: int.
        :raises: ValueError

        """
        self.path = path
        self.indent = indent
        self.readonly = readonly
        self.lock = Lock()
        self.db = None
        if driver == "json":
            self.driver = json
        elif driver == "yaml":
            self.driver = yaml
        elif driver == "jsons" or driver == "json_serialize":
            self.driver = jsons
        else:
            raise ValueError("Unkown driver: %s!" % driver)
        if not os.path.isfile(path):
            if create:
                if template:
                    _template = template
                elif template_file:
                    _template = _load_json(template_file, driver=self.driver)
                else:
                    _template = {}

                _save_json(_template, path, indent=indent, driver=self.driver)
                if load:
                    self.db = _load_json(path, driver=self.driver)
            else:
                raise ValueError("Database file doesn't exist: " + path)
        if load:
            self.db = _load_json(path, driver=self.driver)

    def __contains__(self, k):
        self._load_if_not_loaded()
        return self.db.__contains__(k)

    def __delitem__(self, k):
        self._load_if_not_loaded()
        return self.db.__delitem__(k)

    def __getitem__(self, k):
        self._load_if_not_loaded()
        return self.db.__getitem__(k)

    def __iter__(self):
        self._load_if_not_loaded()
        return self.db.__iter__()

    def __len__(self):
        self._load_if_not_loaded()
        return self.db.__len__()

    def __setitem__(self, k, o):
        self._load_if_not_loaded()
        return self.db.__setitem__(k, o)

    def items(self):
        self._load_if_not_loaded()
        return self.db.items()

    def keys(self):
        self._load_if_not_loaded()
        return self.db.keys()

    def update(self):
        self._load_if_not_loaded()
        return self.db.update()

    def values(self):
        self._load_if_not_loaded()
        return self.db.values()

    def has_key(self):
        self._load_if_not_loaded()
        try:
            return self.db.has_key()
        except:
            pass

    def _load_if_not_loaded(self):
        with self.lock:
            if self.db is None:
                self.db = _load_json(self.path, driver=self.driver)

    def save(self):
        """updates database persistance file in the disk. """
        if self.readonly:
            raise Exception("Read Only Access!")
        if self.db is None:
            raise Exception("Database is not loaded")
        _save_json(self.db, self.path, indent=self.indent, driver=self.driver)

    def reload(self):
        """reload database from disk."""
        with self.lock:
            self.db = _load_json(self.path, driver=self.driver)
    
    def unload(self):
        with self.lock:
            self.db = None

    def __str__(self):
        return "<kutils.json_min_db.JsonMinConnexion instance %s>" % self.db.__str__()

    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                self.save()
        finally:
            self.lock.release()


class JsonTreeDataBase(MutableMapping):
    def __init__(self, path, create=True, indent=3, readonly=False, driver="jsons"):
        self.path = path
        self.indent = indent
        self.readonly = readonly
        self.lock = Lock()
        self.driver = driver
        self._meta = None
        self._meta_path = os.path.join(self.path, '_meta.'+ self.driver)

        if not os.path.isdir(path):
            if create:
                try:
                    os.mkdir(path)
                    self._meta = JsonMinConnexion(self._meta_path, create=create, template=TREE_DB_META_TEMPLATE,
                                                  indent=indent, readonly=readonly, driver=driver)

                except:
                    # Remove db directory if it was created

                    if os.path.isdir(self.path):
                        try: os.rmdir(self.path)
                        except: pass
                    raise
                finally:
                    pass
            else:
                raise ValueError("Database file doesn't exist: " + path)
        else:
            self._meta = JsonMinConnexion(self._meta_path, create=False, indent=indent, readonly=readonly, driver=driver)


    def __getitem__(self, item):
        pass

    def __setitem__(self, key, value):
        raise Exception('Unimplemented')

    def __delitem__(self, key):
        pass

    def __iter__(self):
        raise Exception('Unimplemented')

    def __len__(self):
        raise Exception('Unimplemented')
