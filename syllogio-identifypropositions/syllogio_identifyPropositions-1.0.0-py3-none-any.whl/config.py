import os
from configparser import ConfigParser, NoOptionError, NoSectionError

parser = ConfigParser()
parser.read([os.path.join(os.getcwd(), "setup.cfg")])


def get(prop, default=None):
    try:
        return parser.get("syllogio-identifyPropositions", prop)
    except (NoOptionError, NoSectionError):
        return default
