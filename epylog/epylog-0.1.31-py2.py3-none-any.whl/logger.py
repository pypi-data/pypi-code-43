#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import json
import logging
from logging import handlers
import os
import sys

import graypy

global_handlers = {'file': logging.FileHandler,
                   'watch-file': handlers.WatchedFileHandler,
                   'syslog': handlers.SysLogHandler,
                   'http': handlers.HTTPHandler,
                   'graylog': graypy.GELFUDPHandler}


class Logger:
    """Basic logger class"""

    configuration = {}
    targets = {}
    logger = logging.getLogger('PyLog')

    @classmethod
    def getLogger(cls, name):
        """Returns Logger object with specified settings"""

        logger = logging.getLogger(name)

        if not cls.configuration:
            cls.__read_config_file()

        if cls.configuration['_is_valid']:
            datefmt = "%Y-%m-%d,%H:%M:%S.%f"
            for rule in [rule for rule in cls.configuration['rules'] if rule['_is_valid']]:
                if name.startswith(rule['name'].split('*')[0]):
                    logger.handlers.clear()

                    for target in rule['write-to']:
                        handler = cls.targets[target]

                        formatter = {}
                        if rule.get('format', False):
                            formatter = logging.Formatter(rule['format'],
                                                          datefmt=datefmt)
                        else:
                            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s",
                                                          datefmt=datefmt)

                        handler.setFormatter(formatter)

                        logger.addHandler(handler)

                    logger.setLevel(logging._nameToLevel[rule['min-level'].upper()])

                    return logger

        logger.setLevel(logging.INFO)
        return logger

    @classmethod
    def __read_config_file(cls):
        file_path = os.path.join(os.path.dirname(sys.modules['__main__'].__file__), 'logging.cfg')

        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                try:
                    cls.configuration = json.load(file)
                    cls.__validate_targets()
                    cls.__prepare_targets()
                    cls.__validate_rules()

                    cls.configuration['_is_valid'] = True
                except Exception:
                    cls.logger.exception('Configuration file syntax error')
                    cls.configuration['_is_valid'] = False
        else:
            cls.logger.error('Configuration file not found')
            cls.configuration['_is_valid'] = False

    @classmethod
    def __prepare_targets(cls):
        for target in [target for target in cls.configuration['targets'] if target['_is_valid']]:
            parameters = inspect.signature(global_handlers[target['type']].__init__).parameters.items()
            args = [arg[0] for arg in parameters if arg[1].default is inspect.Parameter.empty and arg[0] not in ['self', 'args', 'kwargs']]
            mappings = {}

            for arg in args:
                mappings[arg] = target[arg]

            for arg in [arg for arg in target.items() if arg[0] not in ['name', 'type', '_is_valid']]:
                mappings[arg[0]] = arg[1]

            handler = global_handlers[target['type']](**mappings)
            cls.targets[target['name']] = handler


    @classmethod
    def __validate_rules(cls):
        for rule in cls.configuration['rules']:
            rule['_is_valid'] = True

            # Validate rule name
            if not rule.get('name', False):
                cls.logger.warning('Invalid rule name. Rule: %s', rule)
                rule['_is_valid'] = False
                continue

            # Validate rule min LEVEL
            if not rule.get('min-level', False) or rule['min-level'].upper() not in logging._nameToLevel.keys():
                cls.logger.warning('Invalid rule min LEVEL. Rule: %s', rule)
                rule['_is_valid'] = False
                continue

            # Validate write to
            if not rule.get('write-to', False) and not all(elem in rule['write-to'].split(',') for elem in cls.targets.keys()):
                cls.logger.warning('Invalid rule write to. Rule: %s', rule)
                rule['_is_valid'] = False
                continue
            rule['write-to'] = rule['write-to'].split(',')

    @classmethod
    def __validate_targets(cls):
        for target in cls.configuration['targets']:
            target['_is_valid'] = True

            # Validate target name
            if target.get('name', False):
                if target['name'] in cls.targets.keys():
                    cls.logger.warning('Target name must be unique. Target: %s', target)
                    target['_is_valid'] = False
                    continue
            else:
                cls.logger.warning('Invalid target name. Target: %s', target)
                target['_is_valid'] = False
                continue

            # Validate target type
            if not target.get('type', False) or target['type'] not in global_handlers.keys():
                cls.logger.warning('Invalid target type. Target: %s', target)
                target['_is_valid'] = False
                continue

            # Validate arguments
            parameters = inspect.signature(global_handlers[target['type']].__init__).parameters.items()
            args = [arg[0] for arg in parameters if arg[1].default is inspect.Parameter.empty and arg[0] not in ['self', 'args', 'kwargs']]

            for arg in args:
                if not target.get(arg, False):
                    cls.logger.warning('Invalid target argument `%s`. Target: %s', arg, target)
                    target['_is_valid'] = False
                    break
