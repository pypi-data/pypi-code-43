__name__ = '.'.join(__name__.split('/'))
__package__ = '.'.join('.'.join(__name__.split('/')).split('.')[:-1])

__author__ = "Adrien Pouyet (Ricocotam)"

from gym.envs.registration import register

register(
    id='smartcity-small',
    entry_point='gym_foo.envs:FooEnv',
)