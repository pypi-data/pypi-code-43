"""An environment wrapper to convert binary to discrete action space."""
import gym
import numpy as np
from gym import spaces, Wrapper
from gym.envs.atari.atari_env import AtariEnv
from gym.spaces import MultiDiscrete
# try:
#     from gym_doom.wrappers import ViZDoomEnv
# except:
#     pass


# class MultiDiscreteActionWrapper(ViZDoomEnv):
#     def __init__(self, env):
#         super(MultiDiscreteActionWrapper, self).__init__(env)
#         action_size = env.getPossibleActionsCodes()[0]
#         action_space = []
#         for i in range(len(action_size)):
#             action_space.append(2)
#         self.action_space = MultiDiscrete(action_space)
#         self.observation_space = env.observation_space


class AtariObsWrapper(gym.ObservationWrapper):
    def __init__(self, env, dummy_obs):
        super(AtariObsWrapper, self).__init__(env)
        self.atari_env = self.unwrapped
        self.observation_space = self.atari_env.observation_space
        self.shape = self.observation_space.shape
        self.dummy_obs = dummy_obs
        self._obs = np.zeros(shape=self.shape, dtype=np.uint8)

    def observation(self, observation):
        if self.dummy_obs:
            return self._obs
        return observation


class AtariActionWrapper(Wrapper):

    def __init__(self, env, discrete=False):
        """
        Initialize a new binary to discrete action space wrapper.

        Args:
            env (gym.Env): the environment to wrap
            actions (list): an ordered list of actions (as lists of buttons).
                The index of each button list is its discrete coded value

        Returns:
            None

        """
        super(AtariActionWrapper, self).__init__(env)
        self.discrete = discrete
        # create the new action space
        # self.action_space = spaces.Box(low=0, high=17, dtype=np.int32, shape=(1,))
        if isinstance(env.unwrapped, AtariEnv):
            (screen_width, screen_height) = self.env.unwrapped.ale.getScreenDims()
            self.screen_space = spaces.Box(low=0, high=255, shape=(screen_height, screen_width, 3), dtype=np.uint8)

        if not self.discrete:
            self.action_space = MultiDiscrete([env.action_space.n])
            self.observation_space = env.observation_space

    def step(self, action):
        try:
            return self.env.step(action)
        except:
            if isinstance(self.env.unwrapped, AtariEnv):
                return self.env.step(action[0])
        return self.env.step(int(action[0]))

    def reset(self):
        """Reset the environment and return the initial observation."""
        return self.env.reset()

    def getImage(self):
        atari_env = self.env.unwrapped
        return atari_env.ale.getScreenRGB2()


# explicitly define the outward facing API of this module
__all__ = [AtariActionWrapper.__name__, AtariObsWrapper.__name__]
