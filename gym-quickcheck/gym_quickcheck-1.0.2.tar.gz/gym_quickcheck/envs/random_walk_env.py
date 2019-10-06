import sys

import gym
import numpy as np
from gym import spaces, utils


class RandomWalkEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.action_space = spaces.Discrete(2)
        self._walk_len = 7
        self.observation_space = spaces.Box(low=0, high=1, shape=(self._walk_len,), dtype=np.uint8)
        self._position = self._center()
        self._max_len = self._walk_len * 2
        self._penalty = -1
        self._reward = 1
        self.reward_range = (self.penalty * self.max_len,
                             self.reward - (self._steps_to_edge() - 1))
        self._step = 0
        self._last_action = None

    def _center(self):
        return self._walk_len // 2

    def _steps_to_edge(self):
        return self._walk_len - self._center() - 1

    @property
    def max_len(self):
        return self._max_len

    @property
    def penalty(self):
        return self._penalty

    @property
    def reward(self):
        return self._reward

    def step(self, action):
        assert action == 0 or action == 1, "the action range must be [0,1]"
        self._last_action = action
        # noinspection PyTypeChecker
        self._update_position(action)
        self._step += 1
        return self._make_observation(), self._calc_reward(), self._is_done(), None

    def _update_position(self, action):
        self._position += action * 2 - 1
        self._position = max(0, self._position)

    def _calc_reward(self):
        return self.reward if self._reached_right_edge() else self.penalty

    def _reached_right_edge(self):
        return self._position == self._walk_len - 1

    def _is_done(self):
        return self._reached_right_edge() or self._step == self.max_len

    def _make_observation(self):
        obs = np.zeros(shape=self.observation_space.shape)
        obs[self._position] = 1
        return obs

    def reset(self):
        self._position = self._center()
        self._step = 0
        return self._make_observation()

    def render(self, mode='human'):
        sys.stdout.write(f"{self._render_action()}\n{self._render_walk()}\n")

    def _render_action(self):
        if self._last_action is None:
            return ""
        return ["(Left)", "(Right)"][self._last_action]

    def _render_walk(self):
        chars = ['#'] * self._walk_len
        c = 'green' if self._reached_right_edge() else 'red'
        chars[self._position] = utils.colorize(chars[self._position], color=c, highlight=True)
        return "".join(chars)

    def close(self):
        pass
