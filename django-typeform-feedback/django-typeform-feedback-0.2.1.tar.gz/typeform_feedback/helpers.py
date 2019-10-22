import json
import random
import string

from django.conf import settings


class SimpleUserFeedback:
    pk = None
    url = None
    status = None
    object = None

    def __init__(self, id, url, status, user_object=None):
        self.pk = id
        self.url = url
        self.status = status
        self.object = user_object


def _ensure_request(request):
    """
    Security test to authentiate the request
    """
    ensured_request = False
    body = request.body

    if len(body):

        data = json.loads(body.decode('utf-8'))

        keys_received = [_ for _ in data.keys() if _ in settings.TYPEFORM_FEEDBACK_WEBHOOK_DATA_KEYS]
        ensured_request = len(keys_received) == len(settings.TYPEFORM_FEEDBACK_WEBHOOK_DATA_KEYS)
    return ensured_request


def random_string(string_length=20):
    return ''.join(
        random.SystemRandom().choice('{}{}'.format(
            string.ascii_lowercase,
            string.ascii_uppercase,
        )) for _ in range(string_length)
    )
