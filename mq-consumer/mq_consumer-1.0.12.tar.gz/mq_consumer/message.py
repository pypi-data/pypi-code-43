class MQMessage:
    def __init__(self, channel, method, properties, body):
        self.channel = channel
        self.method = method
        self.properties = properties
        self.body = body
