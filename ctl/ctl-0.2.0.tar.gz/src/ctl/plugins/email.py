from __future__ import absolute_import

import ctl
import confu.schema
import smtplib

from ctl.plugins import PluginBase
from ctl.config import SMTPConfigSchema

from email.mime.text import MIMEText


class EmailPluginConfig(confu.schema.Schema):
    subject = confu.schema.Str()
    sender = confu.schema.Email()
    recipients = confu.schema.List(
        item=confu.schema.Email(), help="list of recipient addresses"
    )
    smtp = SMTPConfigSchema()


@ctl.plugin.register("email")
class EmailPlugin(PluginBase):
    class ConfigSchema(PluginBase.ConfigSchema):
        config = EmailPluginConfig()

    @property
    def smtp(self):
        if not hasattr(self, "_smtp"):
            self._smtp = smtplib.SMTP(self.smtp_host)
        return self._smtp

    def init(self):
        self.smtp_host = self.config.get("smtp").get("host")

    def alert(self, message):
        return self.send(message)

    def send(self, body, **kwargs):
        subject = kwargs.get("subject", self.config.get("subject"))
        recipients = kwargs.get("recipients", self.config.get("recipients", []))
        sender = kwargs.get("sender", self.config.get("sender"))
        for recipient in recipients:
            self._send(body, subject, sender, recipient)

    def _send(self, body, subject, sender, recipient, **kwargs):
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient

        self.log.debug("SENDING {} from {} to {}".format(subject, sender, recipient))
        if kwargs.get("test_mode"):
            return msg

        self.smtp.sendmail(sender, recipient, msg.as_string())
