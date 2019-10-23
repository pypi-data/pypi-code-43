from ehelply_logger.Logger import Logger

from ehelply_batcher.abstract_batching_service import AbstractBatchingService


class AbstractTimerService(AbstractBatchingService):
    """
    A timed send/receive class without any batching
    """
    def __init__(self, name: str = "", delay_seconds: float = 2, mandatory_delay_seconds: float = 0,
                 logger: Logger = None):
        super().__init__(
            name=name,
            batch_size=1,
            max_message_delay_minutes=int(delay_seconds / 60),
            sleep_interval_seconds=delay_seconds,
            mandatory_delay_seconds=mandatory_delay_seconds,
            logger=logger
        )
