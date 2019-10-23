# -*- coding: utf-8 -*-
import logging

from rq import Connection
from rq import Queue


def queue_job(redis_connection, queue_name, delegate, *args):
    """
    Queue a job.

    :param redis_connection: redis connection instance
    :param queue_name: name of the queue to place the job on
    :param delegate: function to be executed by the queue -> 'package.module.function'
    :param args: arguments list used by called function
    :return: id of the job
    """
    logging.info("scheduling job {}".format(delegate))
    if callable(delegate):
        delegate = delegate.__module__ + "." + delegate.__name__
    with Connection(redis_connection):
        q = Queue(queue_name)
        job = q.enqueue(delegate, *args)
        return job.id
