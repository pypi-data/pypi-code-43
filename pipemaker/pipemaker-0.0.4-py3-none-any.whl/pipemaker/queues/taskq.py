#!/usr/bin/env python
from ..utils.dotdict import dotdict
from .rabbitq import Rabbitq
from .eventq import Eventq
from threading import Thread
from datetime import datetime

import logging
log = logging.getLogger()

class Taskq(Rabbitq):
    """ tasks for execution by workers on multiple machines """
    name = "task_queue"

    def listen(self):
        self.eventq = Eventq()
        self.thread = None

        # one job per worker_process.
        self.channel.basic_qos(prefetch_count=1)
        super().listen()

    def onGet(self, ch, method, properties, body):
        """ callback when message received from listen """
        try:
            body = self.decode(body)
            self.thread = Thread(target=self.onGetThread, args=(ch, method, properties, body))
            # terminate immediately when taskq is deleted
            self.thread.daemon = True
            self.thread.start()
        except:
            log.exception("")

    def onGetThread(self, ch, method, properties, body):
        """ execute task in separate thread to listener """
        if body == self.STOP:
            self.onStop(method)
            return
        try:
            body.run()
        except:
            log.exception(f"exception {body}")
            body = dotdict(event="onError", time=datetime.now(), url =body.output)
            self.eventq.put(body)
        self.channel.basic_ack(delivery_tag=method.delivery_tag)
