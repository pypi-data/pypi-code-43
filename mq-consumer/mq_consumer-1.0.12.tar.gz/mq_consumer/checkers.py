from mq_consumer.connectors import Connector


class MQChecker:
    def __init__(self, connector: Connector, passive=True, durable=False):
        self.connector = connector
        self.passive = passive
        self.durable = durable

    def get_message_count(self):
        self.connector.create_connection(declare=False)
        try:
            msg_count = self.connector.channel.queue_declare(
                queue=self.connector.queue, passive=self.passive, durable=self.durable
            ).method.message_count
        finally:
            self.connector.close()
        return msg_count

    def get_consumer_count(self):
        self.connector.create_connection(declare=False)
        try:
            consumers_count = self.connector.channel.queue_declare(queue=self.connector.queue, passive=True).method.consumer_count
        finally:
            self.connector.close()
        return consumers_count
