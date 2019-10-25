import nsq
import functools
from collections import defaultdict
import asyncio
from . import isInputEndpoint, isOutputEndpoint, isCoroutineInputEndpoint, \
    isCoroutineOutputEndpoint, AbstractInputEndpoint, AbstractOutputEndpoint,\
    AbstractCoroutineInputEndpoint, AbstractCoroutineOutputEndpoint
from ..tasks import Task
try:
    from utils.logger import RotatingLogger
    logger = RotatingLogger().logger
except:
    from ..log import logger


__all__ = ['NsqInputEndpoint', 'NsqOutputEndpoint']


class NsqInputEndpoint(AbstractCoroutineInputEndpoint):
    """NSQ input endpoint

    input_end = NsqInputEndpoint('topic_x', 'channel_x', 3,  **{'lookupd_http_addresses': ['127.0.0.1:5761']})
    """

    def __init__(self, topic, channel, max_in_flight=5, auto_confirm=True, **conf):
        self._auto_confirm = auto_confirm
        conf['max_in_flight'] = max_in_flight
        self._inner_q = asyncio.Queue(max_in_flight)
        self._nsq_reader = nsq.Reader(topic=topic, channel=channel,
                                      message_handler=self._message_handler, **conf)

    def _message_handler(self, message):
        message.enable_async()
        self._inner_q.put_nowait(message)

    async def get(self):
        message = await self._inner_q.get()
        task = Task(message.body)
        if self._auto_confirm:
            message.finish()
        else:
            task.set_confirm_handle(functools.partial(self._confirm, message))
        return task

    async def _confirm(self, message):
        if not message._has_responded:
            message.finish()


class NsqOutputEndpoint(AbstractCoroutineOutputEndpoint):
    """NSQ output endpoint

    output_end = NsqOutputEndpoint(**{'nsqd_tcp_addresses': '127.0.0.1:5750'})
    """

    def __init__(self, **conf):
        self._nsq_writer = nsq.Writer(**conf)

    def _callback(self, conn, data, fut):
        success = True
        if isinstance(data, nsq.Error):
            logger.error(data)
            success = False
        fut.set_result(success)

    async def _mpub(self, topic, msgs):
        fut = asyncio.Future()
        callback = functools.partial(self._callback, fut=fut)
        self._nsq_writer.mpub(topic, msgs, callback)
        return fut

    async def _dpub(self, topic, delay, msg):
        fut = asyncio.Future()
        callback = functools.partial(self._callback, fut=fut)
        self._nsq_writer.dpub(topic, delay, msg, callback)
        return fut

    async def put(self, tasks):
        grp = defaultdict(list)
        for params, task in tasks:
            grp[params].append(task.get_raw_data())
        for params, msgs in grp.items():
            if len(params) == 1:
                ret = await self._mpub(params[0], msgs)
            elif len(params) == 2:
                for msg in msgs:
                    ret = await self._dpub(params[0], params[1], msg)
            else:
                logger.error("NsqOutput error: invalid params: {}".format(params))
