import pika
import uuid
import os
import json
from pprint import pprint

class Topic_Client():

    def __init__(self, routing_key = None, host='localhost'):
        
        #url = os.environ.get('CLOUDAMQP_URL', 'amqp://tvmjkfee:0BCkrC2idZZJcrCSCXDsoVpd1_VWisUh@emu.rmq.cloudamqp.com/tvmjkfee')
        #params = pika.URLParameters(url)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        #self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        
        self.channel.exchange_declare(exchange='topic_seon', exchange_type='topic')

        self.routing_key = routing_key    

    def send (self,journal):

        self.channel.basic_publish(
                exchange='topic_seon', 
                routing_key=self.routing_key, 
                 properties=pika.BasicProperties(content_type = "application/json"),
                body=json.dumps(journal.__dict__))

        self.connection.close()
