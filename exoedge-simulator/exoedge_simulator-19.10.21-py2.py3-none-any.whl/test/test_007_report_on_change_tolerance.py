import unittest
import time
import json
from .simulator_test import SimulatorTest

class Test(SimulatorTest):

    def test_007_report_on_change_tolerance(self):
        def wait_for_q_size_or_timeout(q, size, timeout):
            start = time.time()
            while q.qsize() <= size:
                if time.time() - start >= timeout:
                    print("timed out!")
                    break
                time.sleep(0.1)

        def get_num_samples(q):
            num_samples = 0
            for i in list(q):
                print("checking: {}".format(i))
                if i.get('data_in'):
                    num_samples += 1
            return num_samples

        def get_sample_from_q(sample):
            data_in = sample['data_in']
            data_in_values = list(data_in.values())
            print("data_in_values: {}".format(data_in_values))
            return json.loads(data_in_values[-1])['one']

        wait_for_q_size_or_timeout(self.test_q, 1, 0.5)
        self.assertEqual(get_num_samples(self.test_q.queue), 1)
        self.assertEqual(get_sample_from_q(self.test_q.get()), 1.0)

        self.config_io\
            .channels["one"]\
                .protocol_config\
                    .app_specific_config['parameters'] = {"value": 1.09}

        wait_for_q_size_or_timeout(self.test_q, 1, 0.5)
        self.assertEqual(get_num_samples(self.test_q.queue), 0)
        self.config_io\
            .channels["one"]\
                .protocol_config\
                    .app_specific_config['parameters'] = {"value": 1.1}

        wait_for_q_size_or_timeout(self.test_q, 1, 0.5)
        self.assertEqual(get_num_samples(self.test_q.queue), 0)

        self.config_io\
            .channels["one"]\
                .protocol_config\
                    .app_specific_config['parameters'] = {"value": 1.11}

        wait_for_q_size_or_timeout(self.test_q, 2, 0.5)
        self.assertEqual(get_num_samples(self.test_q.queue), 1)
        self.assertEqual(get_sample_from_q(self.test_q.get()), 1.11)


def main():
    unittest.main()

if __name__ == "__main__":
    main()
