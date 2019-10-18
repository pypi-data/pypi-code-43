import gym


class SmartCityEnv(gym.Env):
    default_json_path = "settings.json"

    def __init__(self):
        pass

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