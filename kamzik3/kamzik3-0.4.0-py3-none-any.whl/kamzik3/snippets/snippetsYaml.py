import inspect
from collections import OrderedDict

import oyaml as yaml


class YamlDumper(yaml.Dumper):

    def represent_data(self, data):
        """
        Custom Yaml representer.
        Every class inheriting from YamlSerializable is serialized using this representer.
        Use traditional serialization on other classes.
        :param data: mixed
        :return: Yaml Node
        """
        device_py_path = "{}.{}".format(data.__class__.__module__, data.__class__.__name__)

        if isinstance(data, YamlSerializable):
            if self.ignore_aliases(data):
                self.alias_key = None
            else:
                self.alias_key = id(data)
            if self.alias_key is not None:
                if self.alias_key in self.represented_objects:
                    node = self.represented_objects[self.alias_key]
                    # if node is None:
                    #    raise RepresenterError("recursive objects are not allowed: %r" % data)
                    return node
                # self.represented_objects[alias_key] = None
                self.object_keeper.append(data)

            output_node = self.represent_mapping(u"!Device:{}".format(device_py_path), data.yaml_mapping(),
                                                 flow_style=False)
            # self.anchor_node(output_node)
            return output_node
        else:
            try:
                return yaml.Dumper.represent_data(self, data)
            except TypeError:
                return yaml.Dumper.represent_none(self, "")


class YamlSerializable(object):

    def yaml_mapping(self):
        """
        Returns mapping of all arguments for __init__ function.
        If You want to return custom Yaml mapping re-implement this method.
        :return: OrderedDict
        """
        arg_spec = inspect.signature(self.__init__).parameters.keys()
        mapping = OrderedDict()
        for arg in arg_spec:
            try:
                argument_value = self.__getattribute__(arg)
                if argument_value is not None:
                    mapping[arg] = argument_value
            except (KeyError, AttributeError):
                """
                Key does not exists, skip in that case
                If You want to implement missing argument, reimplement yaml_mapping in
                particular device class.
                """
                pass
        return mapping
