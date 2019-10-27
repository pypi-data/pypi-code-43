import logging
import multiprocessing as mp
import threading as th
import time
import os
import socket
import sys
from collections import defaultdict
from datetime import datetime
from random import randint
import json

import msgpack
from kafka import KafkaConsumer
import psutil

from metamorphosis.microservice import Microservice
from metamorphosis.service_web import (
    StopConsumerProcess, KillMicroservice, KillConsumer, KillNode,
    StopNode, StopConsumer, StopMicroservice, AdjustConsumer, ConsumerProcessFinished
)
from metamorphosis.events import load_objecttype, dump_objecttype


def _update_consumer_status_thread(node):
    time.sleep(10)
    while True:
        node.logger.info('Updating node stats')
        node.update_node_stats()
        node.logger.info("Updated node stats")
        time.sleep(30 + randint(-5, 5))


class ConsumerNode(mp.Process):
    """
    A process that runs one or more consumer processes for a Microservice.

    You don't need to instantiate this class directly. This is an object that is created by `gregor.py` as a process
    container for all the consumers related to a microservice.
    """
    def __init__(self, node_name: str, microservice: Microservice, consumer_limits: dict):
        super(ConsumerNode, self).__init__()
        self.bootstrap_servers = microservice.bootstrap_servers
        self.microservice = microservice
        self.service_web_status = microservice.service_status_store
        self.service_web_topic = consumer_limits['service_web_topic']
        microservice.consumer_node = self

        # the pids associated with each consumer process, indexed by microservice.
        self.consumer_processes = defaultdict(list)

        # the desired number of processes, harakiri limit, and harakiri jitter for each consumer
        # indexed by microservice.
        self.consumer_limits = {consumer_name: (
            consumer_limits[microservice.name][consumer_name]['procs'],
            consumer_limits[microservice.name][consumer_name].get('harakiri_limit'),
            consumer_limits[microservice.name][consumer_name].get('harakiri_jitter')
        ) for consumer_name in consumer_limits[microservice.name]}

        # this node's name for the purpose of reporting and for kill/stop signals.
        self.node_name = node_name or socket.gethostname()
        self.logger = logging.getLogger(f'metamorphosis.node.{self.node_name}')
        self.logger.info(f"Creating new node {self.node_name}")

    def _register_node_with_status_store(self):
        self.service_web_status.sadd(f'{self.service_web_topic}.nodes', self.node_name)

    def _unregister_node_with_status_store(self):
        self.service_web_status.srem(f'{self.service_web_topic}.nodes', self.node_name)
        for consumer_name in self.microservice.consumers:
            self._unregister_consumer_with_status_store(consumer_name)

    def _unregister_consumer_with_status_store(self, consumer_name):
        self.service_web_status.hdel(f'{self.service_web_topic}.consumers.procs.{consumer_name}', self.node_name)
        self.service_web_status.hdel(f'{self.service_web_topic}.consumers.{consumer_name}', self.node_name)

    def _process_info(self, consumer_name, now, cp):
        p = psutil.Process(cp.pid)
        with p.oneshot():
            cpu_times = p.cpu_times()
            mem_info = p.memory_info()

        return {
            "node": self.node_name,
            "consumer": consumer_name,
            "pid": cp.pid,
            "user": cpu_times.user,
            "system": cpu_times.system,
            "iowait": getattr(cpu_times, 'iowait', None),
            "rss": mem_info.rss,
            "shared": getattr(mem_info, 'shared', None),
            "vms": mem_info.vms,
            "updated_date": now
        }

    def update_node_stats(self):
        """
        Updates the node stats in redis
        """
        load_avg_1, load_avg_10, load_avg_15 = psutil.getloadavg()
        du = psutil.disk_usage(os.getcwd())
        dio = psutil.disk_io_counters()
        meminfo = psutil.virtual_memory()
        netinfo = psutil.net_io_counters()
        now = datetime.utcnow().isoformat()

        self.logger.debug("Compiling status on %s consumers", len(self.consumer_processes))
        consumers = {
            consumer_name: dict(
                node=self.node_name,
                microservice=self.microservice.name,
                name=consumer_name,
                process_count=self.consumer_limits[consumer_name][0],
                harakiri_limit=self.consumer_limits[consumer_name][1],
                harakiri_jitter=self.consumer_limits[consumer_name][2],
                updated_date=now
            ) for consumer_name in self.consumer_processes
        }

        self.logger.debug("Compiling status on processes")
        consumer_processes = {
            consumer_name: [self._process_info(consumer_name, now, cp)
                            for cp in self.consumer_processes[consumer_name]]
            for consumer_name in self.consumer_processes
        }

        self.logger.debug("Committing everything to redis")
        with self.service_web_status.pipeline() as tx:
            self.service_web_status.hset(
                f'{self.service_web_topic}.nodes.status', self.node_name,
                json.dumps(dict(
                    name=self.node_name,
                    hostname=socket.gethostname(),
                    microservice_name=self.microservice.name,
                    process_count=len(self.consumer_processes),
                    load_avg_1=load_avg_1,
                    load_avg_10=load_avg_10,
                    load_avg_15=load_avg_15,
                    mem_pct=meminfo.percent,
                    mem_free=meminfo.free,
                    mem_used=meminfo.used,
                    mem_total=meminfo.total,
                    disk_usage_pct=du.percent,
                    disk_read_time=dio.read_time,
                    disk_write_time=dio.write_time,
                    disk_busy_time=getattr(dio, 'busy_time', None),
                    bytes_sent=netinfo.bytes_sent,
                    bytes_recv=netinfo.bytes_recv,
                    packets_sent=netinfo.packets_sent,
                    packets_recv=netinfo.packets_recv,
                    errin=netinfo.errin,
                    errout=netinfo.errout,
                    dropin=netinfo.dropin,
                    dropout=netinfo.dropout,
                    updated_date=now
                )))
            for consumer_name in consumers:
                tx.hset(f'{self.service_web_topic}.consumers:{consumer_name}',
                        self.node_name, json.dumps(consumers[consumer_name]))

            tx.set(f'{self.service_web_topic}.microservices.consumers:{self.microservice.name}',
                   json.dumps([consumer_name for consumer_name in consumers]))

            for consumer_name in consumer_processes:
                objs = consumer_processes[consumer_name]
                tx.hset(f'{self.service_web_topic}.consumers.procs:{consumer_name}',
                        self.node_name, json.dumps(objs))
            tx.execute()

    def kill_microservice(self):
        """
        Kill all processes (sigkill) and then kill this node.
        """
        self.logger.info("Got microservice kill signal for %s. Stopping immediately.", self.name)
        for consumer_name in self.consumer_processes:
            self.consumer_limits[consumer_name] = (0, *self.consumer_limits[consumer_name][1:])
            for cp in self.consumer_processes[consumer_name]:
                cp.kill()
        self._unregister_node_with_status_store()
        sys.exit(1)

    def kill_consumer(self, evt):
        """
        Kill all processes for a single consumer, specified by the event.

        Args:
            evt (KillConsumer): The event that indicates which consumer to kill.
        """
        self.logger.info("Got consumer kill signal for %s. Stopping immediately.", evt.name)
        if evt.name in self.consumer_processes:
            for cp in self.consumer_processes[evt.name]:
                cp.kill()
            del self.consumer_processes[evt.name]
            self.consumer_limits[evt.name] = (0, *self.consumer_limits[evt.name][1:])
        self._unregister_consumer_with_status_store(evt.name)
        self.logger.info("Consumers %s have been killed.", evt.name)

    def kill_node(self):
        """Alias for kill_microservice"""
        self.kill_microservice()

    def stop_node(self):
        """Gracefully wait for all consumers to finish what they're working on and then exit."""
        for consumer_name in self.consumer_processes:
            self.consumer_limits[consumer_name] = (0, *self.consumer_limits[consumer_name][1:])
        for consumer_name in self.consumer_processes:
            for cp in self.consumer_processes[consumer_name]:
                cp.join()
        self._unregister_node_with_status_store()
        sys.exit(0)

    def stop_consumer(self, evt):
        """
        Gracefully wait for all consumer processes to finish what they're working on and then stop this consumer.

        This is most likely issued across all nodes.

        Args:
            evt (StopConsumer): The consumer whose processes to stop.
        """
        if evt.name in self.consumer_limits:
            self.consumer_limits[evt.name] = (0, *self.consumer_limits[evt.name][1:])
        self._unregister_consumer_with_status_store(evt.name)

    def stop_microservice(self):
        """Alias for stop_node"""
        self.stop_node()

    def adjust_consumer(self, evt):
        """
        Adjust the number of processes and the harakiri limits for a consumer on this node.

        Args:
            evt (AdjustConsumer): The event containing the data to set the consumer params to,
        """
        new_harakiri_jitter = evt.harakiri_jitter
        new_harakiri_count = evt.harakiri_count
        new_process_count = evt.process_count

        curr_process_count, curr_harakiri_count, curr_harakiri_jitter = self.consumer_limits[evt.name]

        self.consumer_limits[evt.name] = new_process_count, new_harakiri_count, new_harakiri_jitter
        if curr_harakiri_count is None and new_harakiri_count is not None:
            for cp in self.consumer_processes[evt.name]:
                self.microservice.send_event(self.service_web_topic, StopConsumerProcess(
                    node=self.name,
                    name=evt.name,
                    pid=cp.pid
                ))
        elif new_process_count > curr_process_count:
            for x in range(new_process_count - curr_process_count):
                self.consumer_processes[evt.name].append(
                    # create a consumer process with a harakiri limit between the target and the jitter amount
                    # if harakiri was specified.
                    mp.Process(
                        target=self.microservice.consumers[evt.name],
                        kwargs={
                            'harakiri_limit': randint(new_harakiri_count - new_harakiri_jitter,
                                                      new_harakiri_count + new_harakiri_jitter)
                            if new_harakiri_count else None
                        }
                    )
                )
        elif new_process_count < curr_process_count:
            for x in range(min(curr_process_count - new_process_count, len(self.consumer_processes))):
                self.microservice.send_event(self.service_web_topic, StopConsumerProcess(
                    node=self.name,
                    name=evt.name,
                    pid=self.consumer_processes[evt.name][x].pid
                ))
        if new_process_count == 0:
            for consumer_name in self.consumer_processes:
                for cp in self.consumer_processes[consumer_name]:
                    cp.join()

        self.update_node_stats()

    def handle_finished_process(self, evt):
        """
        Handle the safe removal of a process from the running process list and update stats.

        Args:
            evt (ConsumerProcessFinished): The event we're handling
        """
        for cp in list(self.consumer_processes[evt.name]):
            if cp.pid == evt.pid:
                self.consumer_processes[evt.name].remove(cp)
                break
        while len(self.consumer_processes[evt.name]) < self.consumer_limits[evt.name][0]:
            desired_procs, harakiri_count, harakiri_jitter = self.consumer_limits[evt.name]
            harakiri_jitter = harakiri_jitter or 0

            self.logger.info("Starting %s process", evt.name)
            self.consumer_processes[evt.name].append(
                # create a consumer process with a harakiri limit between the target and the jitter amount
                # if harakiri was specified.
                mp.Process(
                    target=self.microservice.consumers[evt.name],
                    kwargs={
                        'harakiri_limit': randint(harakiri_count - harakiri_jitter,
                                                  harakiri_count + harakiri_jitter) if harakiri_count else None
                    }
                )
            )

            self.logger.info("Processes created. Starting")
            self.consumer_processes[evt.name][-1].start()
            self.logger.info("%s processes started", evt.name)
            self.update_node_stats()

    def run(self):
        """
        The process main thread.
        """
        self.logger.info('starting node %s', f'consumer_node.{self.node_name}')
        self.stats_thread = th.Thread(target=_update_consumer_status_thread, kwargs={'node': self})
        self._register_node_with_status_store()
        self.stats_thread.start()

        # create our consumer and attach it to the current mainloop
        consumer = KafkaConsumer(
            self.service_web_topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=f'consumer_node.{self.node_name}'
        )

        # start all requested processes for this node.
        self.logger.info("Bootstrapping consumers with default limits")
        self.logger.info("Starting %s consumers", self.microservice.name)
        for cs in self.consumer_limits:
            desired_procs, harakiri_count, harakiri_jitter = self.consumer_limits[cs]
            harakiri_jitter = harakiri_jitter or 0

            self.logger.info("Starting %s %s processes", desired_procs, cs)

            self.consumer_processes[cs] = [
                # create a consumer process with a harakiri limit between the target and the jitter amount
                # if harakiri was specified.
                mp.Process(
                    target=self.microservice.consumers[cs],
                    kwargs={
                        'harakiri_limit': randint(harakiri_count-harakiri_jitter,
                                                  harakiri_count+harakiri_jitter) if harakiri_count else None
                    }
                ) for _ in range(desired_procs)]

            self.logger.info("Processes created. Starting")
            for cp in self.consumer_processes[cs]:
                cp.start()

            self.logger.info("%s %s processes started", desired_procs, cs)

        # Consume messages
        for msg in consumer:
            # deserialize the data into a json-like structure
            evt_data = msgpack.unpackb(msg.value, raw=False)

            # use that structure to populate g.ObjectTypes, in this case a CreateForm event.
            evt = load_objecttype(evt_data)

            if isinstance(evt, KillMicroservice) and evt.name == self.microservice.name:
                self.kill_microservice()
            elif isinstance(evt, KillConsumer) and evt.name in self.consumer_processes:
                self.kill_consumer(evt)
            elif isinstance(evt, KillNode) and evt.name == self.node_name:
                self.kill_node()
            elif isinstance(evt, StopNode) and evt.name == self.node_name:
                self.stop_node()
            elif isinstance(evt, StopConsumer):
                self.stop_consumer(evt)
            elif isinstance(evt, StopMicroservice) and evt.name == self.microservice.name:
                self.stop_microservice()
            elif isinstance(evt, AdjustConsumer) and evt.node == self.node_name and evt.name in self.consumer_processes:
                self.adjust_consumer(evt)
            elif isinstance(evt, ConsumerProcessFinished) and evt.node == self.node_name:
                self.handle_finished_process(evt)
