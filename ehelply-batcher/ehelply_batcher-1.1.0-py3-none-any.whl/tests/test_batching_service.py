from ehelply_batcher.tests.simulated_batching_service import SimulatedBatchingService


# Max message delay = 2
# Sleep interval = 20
def test_simulation():
    batching_service = SimulatedBatchingService(max_message_delay=0.2, sleep_interval=2, debug=True)


if __name__ == "__main__":
    test_simulation()