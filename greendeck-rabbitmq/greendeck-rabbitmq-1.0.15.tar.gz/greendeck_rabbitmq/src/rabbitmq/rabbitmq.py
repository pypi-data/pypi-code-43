import pika
from multiprocessing.dummy import Pool as ThreadPool


class RabbitMQ:
    def __init__(self, RMQ_HOST, RMQ_PORT=5672, RMQ_VHOST="/", username=None, password=None):
        """

        :type username: str
        :type password: str
        """
        try:
            self.RMQ_HOST = RMQ_HOST
            self.RMQ_PORT = RMQ_PORT
            self.RMQ_VHOST = RMQ_VHOST
            self.username = username
            self.password = password
            try:
                self.credentials = pika.PlainCredentials(self.username, self.password)
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(self.RMQ_HOST, self.RMQ_PORT, self.RMQ_VHOST,
                                              credentials=self.credentials))
                print("\n" + "connection established successfully.")
            except Exception as e:
                print("\n" + str(e))
        except Exception as e:
            print("\n" + str(e))

    def multi_insert_to_rabbitmq(self, message):
        self.credentials = pika.PlainCredentials(self.username, self.password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(self.RMQ_HOST, self.RMQ_PORT, self.RMQ_VHOST,
                                      credentials=self.credentials))
        channel = self.connection.channel()
        channel.queue_declare(queue=self.queue)
        channel.basic_publish(exchange=self.exchange,
                              routing_key=self.routing_key,
                              body=message,
                              properties=pika.BasicProperties(
                                  delivery_mode=self.delivery_mode,  # make message persistent
                              )
                              )
        self.connection.close

    def insert_to_rabbitmq(self, message):
        self.credentials = pika.PlainCredentials(self.username, self.password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(self.RMQ_HOST, self.RMQ_PORT, self.RMQ_VHOST,
                                      credentials=self.credentials))
        channel = self.connection.channel()
        channel.queue_declare(queue=self.queue)
        channel.basic_publish(exchange=self.exchange,
                              routing_key=self.routing_key,
                              body=message,
                              properties=pika.BasicProperties(
                                  delivery_mode=self.delivery_mode,  # make message persistent
                              )
                              )

    def rabbitmq_publisher(self, message, queue, routing_key, exchange="", delivery_mode=2, mode="single"):

        self.queue = queue
        self.exchange = exchange
        self.routing_key = routing_key
        self.delivery_mode = delivery_mode

        if mode == "single":
            try:
                self.insert_to_rabbitmq(message)
                print("message published successfully.")
            except Exception as e:
                print("\n" + str(e))
        if mode == "multi":
            size = len(message)
            thread = min(int(size / 10) + 1, 20)
            try:
                for batch in range(0, len(message), thread * 10):
                    pool = ThreadPool(thread)
                    items = message[batch:batch + (thread * 10)]
                    # connection_items = [(connection, i) for i in items]
                    pool_results = pool.map(self.multi_insert_to_rabbitmq, items)
                    pool.close()
                    pool.join()
                print("message published successfully.")
            except Exception as e:
                print("\n" + str(e))

    def get_from_rabbitmq(self, queue):
        self.credentials = pika.PlainCredentials(self.username, self.password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(self.RMQ_HOST, self.RMQ_PORT, self.RMQ_VHOST,
                                      credentials=self.credentials))
        channel = self.connection.channel()
        channel.queue_declare(queue=queue)
        _, _, body = channel.basic_get(
            queue=queue, auto_ack=True)
        self.connection.close
        return body

    def size(self, queue):
        try:
            channel = self.connection.channel()
            # q = channel.queue_declare(queue=queue)
            # q_len = int(q.method.message_count)
            res = channel.queue_declare(
                queue=queue,
                durable=True,
                exclusive=False,
                auto_delete=False,
                passive=True
            )
            q_len = int(res.method.message_count)
            return q_len
        except Exception as e:
            print("\n" + str(e))
            raise

    def is_empty(self, queue):
        try:
            q_len = self.size(queue)
        except Exception as e:
            print("\n" + str(e))
        if q_len == 0:
            return True
        else:
            return False

    def rabbitmq_get_all(self, queue):
        try:
            channel = self.connection.channel()
            q_len = self.size(queue)
        except Exception as e:
            print("\n" + str(e))
        return self.rabbitmq_consumer(queue, q_len)

    def rabbitmq_consumer(self, queue, size=1):
        try:
            results = []
            queue = [queue] * size
            thread = min(int(size / 2) + 1, 20)
            for batch in range(0, size, thread * 2):
                temp_queue = queue[batch:batch + (thread * 2)]
                pool = ThreadPool(thread)
                pool_results = pool.map(self.get_from_rabbitmq, temp_queue)
                pool.close()
                pool.join()
                results += pool_results
            results = [i for i in results if i != None]
        except Exception as e:
            print("\n" + str(e))
        return results

    def make_rabbitmq_exchange(self, exchange, queues, exchange_type="fanout", routing_key=''):
        channel = self.connection.channel()
        try:
            channel.exchange_declare(exchange=exchange,
                                     exchange_type=exchange_type)
        except Exception as e:
            return str(e)
        for i in queues:
            try:
                channel.queue_declare(queue=i, durable=True)
                channel.queue_bind(exchange=exchange, queue=i, routing_key=routing_key)
            except Exception as e:
                return str(e)
        print("all queues added to " + exchange + " exchange successfully.")
        return "all queues added to " + exchange + " exchange successfully."

    def multi_insert_to_rabbitmq_exchange(self, message):
        self.credentials = pika.PlainCredentials(self.username, self.password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(self.RMQ_HOST, self.RMQ_PORT, self.RMQ_VHOST,
                                      credentials=self.credentials))
        channel = self.connection.channel()
        channel.exchange_declare(exchange=self.exchange,
                                 exchange_type=self.exchange_type)
        channel.basic_publish(exchange=self.exchange, routing_key=self.routing_key, body=message)

        self.connection.close

    # def insert_to_rabbitmq_exchange(self, message):
    #     channel = self.connection.channel()
    #     channel.queue_declare(queue=self.queue)
    #     channel.basic_publish(exchange=self.exchange,
    #                           routing_key=self.routing_key,
    #                           body=message,
    #                           properties=pika.BasicProperties(
    #                               delivery_mode=self.delivery_mode,  # make message persistent
    #                           )
    #                           )

    def rabbitmq_exchange_publisher(self, exchange, message, exchange_type="fanout", routing_key='', mode="single"):
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.routing_key = routing_key

        if mode == "single":
            try:
                channel = self.connection.channel()
                channel.exchange_declare(exchange=self.exchange,
                                         exchange_type=self.exchange_type)
                channel.basic_publish(exchange=exchange, routing_key=routing_key, body=message)
            except Exception as e:
                return "error: " + str(e)
        else:
            pass
        if mode == "multi":
            size = len(message)
            thread = min(int(size / 10) + 1, 20)
            try:
                for batch in range(0, len(message), thread * 10):
                    pool = ThreadPool(thread)
                    items = message[batch:batch + (thread * 10)]
                    # connection_items = [(connection, i) for i in items]
                    pool_results = pool.map(self.multi_insert_to_rabbitmq_exchange, items)
                    pool.close()
                    pool.join()
                print("message published successfully.")
            except Exception as e:
                print("\n" + str(e))

    def rabbitmq_close_connection(self):
        try:
            self.connection.close()
            print("\n existing connection closed successfully.")
        except Exception as e:
            print("\n" + str(e))
