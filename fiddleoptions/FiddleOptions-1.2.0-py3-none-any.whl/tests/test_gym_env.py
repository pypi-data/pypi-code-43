from __future__ import absolute_import
import gym
import mercury  # don't remove - needed to hook into gym registration
import unittest
from nose.tools import raises


class TestGymEnv(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @raises(ValueError)
    def test_gym_parameters(self):
        env = gym.make("OptionsEnv-v0", host="")

    @raises(ValueError)
    def test_gym_parameters2(self):
        env = gym.make("OptionsEnv-v0", trade_id="")

    def test_registration(self):
        env = gym.make("OptionsEnv-v0", host="http://mercury-api.nickelandswan.com:80/mercury", trade_id="Vx7y0")
        assert env is not None

    def test_state_is_not_empty(self):
        env = gym.make("OptionsEnv-v0", host="http://mercury-api.nickelandswan.com:80/mercury", trade_id="Vx7y0")
        state, _, _, _ = env.step(env.action_space.sample())
        print(state)
        assert isinstance(state, dict)


if __name__ == '__main__':
    unittest.main()
