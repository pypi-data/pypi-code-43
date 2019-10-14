""" Queue is responsible to forward messages between brokers and consumers. """

from aio_task.queue.base import (Producer as ProducerABC,
                                 Consumer as ConsumerABC,
                                 Message)
