# -*- coding: utf-8 -*-
import logging
import smtplib
import sys
from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

log = logging.getLogger(__name__)
PY2 = sys.version_info[0] == 2


if PY2:
    binary_type = str
else:
    binary_type = bytes


def text_(s, encoding="latin-1", errors="strict"):
    if isinstance(s, binary_type):
        return s.decode(encoding, errors)
    return s


class SMTPClient(object):
    def __init__(self, smtp_host, sender):
        """
        Create an smtp client.

        :param smtp_host: smtp server
        :param sender: Sender of the mail
        """
        self.smtp_host = smtp_host
        self.sender = sender
        self.smtp_obj = smtplib.SMTP(self.smtp_host)

    def send_mail(
        self,
        receivers,
        subject,
        message_plain,
        message_html=None,
        cc=None,
        bcc=None,
        files=None,
    ):
        """
        Send an email.

        :param receivers: Receivers (list)
        :param subject: Email subject
        :param message_plain: Email message (plain text)
        :param message_html: Email message (html version)
        :param cc: carbon copy (list)
        :param bcc: blind carbon copy (list)
        :param files: array for attachments with
        {'name': filename, 'data': binary attachmentdata}
        """
        msg = MIMEMultipart("alternative")
        msg["Subject"] = Header(subject, "utf-8")
        msg["From"] = Header(text_(self.sender), "utf-8")
        msg["To"] = Header(text_("; ".join(receivers)), "utf-8")
        if cc:
            msg["CC"] = Header(text_("; ".join(cc)), "utf-8")
        else:
            cc = []
        if bcc:
            msg["BCC"] = Header(text_("; ".join(bcc)), "utf-8")
        else:
            bcc = []
        plain_text = MIMEText(message_plain, "plain", _charset="UTF-8")
        msg.attach(plain_text)
        if message_html:
            # According to RFC 2046, the last part of a multipart message, in this case
            # the HTML message, is best and preferred.
            html_text = MIMEText(message_html, "html", _charset="UTF-8")
            msg.attach(html_text)
        if files:
            for f in files or []:
                maintype, subtype = f["mime"].split("/", 1)
                attachment = MIMEBase(maintype, subtype)
                attachment.set_payload(f["data"])
                if not isinstance(attachment, (bytes, bytearray)):
                    log.warning("The attachment should be bytes or bytearray.")
                encoders.encode_base64(attachment)
                attachment.add_header(
                    "Content-Disposition", "attachment", filename=f["name"]
                )
                msg.attach(attachment)
        self.smtp_obj.sendmail(self.sender, receivers + cc + bcc, msg.as_string())
