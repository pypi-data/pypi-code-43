import logging

import emails

from dq.config import Config
from dq.logging import error

logger = logging.getLogger(__name__)

SMTP_CONFIG = Config.get('mail')


def send_email(to, subject, html, sender_name, sender_email):
    """Send an email.

    :param string to: The recepient of the email.
    :param string subject: The subject of the email.
    :param string html: The HTML content of the email.
    :param string sender_name: The name of the sender.
    :param string sender_email: The sender address of the email.
    :returns boolean: True if the email is sent successfully. False otherwise.
    """
    mail = emails.Message(
        html=html,
        subject=subject,
        mail_from=(sender_name, sender_email),
    )
    resp = mail.send(to=to, smtp=SMTP_CONFIG)
    if not resp.success:
        error(logger, 'Failed to send email', {
            'error': resp.error.strerror, 'to': to, 'subject': subject,
        })
    return resp.success
