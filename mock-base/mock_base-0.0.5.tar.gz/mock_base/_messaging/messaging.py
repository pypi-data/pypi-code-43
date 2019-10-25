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
