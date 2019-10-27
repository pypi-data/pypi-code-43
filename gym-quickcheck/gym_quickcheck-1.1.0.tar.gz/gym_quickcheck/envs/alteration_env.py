import sys

import gym
import numpy as np
from gym import utils


class NormalDistribution:
    def __init__(self, mean, std):
        self.mean = mean
        self.std = std

    def sample(self):
        return np.random.normal(self.mean, self.std)


class AlternationEnv(gym.Env):
    def __init__(self):
        self.action_space = gym.spaces.Discrete(2)
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(2,), dtype=np.uint8)
        self._len_episode = 100
        self._current_step = 0
        self._current_state = None
        self._last_action = None
        self._has_alternated = None
        self._reward = NormalDistribution(1, 0.1)
        self._penalty = NormalDistribution(-1, 0.1)
        self.reward_range = (self.penalty.mean * self.len_episode, self.reward.mean * self.len_episode)

    @property
    def len_episode(self):
        return self._len_episode

    @property
    def reward(self):
        return self._reward

    @property
    def penalty(self):
        return self._penalty

    def step(self, action):
        self._has_alternated = self._is_alternating(action)
        reward = self.reward.sample() if self._has_alternated else self.penalty.sample()
        self._update_state(action)
        self._last_action = action
        return self._current_state, reward, self._is_done(), None

    def _is_alternating(self, action):
        return self._current_state[0] != action

    def _update_state(self, action):
        self._current_state = np.zeros(shape=self.observation_space.shape, dtype=self.observation_space.dtype)
        self._current_state[1 - action] = 1
        self._current_step += 1

    def _is_done(self):
        return self._current_step == self.len_episode

    def reset(self):
        self._current_step = 0
        self._current_state = self.observation_space.sample()
        return self._current_state

    def render(self, mode='human'):
        sys.stdout.write(f"{self._render_action()}\n{self._render_walk()}\n")

    def _render_action(self):
        if self._last_action is None:
            return ""
        return ["(Right)", "(Left)"][self._last_action]

    def _render_walk(self):
        chars = ['#', '#']
        if self._has_alternated is None:
            color = 'gray'
        elif self._has_alternated:
            color = 'green'
        else:
            color = 'red'
        pos = 1 - self._current_state[0]
        chars[pos] = utils.colorize(chars[pos], color=color, highlight=True)
        return "".join(chars)
