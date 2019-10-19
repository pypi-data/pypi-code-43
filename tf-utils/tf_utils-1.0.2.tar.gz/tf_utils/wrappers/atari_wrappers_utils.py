from gym.spaces import *
from stable_baselines.common.atari_wrappers import *

from .atariActionWrapper import AtariActionWrapper


class ScaledFloatFrame(gym.ObservationWrapper):
    def __init__(self, env):
        gym.ObservationWrapper.__init__(self, env)
        self.observation_space = Box(low=0, high=1, shape=env.observation_space.shape, dtype=np.float32)

    def observation(self, observation):
        # careful! This undoes the memory optimization, use
        # with smaller replay buffers only.
        return np.array(observation).astype(np.float32) / 255.0


class DownSample(gym.ObservationWrapper):
    def __init__(self, env):
        gym.ObservationWrapper.__init__(self, env)
        self.observation_space = Box(low=0, high=255, shape=(50, 50, 3), dtype=np.float32)

    def observation(self, observation):
        return cv2.resize(observation, (50, 50), interpolation=cv2.INTER_AREA)


def make_atari_env(args):
    env = make_atari(args.env_id)
    env = AtariActionWrapper(env, args.discrete)
    if args.deepmind:
        env = wrap_deepmind(env, False)
    return env


def make_atari_vs_nes_env(args):
    # ============================
    isNes = False
    # if "SuperMario" in args.env_id:
    #     isNes = True
    #     from gailtf.environments import gym_super_mario_bros
    #     env = gym_super_mario_bros.make(args.env_id)
    # else:
    env = gym.make(args.env_id)

    env = AtariActionWrapper(env, args.discrete)
    env.metadata = 0

    return env, isNes


def make_atari(env_id, timelimit=True):
    # XXX(john): remove timelimit argument after gym is upgraded to allow double wrapping
    env = gym.make(env_id)
    if not timelimit:
        env = env.env
    if 'NoFrameskip' in env.spec.id:
        env = NoopResetEnv(env, noop_max=30)
        env = MaxAndSkipEnv(env, skip=4)
    return env


def wrap_deepmind(env, episode_life=True, clip_rewards=True, frame_stack=False, scale=False):
    """
    Configure environment for DeepMind-style Atari.

    :param env: (Gym Environment) the atari environment
    :param episode_life: (bool) wrap the episode life wrapper
    :param clip_rewards: (bool) wrap the reward clipping wrapper
    :param frame_stack: (bool) wrap the frame stacking wrapper
    :param scale: (bool) wrap the scaling observation wrapper
    :return: (Gym Environment) the wrapped atari environment
    """
    if episode_life:
        env = EpisodicLifeEnv(env)
    if 'FIRE' in env.unwrapped.get_action_meanings():
        env = FireResetEnv(env)
    env = WarpFrame(env)
    if scale:
        env = ScaledFloatFrame(env)
    if clip_rewards:
        env = ClipRewardEnv(env)
    if frame_stack:
        env = FrameStack(env, 4)
    return env
