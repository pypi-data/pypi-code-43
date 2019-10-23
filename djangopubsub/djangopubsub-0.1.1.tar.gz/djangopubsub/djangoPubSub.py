from kfpubsub import PubSub
from django.conf import settings
from django.db import close_old_connections


class DjangoPubSub(PubSub):

    def __init__(self):
        host = getattr(settings, 'REDIS_HOST', 'localhost')
        port = getattr(settings, 'REDIS_PORT', 6379)

        super(DjangoPubSub, self).__init__(host=host, port=port)

    def emit(self, event, message):
        super(DjangoPubSub, self).emit(event, message, emit=getattr(settings, 'PUB_SUB_EMIT', True))

    def receive(self, listeners):
        super(DjangoPubSub, self).receive(listeners, close_old_connections)
