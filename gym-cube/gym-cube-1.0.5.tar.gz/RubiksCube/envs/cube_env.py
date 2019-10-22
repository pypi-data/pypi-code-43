import gym
import numpy as np
from gym import spaces
from RubiksCube.MagicCube.code.cube import Cube
import imageio


class CubeEnv(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array', 'ansi']
    }

    def __init__(self, n, randomize=0):
        """
        Create an environment
        :param n: number of blocks on a side of the cube
        :param randomize: Number of random steps to be taken from the solved position
        """
        self.cube = Cube(n)
        self.transitions = []
        self.max_steps = 25
        self.solved_cube_stickers = np.copy(self.cube.stickers)

        self.randomize = randomize
        self.cube.randomize(self.randomize)
        self.initial_cube_stickers = np.copy(self.cube.stickers)

        self.metadata['render.modes'].extend(["human", "rgb_array", "ansi"])

        action_count = 0
        self.actions = {}
        for f in self.cube.facedict.keys():
            for l in range(self.cube.N - 1):
                for d in [-1, 1]:
                    self.actions[action_count] = (f, l, d)
                    action_count += 1

        self.action_space = spaces.Discrete(len(self.actions))
        # self.action_space = spaces.Discrete(len(self.cube.facedict) * (self.cube.N - 1) * 2)
        self.observation_space = spaces.Box(low=np.array([0]*(n**2*6)),
                                            high=np.array([5]*(n**2*6)))

    def step(self, action):
        assert self.action_space.contains(action), "%r (%s) invalid" % (action, type(action))

        self.transitions.append(action)
        self.cube.move(*self._action_to_args(action))
        reward = 1 if self.solved else 0
        done = reward or len(self.transitions) >= self.max_steps
        info = {}

        return self.state, reward, done, info

    def reset(self, skip_randomize=False):
        self.cube.stickers = np.copy(self.initial_cube_stickers)
        self.transitions.clear()
        if not skip_randomize:
            self.cube.randomize(self.randomize)
        return self.state

    def render(self, mode='human'):
        """
        Renders the environment
        :param mode: human, rgb_array and ansi supported
        """
        if mode == "human":
            self.cube.render(flat=False).show()
        if mode == "rgb_array":
            fig = self.cube.render(flat=False)
            fig.canvas.draw()
            w, h = fig.canvas.get_width_height()
            buf = np.fromstring (fig.canvas.tostring_rgb(), dtype=np.uint8)
            buf = buf.reshape((h, w, 3))
            return buf
        if mode == "ansi":
            return self.cube.stickers.tostring()

    def render_transitions(self, mode='human', filename='out.mp4'):
        if mode == "human":
            moves = self.transitions[:]
            self.reset(skip_randomize=False)
            with imageio.get_writer(filename, fps=1) as video:
                video.append_data(self.render(mode="rgb_array"))
                for action in moves:
                    self.step(action)
                    video.append_data(self.render(mode="rgb_array"))

    def _action_to_args(self, action):
        return self.actions[action]

    def readable_moves(self):
        return [self._action_to_args(action) for action in self.transitions]

    @property
    def state(self):
        return self.cube.stickers.flatten()

    @property
    def solved(self):
        return np.array_equal(self.cube.stickers, self.solved_cube_stickers)

    @property
    def max_steps(self):
        return self.max_steps_value

    @max_steps.setter
    def max_steps(self, value):
        self.max_steps_value = value


if __name__ == "__main__":
    env = CubeEnv(4, 0)
    for i in range(24):
        state, reward, done, info = env.step(env.action_space.sample())
    print(env.solved)
    print(state, reward, done, info)
    print(env.readable_moves())
    env.render_episodes()

    # env.reset()
    # print(env.solved)

