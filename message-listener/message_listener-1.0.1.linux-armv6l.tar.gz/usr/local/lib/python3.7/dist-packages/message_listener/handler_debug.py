from message_listener.abstract.handler_interface import \
    Handler as HandlerInterface


class HandlerDebug(HandlerInterface):
    def handle(self, message):
        if message is not None:
            self.print(message)

    def print(self, message):
        print(message)
