from pprint import pprint
import pika
import os
import json
import time

from threading import Thread
class Topic_Server(Thread):

    def __init__(self, binding_key, integration_service, host='localhost'):

        self.binding_key = binding_key
        self.integration_service = integration_service
        
        self.host = host
        
        Thread.__init__(self)

    def run(self):

        #self.url = os.environ.get('CLOUDAMQP_URL', 'amqp://tvmjkfee:0BCkrC2idZZJcrCSCXDsoVpd1_VWisUh@emu.rmq.cloudamqp.com/tvmjkfee')
        #self.params = pika.URLParameters(self.url)
        #self.connection = pika.BlockingConnection(self.params)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='topic_seon', exchange_type='topic')
        self.result = self.channel.queue_declare('', exclusive=True)
        self.queue_name = self.result.method.queue
        
        self.channel.queue_bind(exchange='topic_seon', queue=self.queue_name, routing_key=self.binding_key)
       
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=self.callback, auto_ack=True)
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()

        self.connection.close()

    def callback(self,ch, method, properties, body):
        
        data = json.loads(body)
        return self.integration_service.do(data)
        
       
        

        

        

        







