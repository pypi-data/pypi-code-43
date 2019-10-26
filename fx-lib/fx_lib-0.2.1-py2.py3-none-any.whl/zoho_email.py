import os
import yaml
import smtplib
import logging
from sys import exit
from typing import List
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from collections import Counter, namedtuple
from pathlib import Path

log = logging

CONFIG_FILE_NAME = ".email_config.yaml"
CONFIG_FILE_PATH = CONFIG_FILE_NAME
try:
    if os.path.exists(CONFIG_FILE_NAME):
        CONFIG_FILE_PATH = CONFIG_FILE_NAME
    elif os.path.exists(Path.joinpath(Path.home(), CONFIG_FILE_NAME)):
        CONFIG_FILE_PATH = Path.joinpath(Path.home(), CONFIG_FILE_NAME)
    else:
        raise FileNotFoundError("Could not find email config file.")
except FileNotFoundError:
    exit()

# setup_logging(, default_level=logging.DEBUG)
# log = logging.getLogger("frank")

__all__ = ["Email"]


@dataclass
class Email:
    username: str
    password: str
    sender_title: str
    recipient: str

    def __post_init__(self):
        # Create server object with SSL option
        self.client = smtplib.SMTP_SSL('smtp.zoho.com', 465)

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()

    def login(self):
        # Perform operations via server
        log.debug("Start login into Zoho server")
        self.client.login(self.username, self.password)

    def quit(self):
        log.debug("Quit Zoho email")
        self.client.quit()

    def send(self, title, content):
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['Subject'] = Header(title, 'utf-8')
        msg['From'] = formataddr((str(Header(self.sender_title, 'utf-8')), self.username))
        msg['To'] = self.recipient
        self.client.sendmail(self.username, [self.recipient], msg.as_string())

    @staticmethod
    def read_config(path=CONFIG_FILE_PATH):
        try:
            if not os.path.exists(path):
                raise FileNotFoundError("Could not find email config file.")
            with open(path, 'r') as stream:
                config = yaml.safe_load(stream)
                return Email(**config["zoho_email"])
        except FileNotFoundError:
            exit()


