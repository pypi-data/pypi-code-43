from gym.envs.registration import register

from gym_quickcheck._version import __version__

name = "gym_quickcheck"

register(
    id='random-walk-v0',
    entry_point='gym_quickcheck.envs:RandomWalkEnv',
)

register(
    id='alternation-v0',
    entry_point='gym_quickcheck.envs:AlternationEnv',
)
