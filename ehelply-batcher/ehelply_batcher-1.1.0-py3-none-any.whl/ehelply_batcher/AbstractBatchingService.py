import time

from ehelply_batcher.batch import Batch
from ehelply_logger.Logger import Logger


class AbstractBatchingService(Batch):

    def __init__(self, batch_size: int = 16, max_message_delay: float = 2, sleep_interval: float = 20, debug=False,
                 logger: Logger = None):
        super().__init__(batch_size)

        self.logger = logger if logger else Logger(debug_mode=debug)

        # Defines the max time from when the logging service receives a message to when that message will enter the DB
        self.max_message_delay = max_message_delay

        # Defines the responsiveness of the logging service in seconds
        self.sleep_interval = sleep_interval

        if self.sleep_interval > (self.max_message_delay * 60):
            self.sleep_interval = self.max_message_delay * 60

        self.batch_timer_max: int = int(self.max_message_delay * 60 / self.sleep_interval)
        self.batch_timer: int = 0

        if self.batch_timer_max < 1:
            self.batch_timer_max = 1

        self.debug = debug

        self.logger.info("Starting Batching Service:")
        self.logger.info("  * Batch size: " + str(self.batch_size) + " items.")
        self.logger.info("  * Max message delay: " + str(self.max_message_delay) + " minutes.")
        self.logger.info("  * Delay time after receiving 0 messages: " + str(self.sleep_interval) + " seconds.")
        self.logger.info("  * Batch timer: " + str(self.batch_timer_max) + " iterations of no messages.")
        self.logger.info("")

        self.logger.debug("Delegating control of this thread to Batching Service.")
        self.logger.debuggg("This thread will now be 'locked' by the batching service.")
        self.logger.debuggg("  * If this is unintended, please start the Batching Service is a new thread.")
        self.logger.debug("")
        self._service()

    def release_batch(self) -> bool:
        return True

    def receive(self, limit: int) -> list:
        return []

    def is_message_valid(self, message) -> bool:
        return True

    def receipt_message(self, message) -> bool:
        return True

    def form_message(self, message):
        return message

    def _clear(self):
        super()._clear()
        self.batch_timer = 0

    def _service(self):
        while True:
            capacity = self.capacity()

            messages = self.receive(limit=capacity)

            self.logger.debugg(str(len(messages)) + " messages received.")

            if len(messages) > 0:
                i = 0

                for message in messages:
                    self.logger.debuggg(message)

                    self.receipt_message(message)

                    if not self.is_message_valid(message):
                        i += 1
                        continue

                    self._insert(self.form_message(message))

                if i > 0:
                    self.logger.warning(str(i) + " messages were invalid and discarded.")

                if self.size() == self.batch_size:
                    self.logger.debuggg("Releasing batch due to no batch capacity remaining")
                    self.logger.debuggg("")

                    self.release_batch()
                    self._clear()
                    continue

            elif self.batch_timer == self.batch_timer_max:
                self.logger.debuggg("Releasing batch due to batch timer reaching its maximum")
                self.logger.debuggg("")

                self.release_batch()
                self._clear()
                continue

            else:
                time.sleep(self.sleep_interval)
                if self.size() > 0:
                    self.batch_timer += 1

            if self.size() > 0:
                self.logger.debuggg("Batch timer: " + str(self.batch_timer))
                self.logger.debuggg("Batch size: " + str(self.size()))
                self.logger.debuggg()
