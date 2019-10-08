from __future__ import absolute_import
import logging
import copy
import ctl
import confu.schema
import confu.generator

from ctl import plugin
from ctl.log import ATTACHED


class LogPluginLoggerConfig(confu.schema.Schema):
    logger = confu.schema.Str("logger")
    file = confu.schema.Str("file", default="")
    format = confu.schema.Str("format", default="[%(asctime)s] %(message)s")


class LogPluginConfig(ctl.plugins.PluginBase.ConfigSchema):
    loggers = confu.schema.List(
        "loggers", LogPluginLoggerConfig(), help="list of logger names to log to"
    )


@ctl.plugin.register("log")
class LogPlugin(ctl.plugins.PluginBase):
    class ConfigSchema(ctl.plugins.PluginBase.ConfigSchema):
        config = LogPluginConfig

    default_config = confu.generator.generate(LogPluginConfig)

    def init(self):
        loggers = self.config.get("loggers", [])

        for logger_config in loggers:
            logger_name = logger_config.get("logger")
            self.attach_to_logger(logger_name)
            self.configure_logger(logger_name, logger_config)

        self.loggers = loggers

    def configure_logger(self, logger_name, logger_config):
        filename = logger_config.get("file")
        logger = logging.getLogger(logger_name)
        if filename:
            formatter = logger_config.get(
                "format", LogPluginLoggerConfig.format.default
            )
            fh = logging.FileHandler(filename=filename, mode="a+")
            fh.setFormatter(logging.Formatter(formatter))
            logger.addHandler(fh)

    def attach_to_logger(self, logger_name):
        # attach log plugin to loggers
        if logger_name not in ATTACHED:
            ATTACHED[logger_name] = [self]
        else:
            ATTACHED[logger_name].append(self)

    def apply(self, message, level):
        return message

    def finalize(self, message, level):
        pass
