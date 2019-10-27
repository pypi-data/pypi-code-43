"""
A manager application for all the consumer processes in a microservice fabric.
"""
import datetime
import json
from functools import reduce
from uuid import uuid4
from flask import current_app
import graphene as g
import msgpack
from kafka import KafkaProducer
from redis import StrictRedis
from werkzeug.exceptions import Unauthorized

from metamorphosis.events import BaseEventMixin, dump_objecttype

_redis = StrictRedis(db=10)  # fixme harcoded
_service_web_topic = 'metamorphosis.services'


class ServiceEventMutation(g.Mutation, BaseEventMixin):
    class Arguments:
        auth_code = g.String(required=True)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        # create the producer and attach it to the current event loop.  Need to figure out broker address config loc.
        guessed_secret = kwargs['auth_code']
        if guessed_secret == current_app.config['SECRET_KEY']:
            producer = KafkaProducer(bootstrap_servers=current_app.config.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'))

            evt = cls.mutate_event(root, info, **kwargs)
            evt.id = str(uuid4())

            # serialize the event and send it over Kafka to the 'forms' topic.  Probably should set this topic in the
            # microservice instance.
            producer.send(current_app.config['SVC_WEB_TOPIC'], msgpack.packb(dump_objecttype(evt)))
            producer.flush()

            # return the mutation object we created, which should provide enough data for the caller to find the
            # object or the status of the request down the road.
            return evt
        else:
            raise Unauthorized()

    @classmethod
    def mutate_event(cls, root, info, **kwargs):
        raise NotImplementedError("Must implement this method instead of `mutate`")


class ConsumerProcess(g.ObjectType):
    pid = g.Int(description='The process or container id that the process is running in')
    messages_processed = g.Int(description='The number of messages this consumer has processed')
    node = g.String()
    consumer = g.String()
    user = g.Float()
    system = g.Float()
    iowait = g.Float()
    rss = g.Float()
    shared = g.Float()
    vms = g.Float()
    updated_date = g.DateTime()


class ConsumerProcessFinished(g.ObjectType):
    node = g.String()
    name = g.String()
    pid = g.Int()
    exit_code = g.String()
    reason = g.String()


class Consumer(g.ObjectType):
    node = g.String()
    microservice = g.String()
    name = g.String()
    process_count = g.Int()
    harakiri_limit = g.Int()
    harakiri_jitter = g.Int()
    processes = g.List(ConsumerProcess)
    updated_date = g.DateTime()

    @staticmethod
    def resolve_processes(parent, info):
        def load_consumer_process(value):
            value['updated_date'] = datetime.datetime.fromisoformat(value['updated_date'])
            return ConsumerProcess(**value)

        key = f'{_service_web_topic}.consumers.procs:{parent.name}'
        print(key)
        return reduce(list.__add__, [
            json.loads(
                _redis.hget(key, name),
                object_hook=load_consumer_process
            )
            for name in _redis.hkeys(key)
        ])


class ConsumerInput(g.InputObjectType):
    node = g.String()
    name = g.String()
    process_count = g.Int()
    harakiri_msg_limit = g.Int()
    harakiri_jitter = g.Int()


class Node(g.ObjectType):
    name = g.String()
    hostname = g.String()
    microservice_name = g.String()
    process_count = g.Int()
    load_avg_1 = g.Float()
    load_avg_10 = g.Float()
    load_avg_15 = g.Float()
    disk_usage_pct = g.Float()
    disk_read_time = g.Float()
    disk_write_time = g.Float()
    disk_busy_time = g.Float()
    mem_pct = g.Float()
    mem_free = g.Float()
    mem_used = g.Float()
    mem_total = g.Float()
    bytes_sent = g.Float(description='number of bytes sent')
    bytes_recv = g.Float(description='number of bytes received')
    packets_sent = g.Float(description='number of packets sent')
    packets_recv = g.Float(description='number of packets received')
    errin = g.Float(description='total number of errors while receiving')
    errout = g.Float(description='total number of errors while sending')
    dropin = g.Float(description='total number of incoming packets which were dropped')
    dropout = g.Float(description='total number of outgoing packets which were dropped (always 0 on macOS and BSD)')
    updated_date = g.DateTime()
    consumers = g.List(Consumer)


class ServiceWeb(g.ObjectType):
    name = g.String()
    nodes = g.List(Node)


class StopConsumer(ServiceEventMutation):
    class Arguments(ServiceEventMutation.Arguments):
        name = g.String(required=True)

    name = g.String()

    @classmethod
    def mutate_event(cls, info, context, **kwargs):
        return StopConsumer(name=kwargs['name'])


class StopConsumerProcess(ServiceEventMutation):
    class Arguments(ServiceEventMutation.Arguments):
        node = g.String(required=True)
        name = g.String(required=True)
        pid = g.Int(required=True)

    node = g.String()
    name = g.String()
    pid = g.Int()

    @classmethod
    def mutate_event(cls, info, context, **kwargs):
        return StopConsumerProcess(
            name=kwargs['name'],
            node=kwargs['node'],
            pid=kwargs['pid']
        )


class KillConsumer(ServiceEventMutation):
    class Arguments(ServiceEventMutation.Arguments):
        name = g.String()

    name = g.String()

    @classmethod
    def mutate_event(cls, info, context, **kwargs):
        return KillConsumer(name=kwargs['name'])


class StopNode(ServiceEventMutation, BaseEventMixin):
    class Arguments(ServiceEventMutation.Arguments):
        name = g.String()

    name = g.String()

    @classmethod
    def mutate_event(cls, info, context, **kwargs):
        return StopNode(name=kwargs['name'])


class KillNode(ServiceEventMutation):
    class Arguments(ServiceEventMutation.Arguments):
        name = g.String()

    name = g.String()

    @classmethod
    def mutate_event(cls, info, context, **kwargs):
        return KillNode(name=kwargs['name'])


class StopMicroservice(ServiceEventMutation):
    class Arguments(ServiceEventMutation.Arguments):
        name = g.String()

    name = g.String()

    @classmethod
    def mutate_event(cls, info, context, **kwargs):
        return StopMicroservice(name=kwargs['name'])


class KillMicroservice(ServiceEventMutation):
    class Arguments(ServiceEventMutation.Arguments):
        name = g.String()

    name = g.String()

    @classmethod
    def mutate_event(cls, info, context, **kwargs):
        return KillMicroservice(name=kwargs['name'])


class AdjustConsumer(ServiceEventMutation):
    class Arguments(ServiceEventMutation.Arguments):
        node = g.String()
        name = g.String()
        harakiri_count = g.Int()
        harakiri_jitter = g.Int()
        process_count = g.Int()

    node = g.String()
    name = g.String()
    harakiri_count = g.Int()
    harakiri_jitter = g.Int()
    process_count = g.Int()

    @classmethod
    def mutate_event(cls, info, context, **kwargs):
        return AdjustConsumer(
            node=kwargs['node'],
            name=kwargs['name'],
            harakiri_count=kwargs['harakiri_count'],
            harakiri_jitter=kwargs['harakiri_jitter'],
            process_count=kwargs['process_count']
        )


class ServiceWebMutations(g.ObjectType):
    """A set of mutations that allow you to stop, kill, or adjust the process limits of a microservice."""
    stop_consumer = StopConsumer.Field()
    stop_microservice = StopMicroservice.Field()
    stop_node = StopNode.Field()
    kill_consumer = KillConsumer.Field()
    kill_microservice = KillMicroservice.Field()
    kill_node = KillNode.Field()
    adjust_consumer = AdjustConsumer.Field()


class ServiceWebQuery(g.ObjectType):
    """Pull info for the cluster on which consumers are running"""

    nodes = g.Field(
        g.List(Node),
        name=g.String(description='The node name'))
    consumers = g.Field(
        g.List(Consumer),
        consumer_name=g.String(description='Grab the given consumer'),
        microservice_name=g.String(description='Grab all consumers for the given microservice'),
        node_name=g.String(description='Grab all consumers on a given node'))
    consumer_processes = g.Field(
        g.List(ConsumerProcess),
        microservice_name=g.String(description='Filter consumer processes to given microservice'),
        consumer_name=g.String(description='Filter consumer processes to a given consumer'))

    @staticmethod
    def resolve_nodes(parent, info, name=None):
        def load_node(value):
            value['updated_date'] = datetime.datetime.fromisoformat(value['updated_date'])
            return Node(**value)

        if name:
            return [json.loads(
                _redis.hget(f'{_service_web_topic}.nodes.status', name),
                object_hook=load_node)]
        else:
            return [
                json.loads(
                    _redis.hget(f'{_service_web_topic}.nodes.status', name),
                    object_hook=load_node
                )
                for name in _redis.hkeys(f'{_service_web_topic}.nodes.status')
            ]

    @staticmethod
    def resolve_consumers(parent, info, consumer_name=None, microservice_name=None, node_name=None):
        def load_consumer(value):
            print(value)
            value['updated_date'] = datetime.datetime.fromisoformat(value['updated_date'])
            return Consumer(**value)

        if consumer_name:
            key = f'{_service_web_topic}.consumers:{consumer_name}'
            if node_name:
                return [json.loads(_redis.hget(key, node_name), object_hook=load_consumer)]
            else:
                return [json.loads(value, object_hook=load_consumer) for value in _redis.hgetall(key).values()]
        elif microservice_name:
            rslt = []
            for consumer_name in [x.decode('utf-8').rsplit(':', 1)[1] for x in _redis.keys(f'{_service_web_topic}.consumers:*')]:
                print(consumer_name)
                key = f'{_service_web_topic}.consumers:{consumer_name}'
                rslt.extend([
                    json.loads(_redis.hget(key, name), object_hook=load_consumer)
                    for name in _redis.hkeys(key)
                ])
            return rslt
        else:
            rslt = []
            for key in _redis.keys(f'{_service_web_topic}.consumers:*'):
                rslt.extend([
                    json.loads(_redis.hget(key, name), object_hook=load_consumer)
                    for name in _redis.hkeys(key)
                ])
            return rslt


    @staticmethod
    def resolve_consumer_processes(parent, info, microservice_name=None, consumer_name=None):
        def load_consumer_process(value):
            value['updated_date'] = datetime.datetime.fromisoformat(value['updated_date'])
            return ConsumerProcess(**value)

        if microservice_name:
            service_consumers_key = f'{_service_web_topic}.microservices.consumers:{microservice_name}'
            rslt = []
            for consumer_name in json.loads(_redis.get(service_consumers_key)):
                key = f'{_service_web_topic}.consumers.procs:{consumer_name}'
                rslt.extend(reduce(list.__add__, [
                    json.loads(value, object_hook=load_consumer_process)
                    for value in _redis.hgetall(key).values()
                ]))
            return rslt
        elif consumer_name:
            key = f'{_service_web_topic}.consumers.procs:{consumer_name}'
            rslt = reduce(list.__add__, [
                json.loads(value, object_hook=load_consumer_process)
                for value in _redis.hgetall(key).values()
            ])
            return rslt


