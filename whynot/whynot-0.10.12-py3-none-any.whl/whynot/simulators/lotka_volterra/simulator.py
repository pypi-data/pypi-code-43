"""Simulation code for Lotka-Volterra model."""
import dataclasses

import numpy as np
from scipy.integrate import solve_ivp

import whynot as wn


@dataclasses.dataclass
class Config:
    # pylint: disable-msg=too-few-public-methods
    """Parameterization of Lotka-Volterra dynamics.

    Examples
    --------
    >>> # Configure the simulator so each caught rabbit creates 2 foxes
    >>> lotka_volterra.Config(fox_growth=0.5)

    """

    # Dynamics parameters
    #: Natural growth rate of rabbits, when there's no foxes.
    rabbit_growth: float = 1.
    #: Natural death rate of rabbits, due to predation.
    rabbit_death: float = 0.1
    #: Natural death rate of fox, when there's no rabbits.
    fox_death: float = 1.5
    #: Factor describing how many caught rabbits create a new fox.
    fox_growth: float = 0.75

    # Simulator book-keeping
    #: Start time of the simulator.
    start_time: float = 0
    #: End time of the simulator.
    end_time: float = 100

    def update(self, intervention):
        """Generate a new config by applying the intervention."""
        return dataclasses.replace(self, **intervention.updates)


@dataclasses.dataclass
class State:
    # pylint: disable-msg=too-few-public-methods
    """State of the Lotka-Volterra model."""

    #: Number of rabbits.
    rabbits: float = 10.
    #: Number of foxes.
    foxes: float = 5.

    def values(self):
        """Return the state as a numpy array."""
        state_dict = dataclasses.asdict(self)
        return np.array([state_dict[key] for key in sorted(state_dict.keys())])


class Intervention:
    # pylint: disable-msg=too-few-public-methods
    """Parameterization of an intervention in the Lotka-Volterra model.

    An intervention changes a subset of the configuration variables in the
    specified year. The remaining variables are unchanged.

    Examples
    --------
    >>> # Starting in year 25, set fox_growth to 0.4 (leave other variables unchanged)
    >>> Intervention(year=25, fox_growth=0.4)

    """

    def __init__(self, year=30, **kwargs):
        """Specify an intervention in lotka_volterra.

        Parameters
        ----------
            year: int
                Time of intervention in simulator dynamics.
            kwargs: dict
                Only valid keyword arguments are parameters of Config.

        """
        self.year = year
        config_args = set(f.name for f in dataclasses.fields(Config))
        for arg in kwargs:
            if arg not in config_args:
                raise TypeError("__init__() got an unexpected keyword argument {}!".format(arg))
        self.updates = kwargs


def dynamics(state, config):
    """Noisy Lotka-Volterra equations for 2 species.

    Equations from:
        https://scipy-cookbook.readthedocs.io/items/LoktaVolterraTutorial.html
    """
    rabbits, foxes = state

    delta_rabbits = (config.rabbit_growth * rabbits
                     - config.rabbit_death * rabbits * foxes)

    delta_foxes = (-config.fox_death * foxes +
                   config.fox_growth * config.rabbit_death * rabbits * foxes)

    return [delta_rabbits, delta_foxes]


def simulate(initial_state, config, intervention=None, seed=None):
    """Simulate a run of the Lotka volterra model.

    The simulation starts at initial_state at time start_time, using the
    problem parameters specified in config. The simulator is deterministic,
    so the seed parameter is ignored.
    """
    # pylint: disable-msg=unused-argument
    def forward_map(time, state):
        """Wrap Lotka-volterra equations to use problem config."""
        # Interventions are fixed changes in dynamics after a given time.
        if intervention and time >= intervention.year:
            return dynamics(state, config.update(intervention))
        return dynamics(state, config)

    # Numerically integrate the ODE
    solution = solve_ivp(forward_map, [config.start_time, config.end_time],
                         dataclasses.astuple(initial_state))

    times = solution.t
    states = []
    for pop0, pop1 in zip(solution.y[0], solution.y[1]):
        states.append(State(pop0, pop1))
    return wn.framework.Run(states=states, times=times)
