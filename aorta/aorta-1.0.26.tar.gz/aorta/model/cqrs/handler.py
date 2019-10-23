from aorta.messaging.handler import MessageHandler


class CommandHandler(MessageHandler):
    """Base class for all event listeners."""
    __abstract__ = True
    is_consumer = True

