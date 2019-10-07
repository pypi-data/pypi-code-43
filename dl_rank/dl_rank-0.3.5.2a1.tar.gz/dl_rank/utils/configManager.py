from yaml import SafeDumper
import yaml
from tensorflow import gfile
import os

SafeDumper.add_representer(
    type(None),
    lambda dumper, value: dumper.represent_scalar(u'tag:yaml.org,2002:null', '')
  )

class ConfigManager(object):
    def __init__(self, config_dict=None, **template):
        self._yamls = dict()
        if config_dict is None:
            self.inputConfig(template)
        elif template is None:
            self.inputConfig(config_dict)
        else:
            config_dict.update(template)
            self.inputConfig(config_dict)

    def dumpConfig(self, save_path):
        for yamlName in self._yamls:
            out_path = os.path.join(save_path, yamlName)
            with gfile.GFile(out_path, 'w') as f:
                yaml.safe_dump(self._yamls[yamlName], f, default_flow_style=False)

    def getConfig(self):
        return self._yamls

    def inputConfig(self, template):
        for yamlName, value in template.items():
            self.addYaml(yamlName, value)

    def addYaml(self, yamlName, value):
        if isinstance(value, str):
            with gfile.GFile(value, 'r') as f:
                self._yamls[yamlName] = yaml.load(f, Loader=yaml.FullLoader)
        elif isinstance(value, dict):
            self._yamls[yamlName] = value

    def update(self, input_dict):
        # for each yaml
        for yaml_name, config_dict in input_dict.items():
            # for each {(key1, key2, key3...): value} ...
            for multi_key, value in config_dict.items():
                multi_dict = self._yamls[yaml_name]
                if isinstance(multi_key, str):
                    multi_dict[multi_key] = value
                else:
                    for idx in range(len(multi_key)-1):
                        multi_dict = multi_dict[multi_key[idx]]
                    multi_dict[multi_key[-1]] = value

    def check(self):
        pass



if __name__ == '__main__':
    conf = ConfigManager(f=
                       {'type': 'continuous', 'transform': None, 'parameter':
                           {'normalization': None, 'boundaries': None},
                        'ignore': False, 'scope': ['wide', 'deep']})
    conf.update({'f': {('parameter', 'normalization'): 3, ('transform', ): 5}})
    a = 1
