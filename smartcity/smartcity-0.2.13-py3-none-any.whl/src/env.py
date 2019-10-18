import gym

from .factory import load_from_json


class SmartCityEnv(gym.Env):
    def __init__(self, json_file_path):
        self.engine = load_from_json(json_file_path)

    def change_settings(self, setting_file_path):
        pass

    def step(self, **kwargs):
        obs, reward, done, info = [None] * 4
        return obs, reward, done, info

    def seed(self, seed):
        pass

    def reset(self):
        pass

    def render(self):
        pass

    def close(self):
        pass


class SmartCityEnvSmall(SmartCityEnv):
    def __init__(self):
        super(SmartCityEnvSmall, self).__init__(json_file_path="data/small.json")


class SmartCityEnvMedium(SmartCityEnv):
    def __init__(self):
        super(SmartCityEnvMedium, self).__init__(json_file_path="data/medium.json")


class SmartCityEnvBig(SmartCityEnv):
    def __init__(self):
        super(SmartCityEnvBig, self).__init__(json_file_path="data/big.json")