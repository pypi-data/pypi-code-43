from pystickynote.paths import CONFIG_PATH
from configparser import ConfigParser

class Config:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read(CONFIG_PATH)
        self.config_dict = self.config['DEFAULT']
        self.background_color = self.config_dict['background_color']
        self.text_color = self.config_dict['text_color']
        self.alpha = self.config_dict['alpha']