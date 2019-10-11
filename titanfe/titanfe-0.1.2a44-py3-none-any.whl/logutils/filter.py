#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

"""filter for the titan logging to get the hostname into the log records"""

import logging
import platform


class HostnameFilter(logging.Filter):  # pylint: disable=too-few-public-methods
    """Make the hostname available in log records"""
    hostname = platform.node()

    def filter(self, record):
        record.hostname = HostnameFilter.hostname
        return True
