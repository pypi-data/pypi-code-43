"""Experiments for civil violence simulator."""
import copy
import dataclasses

import numpy as np
import pandas as pd
from whynot.framework import GenericExperiment, parameter
from whynot.simulators import civil_violence
from whynot import utils


def get_experiments():
    """Return all experiments for civil violence."""
    return [RCT]


def run_simulator(agents, config, treatment_assignment, seed):
    """Run the simulator with the specified agents receiving treatment."""
    population = []
    for agent, treated in zip(agents, treatment_assignment):
        agent = copy.deepcopy(agent)
        if treated:
            agent.risk_aversion = .9
        population.append(agent)
    return civil_violence.simulate(population, config, seed)


def run_abm_experiment(agents, treatment_assignments, config, rng, parallelize, show_progress=True):
    """Run an agent-based modeling experiment.

    We run (in parallel) the agent based model for the given treatment
    assignments to simulate a causal experiment. To obtain ground truth
    counterfactuals, we run repeatedly run the simulator with the same random
    seed where (1) no agent is treated [baseline] and (2) where only agent i is
    treated for i=1, 2, ... Thus, the reported ground truth effects are really
    the marginal causal effect.
    """
    baseline_assignments = np.zeros_like(treatment_assignments)
    counterfactual_assignments = []
    for idx in range(len(agents)):
        one_hot = np.zeros_like(treatment_assignments)
        one_hot[idx] = 1.0
        counterfactual_assignments.append(one_hot)

    assignments = [treatment_assignments, baseline_assignments] + counterfactual_assignments

    # Use the same seed for all runs to ensure difference in counterfactual
    # outcome only due to treatment assignment.
    seed = rng.randint(0, 99999)
    parallel_args = [(agents, config, assign, seed) for assign in assignments]

    if parallelize:
        runs = utils.parallelize(run_simulator, parallel_args, show_progress=show_progress)
    else:
        runs = [run_simulator(*args) for args in parallel_args]

    # RCT Outcomes
    observed_outcomes = runs[0].days_active.values

    # Baseline outcomes
    baseline = runs[1].days_active.values

    true_effects = []
    for idx, run in enumerate(runs[2:]):
        effect = run.days_active.values - baseline
        true_effects.append(effect[idx])

    true_effects = np.array(true_effects)

    return observed_outcomes, true_effects


def sample_agents(rng, num_samples, citizen_vision):
    """Generate covariates for each agent in the model."""
    agents = []
    for _ in range(num_samples):
        agent = civil_violence.Agent()
        agent.vision = citizen_vision
        agent.hardship = rng.uniform()
        agent.risk_aversion = .1
        agent.active_threshold = .1
        agent.legitimacy = rng.uniform()
        agents.append(agent)
    return agents


@parameter(name="citizen_vision", default=5, values=list(range(1, 7)),
           description="How many other citizens each agent can see.")
@parameter(name="agent_density", default=0.8, values=np.arange(0.05, 0.95, 0.1),
           description="How densely packed are agents on the grid.")
@parameter(name='cop_fraction', default=0.05, values=[.1, .2, .3],
           description="number of cops = floor(num_samples * cop_fraction)")
@parameter(name="arrest_prob_constant", default=0.9, values=[0.6, 1.2, 2.3, 4.6],
           description="How strong the interaction between agents is.")
@parameter(name="prison_interaction", default=0.4, values=[.01, .05, .1, .15, .2],
           description="Degree to which regime legitimacy is drawn toward the min while in prison")
def run_civil_violence(citizen_vision, agent_density, cop_fraction, arrest_prob_constant,
                       prison_interaction, num_samples=100, seed=None, show_progress=False,
                       parallelize=True):
    """Run an RCT experiment on ABM civil violence model.

    Treatment corresponds to increasing the 'regime_legitimacy'
    belief of an agent. Treatment is assigned randomly, but the
    units interact, and the parameterization of the experiment is
    based upon the degree of interaction.

    Returns:
        - covariates:               np.array, [num_samples, state_dim]
        - treatment:                Binary np.array [num_samples,]
        - outcomes:                 np.array [num_samples,]
        - ground_truth_effect:      sample average treatment effect

    """
    rng = np.random.RandomState(seed)

    # Determine grid size
    num_cops = int(np.floor(cop_fraction * num_samples))
    num_cells = (num_samples + num_cops) / agent_density
    side_length = int(np.ceil(np.sqrt(num_cells)))

    simulator_config = civil_violence.Config(
        grid_height=side_length,
        grid_width=side_length,
        cop_fraction=cop_fraction,
        arrest_prob_constant=arrest_prob_constant,
        prison_interaction=prison_interaction)

    # Generate population of agents
    agents = sample_agents(rng, num_samples, citizen_vision)

    # Assign treatment
    rct_assignments = rng.uniform(size=(num_samples,)) < 0.5

    outcomes, true_effects = run_abm_experiment(
        agents, rct_assignments, simulator_config, rng, parallelize=parallelize,
        show_progress=show_progress)

    covariates = pd.DataFrame(dataclasses.asdict(a) for a in agents).values
    treatment = rct_assignments.astype(np.int64)

    return (covariates, treatment, outcomes), true_effects


#: RCT experiment that explores how violations of SUTVA impact inference.
RCT = GenericExperiment(
    name="civil_violence_rct",
    description="RCT experiment showing the effect of SUTVA violations on inference.",
    run_method=run_civil_violence)
