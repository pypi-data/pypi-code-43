import email
import random
import smtplib
import time

import loremipsum
from pvHelpers.mail.email import EmailHelpers


class GetSMTPConnetion(object):
    def __init__(self, config, login_as=(None, None)):
        self.config = config
        self.conn = None
        (self.username, self.password) = login_as

    def __enter__(self):
        self.conn = smtplib.SMTP(self.config.host, self.config.port, timeout=10)
        if self.config.use_tls:
            self.conn.starttls()

        if self.username and self.password:
            self.conn.login(self.config.username, self.config.password)
            self.conn.ehlo_or_helo_if_needed()
        elif self.config.username and self.config.password:
            self.conn.login(self.config.username, self.config.password)
            self.conn.ehlo_or_helo_if_needed()

        return self.conn

    def __exit__(self, type_, value, traceback):
        self.conn.close()


def test_smtp_connection(config):
    with GetSMTPConnetion(config) as conn:
        print conn.helo()
        print conn.verify(config.username)


def send_test_mail(config, message):
    with GetSMTPConnetion(config) as conn:
        # TODO assert return codes
        conn.verify(config.username)
        return conn.sendmail(config.username, [config.send_to_user], message)


def create_test_mime(sender_id, recipient_ids):
    n = time.time()
    return '''
        X-PreVeil-Msg
        Message-ID: <{}>
        From: {} <{}>
        To: {}
        Date: {}

        {}
        '''.format(
            EmailHelpers.newMessageId(),
            sender_id, sender_id,
            ', '.join(map(lambda i: '{} <{}>'.format(i, i), recipient_ids)),
            u'{}'.format(email.utils.formatdate(n - random.randint(100000, 999999999))),
            loremipsum.generate_paragraph()[2])
