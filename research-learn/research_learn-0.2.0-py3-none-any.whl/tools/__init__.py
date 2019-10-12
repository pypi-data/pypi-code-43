"""
The :mod:`rlearn.tools` module includes various functions
to analyze and visualize the results of model search and experiments
on multiple datasets.
"""

from .reporting import (
    report_model_search_results,
    summarize_datasets,
    calculate_optimal,
    calculate_wide_optimal,
    calculate_ranking,
    calculate_mean_sem_ranking,
    calculate_mean_sem_scores,
    calculate_mean_sem_perc_diff_scores,
    apply_friedman_test,
    apply_holms_test,
)
from .experiment import select_results, combine_results, ImbalancedExperiment

__all__ = [
    'report_model_search_results',
    'summarize_datasets',
    'calculate_optimal',
    'calculate_wide_optimal',
    'calculate_ranking',
    'calculate_mean_sem_ranking',
    'calculate_mean_sem_scores',
    'calculate_mean_sem_perc_diff_scores',
    'apply_friedman_test',
    'apply_holms_test',
    'select_results',
    'combine_results',
    'ImbalancedExperiment',
]
