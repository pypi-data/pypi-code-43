import json
from CoachCare.constants import BASE_DIR, CONFIG_DIR, logging

logging = logging.getLogger(__name__)
class ConfigCreator(object):
    """description of class"""
    def __init__(self, filename, section=None):
        config_dir = CONFIG_DIR
        self.filename = config_dir + filename
        self.section = section

    def create(self):
        try:
            with open(self.filename, "r") as f:
                config = json.load(f)
                if self.section:
                    return config[self.section]
                return config
        except ValueError as e:
            logging.error("[ConfigCreator] Invalid Json: %s" %e ) 
            raise ValueError
        except FileNotFoundError as fnf:
            logging.error("[ConfigCreator] FileNotFound: {}\n{}".format(self.filename, fnf))
            raise FileNotFoundError
            
