from typing import Optional


class Metrics:
    class __Metrics:
        channel = None

        def __init__(self, channel: Optional = None):
            self.channel = channel

        def send(self, metric_type, name, metric_value):
            if self.channel is None:
                print("Metrics [" + metric_type + '] ' + name + " : " + metric_value)
            else:
                self.channel.basic_publish(exchange='',
                                           routing_key="metrics",
                                           body={'type': metric_type, 'name': name, 'value': metric_value})

    instance = None

    def __init__(self, channel: Optional):
        if not Metrics.instance:
            Metrics.instance = Metrics.__Metrics(channel)

    @staticmethod
    def inc(self, name: str, value: int):
        Metrics.instance.send('inc', name, value)

    @staticmethod
    def dec(self, name: str, value: int):
        Metrics.instance.send('dec', name, value)

    @staticmethod
    def value(self, name: str, value: int):
        Metrics.instance.send('value', name, value)

    def __getattr__(self, name):
        return getattr(self.instance, name)
