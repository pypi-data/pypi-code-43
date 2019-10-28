# -*- coding: utf-8 -*-
import logging
import time
import threading
from skydl.ray.experimental.streaming.streaming import DataStream
from py_common_util.common.date_utils import DateUtils
from skydl.ray.experimental.ray_ring_buffer import RayRingBuffer
from skydl.ray.experimental.ray_streaming_executor import RayStreamingExecutor
from skydl.ray.experimental.ray_streaming_util import DefaultStreamingSource

# define logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RayStreamingExecutorSample(RayStreamingExecutor):
    """
    ray流计算执行器sample
    """
    @property
    def ray_ring_buffer(self):
        return self._ray_ring_buffer

    def __init__(self):
        super().__init__()
        self._ray_ring_buffer = RayRingBuffer(1000)

        def exec_forever():
            try:
                count = 0
                while True:
                    count += 1
                    self.ray_ring_buffer.put(str(count) + "*aaa")
                    time.sleep(4)
            except Exception as e:
                logger.error("error occurred at exec_forever ringbuffer put, %s", str(e))
        put_ring_buffer_thread = threading.Thread(target=exec_forever, args=())
        put_ring_buffer_thread.setDaemon(True)
        put_ring_buffer_thread.start()

    def build_stream(self, streaming_parallelism, env) -> DataStream:
        class RayStreamingSource(DefaultStreamingSource):
            @property
            def global_queue(self):
                return self._global_queue

            @property
            def ringbuffer(self):
                return self._ringbuffer

            def __init__(self, ray_ring_buffer):
                self._count = 0
                self._ringbuffer = ray_ring_buffer

            def get_next(self):
                self._count += 1
                print("source will get something...")
                something = self.ringbuffer.get()
                print("source got something=" + something)
                time.sleep(0.5)
                return str(self._count) + "-" + something

        def splitter_fn(record):
            """convert record to another record list, e.g. [record]"""
            logger.info("splitter: " + record)
            # return [record+"-splitter-" + str(i) for i in range(20)]
            return [record+"-splitter-" + DateUtils.now_to_str()]

        def handle_record_fn(record):
            """处理回测的逻辑"""
            logger.info("handle record=" + record)
            time.sleep(10)
            logger.info(record + ", finished:" + DateUtils.now_to_str())

        stream = env.source(
            RayStreamingSource(self.ray_ring_buffer)
        ).set_parallelism(5).flat_map(
            flatmap_fn=splitter_fn
        ).set_parallelism(1).map(
            map_fn=handle_record_fn,
            name="nocode_backtest_map"
        ).set_parallelism(5)
        return stream


