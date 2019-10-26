"""Experiments for HIV simulator."""

import numpy as np

from whynot.framework import DynamicsExperiment, parameter
from whynot.simulators import hiv


def get_experiments():
    """Return all experiments for HIV."""
    return [HIVRCT,
            HIVConfounding]


def sample_initial_states(rng):
    """Sample initial state by randomly perturbing the default state."""
    def random_scale(scale, base=10):
        """Make 10**(-scale) to 10**scale smaller/bigger uniformly."""
        return rng.choice(np.logspace(-scale, scale, base=base, num=50))

    state = hiv.State()
    state.uninfected_T1 *= random_scale(0.33)
    state.infected_T1 *= random_scale(0.33)
    state.uninfected_T2 *= random_scale(0.33)
    state.infected_T2 *= random_scale(0.33)
    state.free_virus *= random_scale(0.33)
    state.immune_response *= random_scale(0.33)
    return state


##################
# RCT Experiment
##################
# pylint: disable-msg=invalid-name
#: Experiment on effect of increased drug efficacy on infected macrophages (cells/ml)
HIVRCT = DynamicsExperiment(
    name="hiv_rct",
    description="Study effect of increased drug efficacy on infected macrophages (cells/ml).",
    simulator=hiv,
    simulator_config=hiv.Config(epsilon_1=0.1, duration=150),
    intervention=hiv.Intervention(time=100, epsilon_1=0.5),
    state_sampler=sample_initial_states,
    propensity_scorer=0.5,
    outcome_extractor=lambda run: run[149].infected_T2,
    covariate_builder=lambda run: run.initial_state.values())


##########################
# Confounding Experiments
##########################

@parameter(name="treatment_bias", default=0.9,
           description="Treatment probability bias between more infected and less infected units.")
def hiv_confounded_propensity(run, treatment_bias):
    """Probability of treating each unit.

    We are more likely to treat units with high immune response and free virus.
    """
    if run.initial_state.immune_response > 10 and run.initial_state.free_virus > 1:
        return treatment_bias

    return 1. - treatment_bias


# pylint: disable-msg=invalid-name
#: Experiment on effect of increased drug efficacy on infected macrophages with confounding
HIVConfounding = DynamicsExperiment(
    name="hiv_confounding",
    description=("Study effect of increased drug efficacy on infected macrophages (cells/ml). "
                 "Units with high immune response and free virus are more likely to be treated."),
    simulator=hiv,
    simulator_config=hiv.Config(epsilon_1=0.1, duration=150),
    intervention=hiv.Intervention(time=100, epsilon_1=0.5),
    state_sampler=sample_initial_states,
    propensity_scorer=hiv_confounded_propensity,
    outcome_extractor=lambda run: run[149].infected_T2,
    covariate_builder=lambda intervention, run: run.initial_state.values())
