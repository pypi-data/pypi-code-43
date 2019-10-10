from typing import Optional


class Logging:
    class __Logging:
        channel = None

        def __init__(self, channel: Optional = None):
            self.channel = channel

        def send(self, type, message):
            if self.channel is None:
                print("LOGGING [" + type + '] ' + message)
            else:
                self.channel.basic_publish(exchange='',
                                           routing_key="logs",
                                           body={'type': type, 'message': message})

    instance = None

    def __init__(self, channel: Optional):
        if not Logging.instance:
            Logging.instance = Logging.__Logging(channel)

    @staticmethod
    def debug(message):
        Logging.instance.send("debug", message)

    @staticmethod
    def info(message):
        Logging.instance.send("info", message)

    @staticmethod
    def warning(message):
        Logging.instance.send("warning", message)

    @staticmethod
    def error(message):
        Logging.instance.send("error", message)

    def __getattr__(self, name):
        return getattr(self.instance, name)
