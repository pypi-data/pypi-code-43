"""
Test the validation module.
"""

from itertools import product

import pytest
from sklearn.datasets import make_classification
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from imblearn.over_sampling import SMOTE, BorderlineSMOTE
from imblearn.pipeline import Pipeline

from rlearn.utils.validation import (
    check_param_grids,
    check_datasets,
    check_random_states,
    check_oversamplers_classifiers,
)


def test_check_param_grids_empty():
    """Test the case when parameter grid is empty."""
    init_param_grids = {}
    param_grids = check_param_grids(init_param_grids, ['svc', 'dtc'])
    exp_param_grids = [{'est_name': ['svc']}, {'est_name': ['dtc']}]
    assert all([param_grid in exp_param_grids for param_grid in param_grids])


def test_check_param_grids_given_est_name():
    """Test the case when estimator name is given."""
    init_param_grids = {'svr__C': [0.1, 1.0], 'est_name': ['svr']}
    param_grids = check_param_grids(init_param_grids, ['svr', 'dtc'])
    exp_param_grids = [
        {'svr__C': [0.1], 'est_name': ['svr']},
        {'svr__C': [1.0], 'est_name': ['svr']},
        {'est_name': ['dtc']},
    ]
    assert all([param_grid in exp_param_grids for param_grid in param_grids])


def test_check_param_grids_single():
    """Test the check of a single parameter grid."""
    init_param_grids = {'svr__C': [0.1, 1.0], 'svr__kernel': ['rbf', 'linear']}
    param_grids = check_param_grids(init_param_grids, ['lr', 'svr', 'dtr'])
    exp_param_grids = [
        {'svr__C': [0.1], 'svr__kernel': ['rbf'], 'est_name': ['svr']},
        {'svr__C': [1.0], 'svr__kernel': ['rbf'], 'est_name': ['svr']},
        {'svr__C': [0.1], 'svr__kernel': ['linear'], 'est_name': ['svr']},
        {'svr__C': [1.0], 'svr__kernel': ['linear'], 'est_name': ['svr']},
        {'est_name': ['dtr']},
        {'est_name': ['lr']},
    ]
    assert all([param_grid in exp_param_grids for param_grid in param_grids])


def test_check_param_grids_list():
    """Test the check of a list of parameter grids."""
    init_param_grids = [
        {'svr__C': [0.1, 1.0], 'svr__kernel': ['rbf', 'linear']},
        {'dtr__max_depth': [3, 5], 'est_name': ['dtr']},
    ]
    param_grids = check_param_grids(init_param_grids, ['lr', 'svr', 'knr', 'dtr'])
    exp_param_grids = [
        {'svr__C': [0.1], 'svr__kernel': ['rbf'], 'est_name': ['svr']},
        {'svr__C': [1.0], 'svr__kernel': ['rbf'], 'est_name': ['svr']},
        {'svr__C': [0.1], 'svr__kernel': ['linear'], 'est_name': ['svr']},
        {'svr__C': [1.0], 'svr__kernel': ['linear'], 'est_name': ['svr']},
        {'dtr__max_depth': [3], 'est_name': ['dtr']},
        {'dtr__max_depth': [5], 'est_name': ['dtr']},
        {'est_name': ['lr']},
        {'est_name': ['knr']},
    ]
    assert all([param_grid in exp_param_grids for param_grid in param_grids])


def test_check_param_grids_wrong_est_name():
    """Test wrong estimator name."""
    param_grids = {'svr__C': [0.1, 1.0], 'est_name': ['svc']}
    with pytest.raises(ValueError):
        check_param_grids(param_grids, ['svr', 'dtc'])


def test_check_param_grids_wrong_est_names():
    """Test wrong estimator names."""
    param_grids = {'svc__C': [0.1, 1.0], 'svc__kernel': ['rbf', 'linear']}
    with pytest.raises(ValueError):
        check_param_grids(param_grids, ['svr', 'dtc'])


def test_check_oversamplers_classifiers():
    """Test the check of oversamplers and classifiers."""

    # Initialization
    n_runs = 5
    rnd_seed = 0
    oversamplers = [
        ('ovs', BorderlineSMOTE(), [{'k_neighbors': [2, 4]}, {'m_neighbors': [6, 8]}])
    ]
    classifiers = [('clf', DecisionTreeClassifier(), {'max_depth': [3, 5]})]

    # Estimators and parameters grids
    estimators, param_grids = check_oversamplers_classifiers(
        oversamplers, classifiers, rnd_seed, n_runs
    )
    names, pips = zip(*estimators)
    steps = [
        [(step[0], step[1].__class__.__name__) for step in pip.steps] for pip in pips
    ]

    # Expected estimators and parameters grids
    exp_name = 'ovs|clf'
    exp_steps = [('ovs', 'BorderlineSMOTE'), ('clf', 'DecisionTreeClassifier')]
    exp_random_states = check_random_states(rnd_seed, n_runs)
    partial_param_grids = []
    for k_neighbors, max_depth in product([2, 4], [3, 5]):
        partial_param_grids.append(
            {
                'ovs|clf__ovs__k_neighbors': [k_neighbors],
                'ovs|clf__clf__max_depth': [max_depth],
            }
        )
    for m_neighbors, max_depth in product([6, 8], [3, 5]):
        partial_param_grids.append(
            {
                'ovs|clf__ovs__m_neighbors': [m_neighbors],
                'ovs|clf__clf__max_depth': [max_depth],
            }
        )
    exp_param_grids = []
    for rnd_seed, partial_param_grid in product(exp_random_states, partial_param_grids):
        partial_param_grid = partial_param_grid.copy()
        partial_param_grid.update(
            {
                'est_name': ['ovs|clf'],
                'ovs|clf__ovs__random_state': [rnd_seed],
                'ovs|clf__clf__random_state': [rnd_seed],
            }
        )
        exp_param_grids.append(partial_param_grid)

    # Assertions
    assert names[0] == exp_name
    assert steps[0] == exp_steps
    assert len(param_grids) == len(exp_param_grids)
    assert all([param_grid in exp_param_grids for param_grid in param_grids])


