import collections


class Provider:
    """Base class for registries of message handlers."""

    #: All handlers must inherit from this class in order to
    #: be accepted by the :class:`Provider`.
    handler_base_class = None

    #: Indicates if the provider is a consumer i.e. when
    #: a message is accepted by a handler, it is not
    #: propagated to additional handlers.
    consumer = False

    def __init__(self):
        self.handlers = collections.defaultdict(set)

    def autodiscover(self, *args, **kwargs):
        """Automatically discover message handlers. The default
        implementation does nothing.
        """
        pass

    def add(self, cls):
        """Adds a message handler class to the providers'
        registry.
        """
        if cls in self.handlers:
            raise ValueError(f"Handler {cls.__name__} is already registered.")
        cls.add_to_provider(self)

    def get(self, message):
        """Return all handlers for the incoming message."""
        assert getattr(message, 'is_aorta', False),\
            f"Not an Aorta message: {message.get_message_id()}"
        return self.handlers[message.canonical]

    def provide(self, message):
        """Inspect the application properties of an incoming AMQP
        message and return the appropriate handler(s).
        """
        return list(self.handlers[message.canonical])

    def on_canonical(self, name, handler_cls):
        """Registers message handler `handler_cls` to receive messages
        identified by the canonical name `name`.
        """
        if self.isconsumer() and name in self.handlers:
            raise Exception(f"Handler already registerd for {name}")
        self.handlers[name].add(handler_cls)

    def isconsumer(self):
        """Returns a boolean indicating if the provider is a
        consumer.
        """
        return self.consumer

    def __len__(self):
        return len(list(self.handlers.keys()))
