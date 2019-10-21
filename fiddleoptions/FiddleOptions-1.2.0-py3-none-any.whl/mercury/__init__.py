from mercury.client.model import *
from mercury.client.api import *
from gym.envs.registration import register

register(
    id='OptionsEnv-v0',
    entry_point='mercury.envs:OptionsEnv'
)
