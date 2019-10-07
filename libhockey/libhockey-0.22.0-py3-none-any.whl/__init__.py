#!/usr/bin/env python3

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""Hockey API wrapper."""

import json
import logging
import re
import time
from typing import Any, ClassVar, Dict, List, Optional

import requests

from libhockey.crashes import HockeyCrashesClient
from libhockey.versions import HockeyVersionsClient


class HockeyClient:
    """Class responsible for getting data from HockeyApp through REST calls.

    :param str access_token: The access token to use for authentication. Leave as None to use KeyVault
    """

    log: logging.Logger
    token: str

    versions: HockeyVersionsClient
    crashes: HockeyCrashesClient

    def __init__(self, *, access_token: str, parent_logger: Optional[logging.Logger] = None) -> None:
        """Initialize the HockeyAppClient with the application id and the token."""

        if parent_logger is None:
            self.log = logging.getLogger("libhockey")
        else:
            self.log = parent_logger.getChild("libhockey")

        self.token = access_token
        self.crashes = HockeyCrashesClient(self.token, self.log)
        self.versions = HockeyVersionsClient(self.token, self.log)
