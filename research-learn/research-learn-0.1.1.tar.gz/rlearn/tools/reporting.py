"""
It contains functions to report the results of model
search and experiments.
"""

# Author: Georgios Douzas <gdouzas@icloud.com>
# Licence: MIT

from collections import Counter
import warnings

from scipy.stats import friedmanchisquare, ttest_rel
from statsmodels.stats.multitest import multipletests
import numpy as np
import pandas as pd
from sklearn.metrics import SCORERS
from sklearn.utils.validation import check_is_fitted

from ..utils import check_datasets
from ..model_selection import ModelSearchCV


def _return_row_ranking(row, sign):
    """Returns the ranking of values. In case of tie, each ranking value
    is replaced with its group average."""

    # Calculate ranking
    ranking = (sign * row).argsort().argsort().astype(float)

    # Break the tie
    groups = np.unique(row, return_inverse=True)[1]
    for group_label in np.unique(groups):
        indices = groups == group_label
        ranking[indices] = ranking[indices].mean()

    return ranking.size - ranking


def calculate_ranking(imbalanced_experiment):
    """Calculate the ranking of oversamplers for
    any combination of datasets, classifiers and
    metrics."""
    ranking_results = imbalanced_experiment.wide_optimal_.apply(
        lambda row: _return_row_ranking(
            row[3:], SCORERS[row[2].replace(' ', '_').lower()]._sign
        ),
        axis=1,
    )
    ranking = pd.concat(
        [imbalanced_experiment.wide_optimal_.iloc[:, :3], ranking_results], axis=1
    )
    return ranking


def report_model_search_results(model_search_cv, sort_results=None):
    """Generate a basic model search report of results."""

    # Check model_search_cv parameter
    if not isinstance(model_search_cv, ModelSearchCV):
        raise ValueError(
            'Parameter `model_search_cv` should be a ModelSearchCV instance.'
        )

    # Check if object is fitted
    check_is_fitted(model_search_cv, 'cv_results_')

    # Select columns
    columns = ['models', 'params'] + [
        results_param
        for results_param in model_search_cv.cv_results_.keys()
        if 'mean_test' in results_param or results_param == 'mean_fit_time'
    ]

    # select results
    results = {
        results_param: values
        for results_param, values in model_search_cv.cv_results_.items()
        if results_param in columns
    }

    # Generate report table
    report = pd.DataFrame(results, columns=columns)

    # Sort results
    if sort_results is not None:

        # Use sort_results parameter as the sorting key
        try:
            report = report.sort_values(
                sort_results, ascending=(sort_results == 'mean_fit_time')
            ).reset_index(drop=True)

        # Key error
        except KeyError:

            # Define error message
            if isinstance(model_search_cv.scoring, list):
                options = ', '.join(
                    ['mean_test_%s' % sc for sc in model_search_cv.scoring]
                )
            else:
                options = 'mean_test_score'
            error_msg = f'Parameter `sort_results` should be one of mean_fit_score, '
            f'{options}. Instead {sort_results} found.'

            # Raise custom error
            raise KeyError(error_msg)

    return report


def summarize_datasets(datasets):
    """Create a summary of imbalanced datasets."""

    # Check datasets format
    check_datasets(datasets)

    # Define summary table columns
    summary_columns = [
        "Dataset name",
        "Features",
        "Instances",
        "Minority instances",
        "Majority instances",
        "Imbalance Ratio",
    ]

    # Define empty summary table
    datasets_summary = []

    # Populate summary table
    for dataset_name, (X, y) in datasets:
        n_instances = Counter(y).values()
        n_minority_instances, n_majority_instances = min(n_instances), max(n_instances)
        values = [
            dataset_name,
            X.shape[1],
            len(X),
            n_minority_instances,
            n_majority_instances,
            round(n_majority_instances / n_minority_instances, 2),
        ]
        datasets_summary.append(values)
    datasets_summary = pd.DataFrame(datasets_summary, columns=summary_columns)

    # Cast to integer columns
    datasets_summary[summary_columns[1:-1]] = datasets_summary[
        summary_columns[1:-1]
    ].astype(int)

    # Sort datasets summary
    datasets_summary = datasets_summary.sort_values('Imbalance Ratio').reset_index(
        drop=True
    )

    return datasets_summary


