from herald import base
from . import settings
from .client import get_client


class SlackNotification(base.NotificationBase):
    render_types = ['text']
    channel = None
    token = settings.TOKEN
    as_user = settings.AS_USER
    icon_url = settings.ICON_URL
    username = settings.USERNAME

    def get_recipients(self):
        return [self.channel]

    def get_sent_from(self):
        return

    def get_extra_data(self):
        return {
            'token': self.token,
            'as_user': self.as_user,
            'icon_url': self.icon_url,
            'username': self.username,
        }

    @staticmethod
    def _send(recipients, text_content=None, html_content=None, sent_from=None,
              subject=None, extra_data=None, attachments=None):
        client = get_client(token=extra_data['token'])
        client.api_call(
            'chat.postMessage',
            channel=recipients[0],
            text=text_content,
            as_user=extra_data['as_user'],
            username=extra_data['username'],
            icon_url=extra_data['icon_url'],
        )
