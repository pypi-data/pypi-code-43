import unittest
import time
import json
from .simulator_test import SimulatorTest

class TestSinWave(SimulatorTest):

    def test_004_report_on_change(self):
        time.sleep(0.5)
        num_samples = 0
        for i in list(self.test_q.queue):
            print("checking: {}".format(i))
            if i.get('data_in'):
                num_samples += 1
        self.assertLess(num_samples, 2)
        self.config_io\
            .channels["one"]\
                .protocol_config\
                    .app_specific_config['parameters'] = {"value": 0.0}
        time.sleep(1.5)
        print("queue contains: {}".format(list(self.test_q.queue)))
        last_dp = list(self.test_q.queue)[-1]
        print('last_dp: {}'.format(last_dp))
        last_dp_value = json.loads(list(last_dp['data_in'].values())[-1])["one"]
        self.assertEqual(0.0, float(last_dp_value))

def main():
    unittest.main()

if __name__ == "__main__":
    main()
