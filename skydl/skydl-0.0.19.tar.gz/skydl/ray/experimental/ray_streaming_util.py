# -*- coding: utf-8 -*-
from dataclasses import dataclass
from skydl.ray.experimental.streaming.communication import QueueConfig


class DefaultStreamingEnvConfig(object):
    """
    default ray streaming env config
    """
    def __init__(self, max_size=999999,
                max_batch_size=99999,
                max_batch_time=0.01,
                prefetch_depth=10,
                background_flush=False,
                parallelism=1):
        self.queue_config = QueueConfig(
            max_size=max_size,
            max_batch_size=max_batch_size,
            max_batch_time=max_batch_time,
            prefetch_depth=prefetch_depth,
            background_flush=background_flush)
        self.parallelism = parallelism


class DefaultStreamingSource(object):
    """default streaming source implement"""
    def get_next(self):
        # get current record
        return None


@dataclass
class StreamingRecord(object):
    """
    A class used to streaming transformer
    """
    status: str  # "ok|fail"
    type: str   # "data|error"
    data: object  # e.g. [12.1, 13.3, 11.00, 12.34]


if __name__ == '__main__':
   obj = StreamingRecord("ok", "data", [12.1, 13.3, 11.00, 12.34])
   print(obj.type)