from aorta.messaging.provider import Provider

from .handler import CommandHandler


class CommandHandlerProvider(Provider):
    """Provides handler instances for incoming command
    messages.
    """
    handler_base_class = CommandHandler
    consumer = True

