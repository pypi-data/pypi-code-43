#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""setup the logging with a custom metric-level"""

import functools
import logging
import logging.config
import pathlib

import ruamel.yaml

METRIC_LVL = 15  # between DEBUG & INFO
logging.addLevelName(METRIC_LVL, "METRIC")

CONFIG_FILE = pathlib.Path(__file__).parent / "logutils/log_config.yml"
with open(CONFIG_FILE) as cf:
    LOG_CONFIG = ruamel.yaml.safe_load(cf)
    logging.config.dictConfig(LOG_CONFIG)


def metric(self, message, *args, **kws):
    """log on metric level, needs to be attached to a logger instance first"""
    # attach to instances of logger class to have a metric lvl
    if self.isEnabledFor(METRIC_LVL):
        # Yes, logger takes its '*args' as 'args'.
        self._log(METRIC_LVL, message, args, **kws)   # pylint: disable=protected-access


def getLogger(name):  # pylint: disable=invalid-name ; noqa: N802
    """get a logger with "metric" callable attached"""
    if not name.startswith("titanfe."):
        name = f"titanfe.bricks.{name}"
    log = logging.getLogger(name)
    log.metric = functools.partial(metric, log)
    return log
