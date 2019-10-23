from ehelply_batcher.abstract_batching_service import AbstractBatchingService
import random


class SimulatedBatchingService(AbstractBatchingService):

    def release_batch(self) -> bool:
        i = 0
        print("=== Released Batch ===")
        for message in self.get():
            print("i" + str(i) + ": " + str(message))
            i += 1
        print(flush=True)
        return True

    def receive(self, limit: int) -> list:
        messages: list = []

        # Simulates an empty Q on SQS
        simulate_empty_percent: float = 75
        if random.randint(0, 1000) < (simulate_empty_percent * 10):
            return messages

        # Simulates the Q having at least 1 message
        num_messages = random.randint(1, limit)
        for i in range(0, num_messages):
            messages.append(random.randint(0, 400))
        return messages

    def is_message_valid(self, message) -> bool:
        return True

    def form_message(self, message):
        return {"message": message}
