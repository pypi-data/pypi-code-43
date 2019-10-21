""" Notification Module """


class Slack(object):
    """ Slack Class """

    def __init__(self):
        self._workgroup = None
        self._channel = None


class Emails(object):
    """ Emails Class """

    def __init__(self):
        self._account = None


class Notifications(object):
    """ Notifications Class """

    def __init__(self):
        self._slack_channels = list()
        self._emails = list()

    def import_from_json(self, notifications):
        """ Import notifications from JSON """
        # TODO:
        pass
