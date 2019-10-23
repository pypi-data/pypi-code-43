import logging
import os

import ioc
from aorta.messaging import factory
from aorta.context import Context


class MessageRunner:
    """Runs the handlers that are interested in a
    specific message.
    """
    logger = logging.getLogger('aorta.ingress')

    #: Indicates if any exception propagating from a handler class
    #: is considered fatal.
    errors_fatal = False

    def __init__(self, provider):
        self.provider = provider

    def run(self, incoming, on_success=None, on_failure=None):
        """Retrieve the handlers for the incoming message and
        invoke them. Return a boolean indicating if any handler
        was ran for the incoming message.
        """
        on_success = on_success or (lambda *a, **k: None)
        on_failure = on_failure or (lambda *a, **k: None)

        # Check if the incoming message is valid.
        message = factory(incoming)
        ctx = Context.fromincoming(message)
        if not message.is_aorta:
            self.logger.warning("Dropped message (id: %s): unknown format",
                message.get_message_id())
            return 0

        # Run all handlers. Note that we assume here that the provider ensures
        # that consumables (e.g. commands) are not ran against multiple handlers.
        results = []
        for handler_class in self.provider.get(message):
            try:
                results.append(self.handle(handler_class, ctx))
            except Exception as e:
                self.logger.exception("Caught fatal %s during message handling",
                    type(e).__name__)
            if self.provider.isconsumer():
                break

        return len(results)

    def handle(self, handler_class, context):
        """Handles `context` using the given `handler_class`."""
        return handler_class.run(self, context)

    def has_handlers(self):
        """Return a boolean indicating if the runner has any
        handlers configured.
        """
        return len(self.provider) > 0
