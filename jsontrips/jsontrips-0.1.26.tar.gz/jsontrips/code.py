import logging
logging.basicConfig()

version = "0.1.26"

import os
import pkg_resources
import json

def get_file(name):
    logging.info("Getting {} - version {}".format(name, version))
    return json.loads(pkg_resources.resource_string(__name__, os.path.join("data", name)).decode('utf-8'))
