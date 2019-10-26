"""Interface to simpactcyan's agent-based HIV simulator."""
import os
import numpy as np
import pandas as pd
from whynot.simulators.simpact_hiv.simpactcyan.python import pysimpactcyan

# In contrast to the other simulators, this one currently doesn't
# take a namedtuple Config, since the configuration files for simpactcyan
# are sufficiently complicated and the API supports passing python dictionaries.


def compute_incidence(df_people, age_group, time_window):
    """Compute HVI incidence over the course of the experiment.

    Python modification from:
        https://github.com/wdelva/RSimpactHelp/blob/master/R/incidence.calculator.R

    Incidence is calculated in 3 steps.
          1. Calculate PY of exposure per person
          2. Calculate whether the person had the event or not
          3. Divide events by sum of PY.

    """
    # Calculate naive exposure time
    start_exposure = np.maximum(df_people.TOB + age_group[0], time_window[0])
    infect_time = df_people.InfectTime.astype(np.float64)
    end_exposure = np.minimum(
        np.minimum(df_people.TOB + age_group[1], time_window[1]),
        infect_time)

    exposure = end_exposure - start_exposure

    valid_incidents = (exposure > 0) &  \
        (infect_time > start_exposure) & (infect_time <= end_exposure)

    total_exposure = np.maximum(exposure, 0).sum()
    total_cases = valid_incidents.sum()

    return total_cases / total_exposure


def cumulative_incidence(results, config, age_group=(15, 50)):
    """Compute cumulative incidence total over year intervals for the given age group."""
    df_persons = pd.read_csv(results["logpersons"])

    incidences = []
    for year in list(range(config["population.simtime"]))[1:]:
        incidence = compute_incidence(df_persons, time_window=(year-1, year),
                                      age_group=age_group)
        incidences.append(incidence)

    return sum(incidences)


def simulate(config):
    """Run the simulator and return summary statistics."""
    simpact = pysimpactcyan.PySimpactCyan()

    # Manually set the locations of the binaries and datafiles
    # Trailing "/" is needed for data_path due to bug in Python
    # interface.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    binary_path = os.path.join(current_dir, "simpactcyan_build")
    data_path = os.path.join(current_dir, "simpactcyan", "data") + "/"

    simpact.setSimpactDirectory(binary_path)
    simpact.setSimpactDataDirectory(data_path)

    results = simpact.run(config, "/tmp/simpacttest", parallel=True)
    return cumulative_incidence(results, config)
