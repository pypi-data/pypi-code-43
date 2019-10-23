from aorta.messaging.handler import MessageHandler


class EventListener(MessageHandler):
    """Base class for all event listeners."""
    __abstract__ = True
