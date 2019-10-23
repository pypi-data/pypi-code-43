from aorta.messaging.provider import Provider

from .listener import EventListener


class EventListenerProvider(Provider):
    """Provides handler instances for incoming event
    messages.
    """
    handler_base_class = EventListener