def test_check_oversamplers_classifiers_none():
    """Test the check of oversamplers and classifiers for no oversampler."""

    # Initialization
    n_runs = 2
    rnd_seed = 12
    oversamplers = [('ovs', None, {})]
    classifiers = [('clf', DecisionTreeClassifier(), {'max_depth': [3, 5, 8]})]

    # Estimators and parameters grids
    estimators, param_grids = check_oversamplers_classifiers(
        oversamplers, classifiers, rnd_seed, n_runs
    )
    names, pips = zip(*estimators)
    steps = [
        [(step[0], step[1].__class__.__name__) for step in pip.steps] for pip in pips
    ]

    # Expected names, steps and parameter grids
    exp_name = 'ovs|clf'
    exp_steps = [('ovs', 'FunctionTransformer'), ('clf', 'DecisionTreeClassifier')]
    exp_random_states = check_random_states(rnd_seed, n_runs)
    partial_param_grids = []
    for max_depth in [3, 5, 8]:
        partial_param_grids.append({'ovs|clf__clf__max_depth': [max_depth]})
    exp_param_grids = []
    for rnd_seed, partial_param_grid in product(exp_random_states, partial_param_grids):
        partial_param_grid = partial_param_grid.copy()
        partial_param_grid.update(
            {'est_name': ['ovs|clf'], 'ovs|clf__clf__random_state': [rnd_seed]}
        )
        exp_param_grids.append(partial_param_grid)

    # Assertions
    assert names[0] == exp_name
    assert steps[0] == exp_steps
    assert len(param_grids) == len(exp_param_grids)
    assert all([param_grid in exp_param_grids for param_grid in param_grids])


def test_check_oversamplers_classifiers_pipeline():
    """Test the check of oversampler and classifiers pipelines."""

    # Initialization
    n_runs = 2
    rnd_seed = 3
    oversamplers = [
        (
            'ovs',
            Pipeline([('scaler', MinMaxScaler()), ('smote', SMOTE())]),
            {'scaler__feature_range': [(0, 1), (0, 0.5)], 'smote__k_neighbors': [3, 5]},
        )
    ]
    classifiers = [
        (
            'clf',
            Pipeline([('pca', PCA()), ('dtc', DecisionTreeClassifier())]),
            {'pca__n_components': [4, 8], 'dtc__max_depth': [3, 5]},
        )
    ]

    # Estimators and parameters grids
    estimators, param_grids = check_oversamplers_classifiers(
        oversamplers, classifiers, rnd_seed, n_runs
    )
    names, pips = zip(*estimators)
    steps = [
        [(step[0], step[1].__class__.__name__) for step in pip.steps] for pip in pips
    ]

    # Expected names, steps and parameter grids
    exp_name = 'ovs|clf'
    exp_steps = [
        ('scaler', 'MinMaxScaler'),
        ('smote', 'SMOTE'),
        ('pca', 'PCA'),
        ('dtc', 'DecisionTreeClassifier'),
    ]
    exp_random_states = check_random_states(rnd_seed, n_runs)
    partial_param_grids = []
    for feature_range, k_neighbors, n_components, max_depth in product(
        [(0, 1), (0, 0.5)], [3, 5], [4, 8], [3, 5]
    ):
        partial_param_grids.append(
            {
                'ovs|clf__scaler__feature_range': [feature_range],
                'ovs|clf__smote__k_neighbors': [k_neighbors],
                'ovs|clf__pca__n_components': [n_components],
                'ovs|clf__dtc__max_depth': [max_depth],
            }
        )
    exp_param_grids = []
    for rnd_seed, partial_param_grid in product(exp_random_states, partial_param_grids):
        partial_param_grid = partial_param_grid.copy()
        partial_param_grid.update(
            {
                'est_name': ['ovs|clf'],
                'ovs|clf__smote__random_state': [rnd_seed],
                'ovs|clf__dtc__random_state': [rnd_seed],
                'ovs|clf__pca__random_state': [rnd_seed],
            }
        )
        exp_param_grids.append(partial_param_grid)

    # Assertions
    assert names[0] == exp_name
    assert steps[0] == exp_steps
    assert len(param_grids) == len(exp_param_grids)
    assert all([param_grid in exp_param_grids for param_grid in param_grids])


def test_check_datasets_names():
    """Test the check of datasets names."""
    data = make_classification(random_state=0)
    with pytest.raises(ValueError):
        check_datasets([('ds1', data), ('ds1', data)])


def test_check_datasets_format():
    """Test the check of datasets format of data."""
    data = make_classification(random_state=5)
    with pytest.raises(ValueError):
        check_datasets([('ds1', data), ('ds2', data[1])])
