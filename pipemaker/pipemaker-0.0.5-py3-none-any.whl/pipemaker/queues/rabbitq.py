import pika
import dill as pickle
import multiprocess as mp

import logging
log = logging.getLogger()

class Rabbitq:
    """ base class for a rabbit queue """
    name = "default_queue"
    STOP = "STOP_CONSUMING"

    ## producer/consumer methods ########################################

    def __init__(self, persistent=False, heartbeat=0):
        """
        :param persistent: save queue and messages to disk
        :param heartbeat: typically producer=0, consumer=180

        .. note::
            OK for producer to never send a message.
            Consumer blocks on listen so can send heartbeat.
        """
        self.persistent = persistent
        params = pika.ConnectionParameters(heartbeat=heartbeat)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.queue = self.channel.queue_declare(queue=self.name, durable=self.persistent)

    def list(self):
        """ return list of messages without removing from queue. for testing """
        messages = []
        tags = []
        while True:
            method, prop, body = self.channel.basic_get(self.name)
            if method is None:
                break
            messages.append(self.decode(body))
            tags.append(method.delivery_tag)
        # requeue
        for tag in tags:
            self.channel.basic_nack(delivery_tag=tag)
        return messages


    def delete(self):
        """ clear the queue completely. for testing. """
        for x in range(self.queue.method.consumer_count):
            self.put(self.STOP)
        self.channel.queue_delete(queue=self.name)
        self.channel.close()

    # producer methods ################################################

    def put(self, body, encoded=False):
        """ put a message on the queue
        :param body: message to send
        :param encoded: True if already encoded
        """
        if not encoded:
            body = self.encode(body)
        properties = dict()
        if self.persistent:
            properties["delivery_mode"]=2
        self.channel.basic_publish(exchange='', routing_key=self.name, body=body,
                               properties=pika.BasicProperties(**properties))

    def encode(self, body):
        """ object to message """
        return pickle.dumps(body)

    # consumer methods ###################################################

    def listen(self):
        """ blocking listen with callback """
        self.channel.basic_consume(queue=self.name, on_message_callback=self.onGet)
        log.info(f"start listening {self.name} process={mp.current_process().pid}")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            log.info(f"keyboard interrupt. stopped listening to {self.name}")
            return
        log.info(f"stop listening {self.name}")

    def onGet(self, ch, method, properties, body):
        """ process received messages """
        body = self.decode(body)
        if body == self.STOP:
            self.onStop(method)
            return
        log.info(body)
        self.channel.basic_ack(delivery_tag=method.delivery_tag)


    def decode(self, body):
        """ message to object """
        return pickle.loads(body)

    def onStop(self, method):
        """ stop the listener """
        self.channel.stop_consuming()
        self.channel.basic_ack(delivery_tag=method.delivery_tag)
