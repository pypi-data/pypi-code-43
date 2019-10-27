# -*- coding: utf-8 -*-
""" Configuration manager. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
from os.path import exists

# 3rd party imports
import yaml


class Config(object):
    """ Config loader class.

    Best used by subclassing and using declarative approach. There are few class
    global fields that can be set to customize the loader

    :VERSION:
        This defines the config version parsed by the iteration. Only change
        this if you change the config structure for your project. If the version
        stored in the config file and this setting differ the loading will raise
        exception about version mismatch.
    :defaults:
        A dict with default values for the configuration. Each key is the
        config value name and each value is the default value to use. Those will
        only remain in the config if they are not defined in any other way. If
        the value is a callable it will be called with the current config state
        as it's only argument. The return value will be used as the config
        default.
    :deserializers:
        Sometimes it's easier to store a config value in a python specific type.
        Since we can't store python data types directly in the files we can
        store a representation of them. This is a map where each key is the
        config value name and the value is a function that will receive the
        value loaded and then return what should be stored in the config. This
        can be used for example to convert an ISO date string to a `datetime`
        object and store that in the config instead.
    """
    VERSION = 1
    defaults = {}
    deserializers = {}
    resolution = []

    class Error(RuntimeError):
        """ Base class for all config errors. """
        pass

    def __init__(self, conf_path=None):
        self.conf_path = conf_path or self._discover_config()
        self.config = {}

    def load(self, required=False):
        """ Load the configuration. """
        if self.conf_path is not None:
            config = self._read()
        elif not required:
            config = {'version': self.VERSION}
        else:
            raise RuntimeError(
                "No configuration found. Please provide one of:\n" +
                "\n".join(self.resolution)
            )

        self.validate(config)
        self.deserialize(config)
        self.apply_defaults(config)

        self.config = config
        return config

    def __getattr__(self, item):
        """

        :param str item:
        :return:
        """
        if item.isupper():
            return self.config[item]

        return super(Config, self).__getattr__(item)

    def validate(self, config):
        """ Validate config

        :param Dict[str, Any] config:
            Config as loaded from external sources.
        :raises Config.Error:
            Raised if the config can't be validated.
        """
        if 'version' not in config:
            raise Config.Error("Unknown config version: {}".format(
                self.conf_path
            ))

        if config['version'] != self.VERSION:
            msg = "Unsupported config version: {}. Should be {}".format(
                config['version'], self.VERSION
            )
            raise Config.Error(msg)

    def deserialize(self, config):
        """ Deserialize config.

        This will convert all the primitive values to the appropriate python
        data structures (like date string to date).

        :param Dict[str, Any] config:
            The config to deserialize values in.
        """
        for name, deserialize in self.deserializers.items():
            if name in config:
                config[name] = deserialize(config[name])

    def apply_defaults(self, config):
        """ Apply defaults to the configuration.

        This step is called at the end  of config loading process (after
        deserialization) so you can use the existing config values as a basis
        for your defaults. Here you can also create new complex variables that
        are dependent on other variables.

        :param Dict[str, Any] config:
            The config dict where we apply the defaults.
        """
        for name, value in self.defaults.items():
            if callable(value):
                value = value(config)
            config.setdefault(name, value)

    def _discover_config(self):
        """ Find configuration file.

        The config resolution is as follows:
        - ./scaffyhub.yaml
        - /etc/scaffyhub.yaml
        - <scaffyhub package>/run/config.yaml
        """
        return next((x for x in self.resolution if exists(x)), None)

    def _read(self):
        try:
            # app_cfg = json.load(open(conf_path))
            with open(self.conf_path) as fp:
                config = yaml.load(fp.read())

        except yaml.YAMLError as ex:
            raise RuntimeError("Failed to load config {}: {}".format(
                self.conf_path,
                str(ex)
            ))

        return config
