import os
import yaml
import prettytable as pt

class ConfMgr(object):

    CONFIG_FILE = os.path.join(os.path.expanduser('~'), '.mcutk')

    @classmethod
    def load(cls):
        return cls(cls.CONFIG_FILE)


    def __init__(self, path):
        self._path = path
        self.is_empty = True

        if not os.path.exists(path):
            self._data = dict()
        else:
            with open(path, 'r') as stream:
                self._data = yaml.safe_load(stream)
            self.is_empty = False

        if 'apps' not in self._data:
            self._data['apps'] = dict()

        if not isinstance(self._data['apps'], dict):
            self._data['apps'] = dict()


    def apps(self):
        return self._data['apps']


    def get_app(self, name):
        return self._data['apps'].get(name)


    def get_apps(self):
        return self._data['apps']


    def set_app(self, app):
        assert app.name
        info = {
            'path': str(app.path),
            'version': str(app.version)
        }
        self._data['apps'][app.name] = info

    def __str__(self):
        return str(self._data)


    def save(self):
        with open(self._path, 'w') as file:
            yaml.dump(self._data, file, default_flow_style=False)

    def show(self):
        print(yaml.dump(self._data, default_flow_style=False))
