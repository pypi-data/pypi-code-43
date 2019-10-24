import os


from mail_relay.mail import GetSMTPConnetion
import pytest

from ..utils import create_test_mime, crypto_create_account, rand_user_id


@pytest.mark.integration
def smtp_connection_test(test_config):
    sender_id, recip_id = rand_user_id(), rand_user_id()
    crypto_create_account(os.environ['CRYPTO_HOST'], os.environ['CRYPTO_PORT'], sender_id)
    crypto_create_account(os.environ['CRYPTO_HOST'], os.environ['CRYPTO_PORT'], recip_id)
    recipients = [recip_id]
    msg = create_test_mime(sender_id, recipients)
    with GetSMTPConnetion(test_config.smtp) as conn:
        conn.ehlo_or_helo_if_needed()
        conn.verify(sender_id)
        conn.sendmail(sender_id, recipients, msg)
