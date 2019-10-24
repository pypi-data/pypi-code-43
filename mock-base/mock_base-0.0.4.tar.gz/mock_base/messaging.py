
from . import get_app, _DEFAULT_APP_NAME
from ._app import MockApp


class Notification(object):
  
    def __init__(self, title=None, body=None):
        self.title = title
        self.body = body


class Message(object):
 
    def __init__(self,
                 data=None,
                 notification: Notification = None,
                 android=None,
                 webpush=None,
                 apns=None,
                 token=None,
                 topic=None,
                 condition=None):
        self.data = data
        self.notification = notification
        self.android = android
        self.webpush = webpush
        self.apns = apns
        self.token = token
        self.topic = topic
        self.condition = condition


def send(message: Message, dry_run=False, app: MockApp = None):
    if app is None:
        _a = get_app()
        if _a is None:
            raise Exception("default app not initialized ")
        _a.notify_listeners(message)
    else:
        _a = get_app(app.name)
        if _a is None:
            raise Exception("{} app not initialized ".format(app.name))
        _a.notify_listeners(message)
