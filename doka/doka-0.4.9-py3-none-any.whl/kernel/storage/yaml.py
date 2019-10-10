import yaml

dumper = yaml.dumper.SafeDumper
dumper.ignore_aliases = lambda self, data: True
dumper.add_representer(type(None), lambda self, _: self.represent_scalar('tag:yaml.org,2002:null', ''))


class YamlStorage:
    _APPEND_MODE = 'append'
    _SET_MODE = 'set'

    def __init__(self, file):
        self._compose_file = file
        self._data = self.read()
        self._change_node_mode = None

    def set(self, index, value):
        self._change_node_mode = self._SET_MODE
        self._change_node(index, value, self._data)

    def append(self, index, value):
        self._change_node_mode = self._APPEND_MODE
        self._change_node(index, value, self._data)

    def get(self, index):
        data = self._data
        if index:
            for p in index.split('.'):
                data = data.get(p)
                if not data:
                    return None
        return data

    def remove(self, index):
        self._remove_node(index, self._data)

    def read(self):
        with open(self._compose_file, 'rt') as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    def write(self, file=None):
        file = file or self._compose_file
        with open(file, 'wt') as f:
            yaml.dump(self._data, f, default_flow_style=False, sort_keys=False, Dumper=dumper)

    def _remove_node(self, index, node):
        keys = index.split(".")
        key = keys.pop(0)
        if len(keys) == 1:
            node[key] = None
            return
        self._remove_node(".".join(keys), node.get(key))

    def _change_node(self, index, value, node):
        keys = index.split(".")
        key = keys.pop(0)
        if keys:
            if key == '*':
                for _, _node in node.items():
                    self._change_node(".".join(keys), value, _node)
            else:
                self._change_node(".".join(keys), value, node.get(key))
        else:
            if self._change_node_mode == self._APPEND_MODE and isinstance(node.get(key), list):
                if not isinstance(value, list):
                    value = [value]
                node[key] += value
            elif self._change_node_mode == self._APPEND_MODE and \
                    isinstance(node.get(key), dict) and isinstance(value, dict):
                node[key] = {**node[key], **value}
            else:
                node[key] = value
