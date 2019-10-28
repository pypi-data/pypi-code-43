import logging

from .command import SendEvent, SendResponse
from .encode import JSONEncoder

LOG = logging.getLogger(__name__)


class LoggingBackend:
    def __init__(self, logger=LOG):
        self.logger = logger

    def send(self, message: SendEvent) -> SendResponse:
        self.logger.info(
            JSONEncoder().encode(
                {"event": message.event_name, "payload": message.payload}
            )
        )
        return SendResponse(success=True)
