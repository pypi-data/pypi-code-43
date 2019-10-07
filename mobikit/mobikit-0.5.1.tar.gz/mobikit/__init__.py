#
# Copyright (c) 2019 Mobikit, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import pkg_resources
import json
import logging
import mobikit.workspaces as feeds
import mobikit.workspaces as workspaces
from .config import config

# this will intentionally error for public release
# we don't want to expose models package to the public
try:
    from .models import models
except ImportError:
    pass

# instantiate logger
config.logger = logging.getLogger()
console = logging.StreamHandler()
config.logger.addHandler(console)
# check the environoment and set api base
host = os.getenv("MOBIKIT_API_HOST")
if not host:
    config.base = "https://api.mobikit.io/"
elif "http" in host:
    config.base = host
elif "localhost" in host:
    config.base = f"http://{host}/"
else:
    config.base = f"https://api.{host}/"

# load api urls based no environment
constants_file = pkg_resources.resource_filename("mobikit", "reference/constants.json")
with open(constants_file) as f:
    constants = json.load(f)
    config.upload_route = config.base + constants["urls"]["upload_datafeed_route"]
    config.validate_route = config.base + constants["urls"]["validate"]
    config.feed_route = config.base + constants["urls"]["feeds"]
    config.source_route = config.base + constants["urls"]["sources"]
    config.query_route = config.base + constants["urls"]["query"]


# allow user to pass in an api key to get started
def set_api_key(user_token):
    if not isinstance(user_token, str):
        config.logger.exception("pass in a string token!")
    else:
        config.api_token = user_token
