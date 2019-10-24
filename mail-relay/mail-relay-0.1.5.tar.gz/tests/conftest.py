import os

from mail_relay.config import Config, CSConfig, IMAPConfig, SMTPConfig
import pytest


@pytest.fixture(scope='session')
def test_config():
    return Config(
        SMTPConfig(os.environ['SMTP_HOST'], int(os.environ['SMTP_PORT']), None, None, False, None),
        IMAPConfig(os.environ['IMAP_HOST'], int(os.environ['IMAP_PORT']), None, None, False),
        CSConfig(os.environ['CS_HOST'], int(os.environ['CS_PORT']), False))
