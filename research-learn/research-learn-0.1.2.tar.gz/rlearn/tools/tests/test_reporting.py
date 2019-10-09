"""
Test the model_analysis module.
"""

import pytest
from numpy.testing import assert_array_equal
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.datasets import make_classification

from rlearn.tools import (
    ImbalancedExperiment,
    report_model_search_results,
    summarize_datasets,
    calculate_ranking,
    calculate_mean_sem_ranking,
    calculate_mean_sem_scores,
    calculate_mean_sem_perc_diff_scores,
    apply_friedman_test,
    apply_holms_test,
)
from rlearn.tools.tests import DATASETS, CLASSIFIERS, OVERSAMPLERS
from rlearn.model_selection import ModelSearchCV

EXPERIMENT = ImbalancedExperiment(
    'test_experiment',
    OVERSAMPLERS,
    CLASSIFIERS,
    scoring=None,
    n_splits=3,
    n_runs=3,
    random_state=0,
).fit(DATASETS)


@pytest.mark.parametrize(
    'scoring,sort_results',
    [
        (None, None),
        (None, 'mean_fit_time'),
        (None, 'mean_test_score'),
        ('accuracy', None),
        ('recall', 'mean_fit_time'),
        ('recall', 'mean_test_score'),
        (['accuracy', 'recall'], None),
        (['accuracy', 'recall'], 'mean_fit_time'),
        (['accuracy', 'recall'], 'mean_test_accuracy'),
        (['accuracy', 'recall'], 'mean_test_recall'),
    ],
)
def test_report_model_search_results(scoring, sort_results):
    """Test the output of the model search report function."""
    X, y = make_classification(random_state=0)
    classifiers = [
        ('knn', KNeighborsClassifier()),
        ('dtc', DecisionTreeClassifier()),
        (
            'pip',
            Pipeline([('scaler', MinMaxScaler()), ('knn', KNeighborsClassifier())]),
        ),
    ]
    classifiers_param_grids = [
        {'dtc__max_depth': [2, 5]},
        {'pip__knn__n_neighbors': [3, 5]},
    ]
    mscv = ModelSearchCV(
        classifiers,
        classifiers_param_grids,
        scoring=scoring,
        refit=False,
        verbose=False,
    )
    mscv.fit(X, y)
    report = report_model_search_results(mscv, sort_results)
    assert len(report.columns) == (
        len(mscv.scorer_) if isinstance(mscv.scoring, list) else 1
    ) + len(['models', 'params', 'mean_fit_time'])
    if sort_results is not None:
        assert_array_equal(
            report[sort_results],
            report[sort_results].sort_values(
                ascending=(sort_results == 'mean_fit_time')
            ),
        )


def test_datasets_summary():
    """Test the dataset's summary."""
    datasets_summary = summarize_datasets(DATASETS)
    expected_datasets_summary = pd.DataFrame(
        {
            'Dataset name': ['C', 'B', 'A'],
            'Features': [5, 10, 20],
            'Instances': [100, 100, 100],
            'Minority instances': [40, 20, 10],
            'Majority instances': [60, 80, 90],
            'Imbalance Ratio': [1.5, 4.0, 9.0],
        }
    )
    pd.testing.assert_frame_equal(
        datasets_summary, expected_datasets_summary, check_dtype=False
    )


def test_ranking_results():
    """Test the ranking results of experiment."""
    ranking = calculate_ranking(EXPERIMENT)
    assert set(ranking.Dataset.unique()) == set(EXPERIMENT.datasets_names_)
    assert set(ranking.Classifier.unique()) == set(EXPERIMENT.classifiers_names_)
    assert set(EXPERIMENT.oversamplers_names_).issubset(ranking.columns)
    assert len(ranking) == len(DATASETS) * len(CLASSIFIERS)


def test_mean_sem_ranking():
    """Test the mean ranking results of experiment."""
    mean_ranking, sem_ranking = calculate_mean_sem_ranking(EXPERIMENT)
    assert set(mean_ranking.Classifier.unique()) == set(EXPERIMENT.classifiers_names_)
    assert set(sem_ranking.Classifier.unique()) == set(EXPERIMENT.classifiers_names_)
    assert set(EXPERIMENT.oversamplers_names_).issubset(mean_ranking.columns)
    assert set(EXPERIMENT.oversamplers_names_).issubset(sem_ranking.columns)
    assert len(mean_ranking) == len(CLASSIFIERS)
    assert len(sem_ranking) == len(CLASSIFIERS)


def test_mean_sem_scores():
    """Test the mean scores results of experiment."""
    mean_scores, sem_scores = calculate_mean_sem_scores(EXPERIMENT)
    assert set(mean_scores.Classifier.unique()) == set(EXPERIMENT.classifiers_names_)
    assert set(sem_scores.Classifier.unique()) == set(EXPERIMENT.classifiers_names_)
    assert set(EXPERIMENT.oversamplers_names_).issubset(mean_scores.columns)
    assert set(EXPERIMENT.oversamplers_names_).issubset(sem_scores.columns)
    assert len(mean_scores) == len(CLASSIFIERS)
    assert len(sem_scores) == len(CLASSIFIERS)


def test_mean_sem_perc_diff_scores():
    """Test the mean percentage difference of scores."""
    mean_perc_diff_scores, sem_perc_diff_scores = calculate_mean_sem_perc_diff_scores(
        EXPERIMENT, compared_oversamplers=None
    )
    assert set(mean_perc_diff_scores.Classifier.unique()) == set(
        EXPERIMENT.classifiers_names_
    )
    assert set(sem_perc_diff_scores.Classifier.unique()) == set(
        EXPERIMENT.classifiers_names_
    )
    assert set(mean_perc_diff_scores.columns) == set(
        ['Classifier', 'Metric', 'Difference']
    )
    assert set(sem_perc_diff_scores.columns) == set(
        ['Classifier', 'Metric', 'Difference']
    )
    assert len(mean_perc_diff_scores) == len(CLASSIFIERS)
    assert len(sem_perc_diff_scores) == len(CLASSIFIERS)


def test_friedman_test():
    """Test the results of friedman test."""
    friedman_test = apply_friedman_test(EXPERIMENT, alpha=0.05)
    assert set(friedman_test.Classifier.unique()) == set(EXPERIMENT.classifiers_names_)
    assert len(friedman_test) == len(CLASSIFIERS)


def test_holms_test():
    """Test the results of holms test."""
    holms_test = apply_holms_test(EXPERIMENT, control_oversampler=None)
    assert set(holms_test.Classifier.unique()) == set(EXPERIMENT.classifiers_names_)
    assert len(holms_test) == len(CLASSIFIERS)