def calculate_mean_sem_ranking(experiment):
    """Calculate the mean and standard error of oversamplers' ranking
    across datasets for any combination of classifiers
    and metrics."""
    ranking = calculate_ranking(experiment)
    mean_ranking = ranking.groupby(['Classifier', 'Metric']).mean().reset_index()
    sem_ranking = (
        ranking.drop(columns='Dataset')
        .groupby(['Classifier', 'Metric'])
        .sem()
        .reset_index()
    )
    return mean_ranking, sem_ranking


def calculate_mean_sem_scores(experiment):
    """Calculate mean and standard error of scores across datasets."""
    mean_scores = (
        experiment.wide_optimal_.groupby(['Classifier', 'Metric']).mean().reset_index()
    )
    sem_scores = (
        experiment.wide_optimal_.drop(columns='Dataset')
        .groupby(['Classifier', 'Metric'])
        .sem()
        .reset_index()
    )
    return mean_scores, sem_scores


def calculate_mean_sem_perc_diff_scores(experiment, compared_oversamplers=None):
    """Calculate mean and standard error scores' percentage difference."""

    # Calculate percentage difference only for more than one oversampler
    if len(experiment.oversamplers_names_) < 2:
        warnings.warn(
            'More than one oversampler is required to '
            'calculate the mean percentage difference.'
        )

    # Extract oversamplers
    control, test = (
        compared_oversamplers
        if compared_oversamplers is not None
        else experiment.oversamplers_names_[-2:]
    )

    # Calculate percentage difference
    scores = experiment.wide_optimal_[experiment.wide_optimal_[control] > 0]
    perc_diff_scores = pd.DataFrame(
        (100 * (scores[test] - scores[control]) / scores[control]),
        columns=['Difference'],
    )
    perc_diff_scores = pd.concat([scores.iloc[:, :3], perc_diff_scores], axis=1)

    # Calulate mean and std percentage difference
    mean_perc_diff_scores = (
        perc_diff_scores.groupby(['Classifier', 'Metric']).mean().reset_index()
    )
    sem_perc_diff_scores = (
        perc_diff_scores.drop(columns='Dataset')
        .groupby(['Classifier', 'Metric'])
        .sem()
        .reset_index()
    )

    return mean_perc_diff_scores, sem_perc_diff_scores


def _extract_pvalue(df):
    """Extract the p-value."""
    results = friedmanchisquare(*df.iloc[:, 3:].transpose().values.tolist())
    return results.pvalue


def apply_friedman_test(experiment, alpha=0.05):
    """Apply the Friedman test across datasets for every
    combination of classifiers and metrics."""

    # Apply test for more than two oversamplers
    if len(experiment.oversamplers_names_) < 3:
        warnings.warn(
            'More than two oversamplers are required apply the Friedman test.'
        )

    # Calculate p-values
    friedman_test = (
        calculate_ranking(experiment)
        .groupby(['Classifier', 'Metric'])
        .apply(_extract_pvalue)
        .reset_index()
        .rename(columns={0: 'p-value'})
    )

    # Compare p-values to significance level
    friedman_test['Significance'] = friedman_test['p-value'] < alpha

    return friedman_test


def apply_holms_test(experiment, control_oversampler=None):
    """Use the Holm's method to adjust the p-values of a paired difference
    t-test for every combination of classifiers and metrics using a control
    oversampler."""

    # Apply test for more than one oversampler
    if len(experiment.oversamplers_names_) < 2:
        warnings.warn('More than one oversampler is required to apply the Holms test.')

    # Get the oversamplers name
    oversamplers_names = list(experiment.oversamplers_names_)

    # Use the last if no control oversampler is provided
    if control_oversampler is None:
        control_oversampler = oversamplers_names[-1]
    oversamplers_names.remove(control_oversampler)

    # Define empty p-values table
    pvalues = pd.DataFrame()

    # Populate p-values table
    for name in oversamplers_names:
        pvalues_pair = experiment.wide_optimal_.groupby(['Classifier', 'Metric'])[
            [name, control_oversampler]
        ].apply(lambda df: ttest_rel(df[name], df[control_oversampler])[1])
        pvalues_pair = pd.DataFrame(pvalues_pair, columns=[name])
        pvalues = pd.concat([pvalues, pvalues_pair], axis=1)

    # Corrected p-values
    holms_test = pd.DataFrame(
        pvalues.apply(
            lambda col: multipletests(col, method='holm')[1], axis=1
        ).values.tolist(),
        columns=oversamplers_names,
    )
    holms_test = holms_test.set_index(pvalues.index).reset_index()

    return holms_test
