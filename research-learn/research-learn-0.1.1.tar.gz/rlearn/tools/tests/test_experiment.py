"""
Test the imbalanced_analysis module.
"""

from os import remove
from pickle import load

import pytest
import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import ParameterGrid
from sklearn.datasets import make_classification
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import GradientBoostingClassifier
from imblearn.over_sampling import RandomOverSampler, SMOTE, BorderlineSMOTE

from rlearn.tools.experiment import (
    combine_experiments,
    ImbalancedExperiment,
    GROUP_KEYS,
)

RND_SEED = 23
X1, y1 = make_classification(random_state=RND_SEED, n_features=10, n_samples=50)
X2, y2 = make_classification(random_state=RND_SEED + 2, n_features=20, n_samples=50)
X3, y3 = make_classification(random_state=RND_SEED + 5, n_features=5, n_samples=50)
EXPERIMENT = ImbalancedExperiment(
    'test_experiment',
    oversamplers=[
        ('random', RandomOverSampler(), {}),
        ('smote', SMOTE(), {'k_neighbors': [2, 3, 4]}),
    ],
    classifiers=[
        ('dtc', DecisionTreeClassifier(), {'max_depth': [3, 5]}),
        ('knc', KNeighborsClassifier(), {}),
    ],
    random_state=RND_SEED,
)
DATASETS = [('A', (X1, y1)), ('B', (X2, y2)), ('C', (X3, y3))]


def test_combine_experiments_different_n_splits():
    """Test the raising error for combination of experiments for different
    number of splits."""
    experiment1 = clone(EXPERIMENT).set_params(n_splits=10)
    experiment2 = clone(EXPERIMENT)
    with pytest.raises(ValueError):
        combine_experiments([experiment1, experiment2])


def test_combine_experiments_different_n_runs():
    """Test the raising error for combination of experiments for different
    number of runs."""
    experiment1 = clone(EXPERIMENT).set_params(n_runs=3)
    experiment2 = clone(EXPERIMENT)
    with pytest.raises(ValueError):
        combine_experiments([experiment1, experiment2])


def test_combine_experiments_different_rnd_seed():
    """Test the raising error for combination of experiments for
    different random seed."""
    experiment1 = clone(EXPERIMENT).set_params(random_state=RND_SEED + 5)
    experiment2 = clone(EXPERIMENT)
    with pytest.raises(ValueError):
        combine_experiments([experiment1, experiment2])


def test_combine_experiments_no_fit():
    """Test the raising error for combination of experiments when they
    are not fitted."""
    experiment1 = clone(EXPERIMENT)
    experiment2 = clone(EXPERIMENT)
    with pytest.raises(AttributeError):
        combine_experiments([experiment1, experiment2])


def test_combine_experiments_datasets():
    """Test the combination of experiments for different datasets."""

    # Clone and fit experiments
    experiment1 = clone(EXPERIMENT).fit(DATASETS[:-1])
    experiment2 = clone(EXPERIMENT).fit(DATASETS[-1:])
    experiment = combine_experiments([experiment1, experiment2])

    # Assertions
    assert experiment.name == 'combined_experiment'
    assert set(experiment.datasets_names_) == {'A', 'B', 'C'}
    assert set(experiment.oversamplers_names_) == {'random', 'smote'}
    assert set(experiment.classifiers_names_) == {'dtc', 'knc'}
    assert experiment.scoring_cols_ == ['accuracy']
    assert experiment.n_splits == experiment1.n_splits == experiment2.n_splits
    assert experiment.n_runs == experiment1.n_runs == experiment2.n_runs
    assert (
        experiment.random_state == experiment1.random_state == experiment2.random_state
    )
    pd.testing.assert_frame_equal(
        experiment.results_,
        pd.concat([experiment1.results_, experiment2.results_]).sort_index(),
    )


def test_combine_experiments_ovs():
    """Test the combination of experiments for different
    oversamplers."""

    # Clone and fit experiments
    experiment1 = (
        clone(EXPERIMENT)
        .set_params(
            oversamplers=[('bsmote', BorderlineSMOTE(), {'k_neighbors': [2, 5]})]
        )
        .fit(DATASETS)
    )
    experiment2 = clone(EXPERIMENT).fit(DATASETS)
    experiment = combine_experiments([experiment1, experiment2])

    # Assertions
    assert experiment.name == 'combined_experiment'
    assert set(experiment.datasets_names_) == {'A', 'B', 'C'}
    assert set(experiment.oversamplers_names_) == {'random', 'smote', 'bsmote'}
    assert set(experiment.classifiers_names_) == {'dtc', 'knc'}
    assert experiment.scoring_cols_ == ['accuracy']
    assert experiment.n_splits == experiment1.n_splits == experiment2.n_splits
    assert experiment.n_runs == experiment1.n_runs == experiment2.n_runs
    assert (
        experiment.random_state == experiment1.random_state == experiment2.random_state
    )
    pd.testing.assert_frame_equal(
        experiment.results_,
        pd.concat([experiment1.results_, experiment2.results_]).sort_index(),
    )


def test_combine_experiments_clf():
    """Test the combination of experiments for different
    classifiers."""

    # Clone and fit experiments
    experiment1 = (
        clone(EXPERIMENT)
        .set_params(classifiers=[('gbc', GradientBoostingClassifier(), {})])
        .fit(DATASETS)
    )
    experiment2 = clone(EXPERIMENT).fit(DATASETS)
    experiment = combine_experiments([experiment1, experiment2])

    # Assertions
    assert experiment.name == 'combined_experiment'
    assert set(experiment.datasets_names_) == {'A', 'B', 'C'}
    assert set(experiment.oversamplers_names_) == {'random', 'smote'}
    assert set(experiment.classifiers_names_) == {'dtc', 'knc', 'gbc'}
    assert experiment.scoring_cols_ == ['accuracy']
    assert experiment.n_splits == experiment1.n_splits == experiment2.n_splits
    assert experiment.n_runs == experiment1.n_runs == experiment2.n_runs
    assert (
        experiment.random_state == experiment1.random_state == experiment2.random_state
    )
    pd.testing.assert_frame_equal(
        experiment.results_,
        pd.concat([experiment1.results_, experiment2.results_]).sort_index(),
    )


def test_combine_experiments_multiple():
    """Test the combination of experiments for different
    datasets, oversamplers and classifiers."""

    # Clone and fit experiments
    experiment1 = (
        clone(EXPERIMENT)
        .set_params(
            oversamplers=[('bsmote', BorderlineSMOTE(), {'k_neighbors': [2, 5]})],
            classifiers=[('gbc', GradientBoostingClassifier(), {})],
        )
        .fit(DATASETS[:-1])
    )
    experiment2 = clone(EXPERIMENT).fit(DATASETS[-1:])
    experiment = combine_experiments([experiment1, experiment2])

    # Assertions
    assert experiment.name == 'combined_experiment'
    assert set(experiment.datasets_names_) == {'A', 'B', 'C'}
    assert set(experiment.oversamplers_names_) == {'random', 'smote', 'bsmote'}
    assert set(experiment.classifiers_names_) == {'dtc', 'knc', 'gbc'}
    assert experiment.scoring_cols_ == ['accuracy']
    assert experiment.n_splits == experiment1.n_splits == experiment2.n_splits
    assert experiment.n_runs == experiment1.n_runs == experiment2.n_runs
    assert (
        experiment.random_state == experiment1.random_state == experiment2.random_state
    )
    pd.testing.assert_frame_equal(
        experiment.results_,
        pd.concat([experiment1.results_, experiment2.results_]).sort_index(),
    )


def test_combine_experiments_wrong_multiple():
    """Test the combination of experiments for different
    datasets, oversamplers and classifiers and scoring."""

    # Clone and fit experiments
    experiment1 = (
        clone(EXPERIMENT)
        .set_params(
            oversamplers=[('bsmote', BorderlineSMOTE(), {'k_neighbors': [2, 5]})],
            classifiers=[('gbc', GradientBoostingClassifier(), {})],
            scoring='f1',
        )
        .fit(DATASETS[:-1])
    )
    experiment2 = clone(EXPERIMENT).fit(DATASETS[-1:])
    with pytest.raises(ValueError):
        combine_experiments([experiment1, experiment2])


def test_combine_experiments_scoring():
    """Test the combination of experiments for different
    scorers."""

    # Clone and fit experiments
    experiment1 = clone(EXPERIMENT).set_params(scoring='f1').fit(DATASETS)
    experiment2 = clone(EXPERIMENT).fit(DATASETS)
    experiment = combine_experiments([experiment1, experiment2])

    # Assertions
    assert experiment.name == 'combined_experiment'
    assert set(experiment.datasets_names_) == {'A', 'B', 'C'}
    assert set(experiment.oversamplers_names_) == {'random', 'smote'}
    assert set(experiment.classifiers_names_) == {'dtc', 'knc'}
    assert experiment.scoring_cols_ == ['accuracy', 'f1']
    assert experiment.n_splits == experiment1.n_splits == experiment2.n_splits
    assert experiment.n_runs == experiment1.n_runs == experiment2.n_runs
    assert (
        experiment.random_state == experiment1.random_state == experiment2.random_state
    )
    pd.testing.assert_frame_equal(
        experiment.results_,
        pd.concat(
            [experiment1.results_, experiment2.results_[['accuracy']]], axis=1
        ).sort_index(),
    )


def test_combine_experiments_fit():
    """Test the combination of experiments fit method."""

    # Clone and fit experiments
    experiment1 = clone(EXPERIMENT).fit(DATASETS[:-1])
    experiment2 = clone(EXPERIMENT).fit(DATASETS[-1:])
    experiment = combine_experiments([experiment1, experiment2])
    fitted_experiment = clone(experiment).fit(DATASETS)

    # Assertions
    attributes = [
        'datasets_names_',
        'oversamplers_names_',
        'classifiers_names_',
        'scoring_cols_',
    ]
    for attr_name in attributes:
        assert getattr(experiment, attr_name) == getattr(fitted_experiment, attr_name)


@pytest.mark.parametrize(
    'scoring,n_runs', [(None, 2), ('accuracy', 3), (['accuracy', 'recall'], 2)]
)
def test_experiment_initialization(scoring, n_runs):
    """Test the initialization of experiment's parameters."""

    # Clone and fit experiment
    experiment = clone(EXPERIMENT)
    experiment.set_params(scoring=scoring, n_runs=n_runs)
    experiment.fit(DATASETS)

    # Assertions
    if scoring is None:
        assert experiment.scoring_cols_ == ['accuracy']
    elif isinstance(scoring, str):
        assert experiment.scoring_cols_ == [scoring]
    else:
        assert experiment.scoring_cols_ == scoring
    assert experiment.datasets_names_ == ('A', 'B', 'C')
    assert experiment.oversamplers_names_ == ('random', 'smote')
    assert experiment.classifiers_names_ == ('dtc', 'knc')
    assert len(experiment.estimators_) == 4


def test_results():
    """Test the results of experiment."""

    # Clone and fit experiment
    experiment = clone(EXPERIMENT).fit(DATASETS)

    # Results
    results_cols = experiment.results_.reset_index().columns
    results_cols = results_cols.get_level_values(0).tolist()[:-2]
    assert results_cols == GROUP_KEYS

    n_params = len(ParameterGrid(experiment.param_grids_))
    assert len(experiment.results_) == len(DATASETS) * n_params // experiment.n_runs

    # Optimal results
    datasets_names = set(experiment.optimal_.Dataset.unique())
    assert datasets_names == set(experiment.datasets_names_)

    oversamplers_names = set(experiment.optimal_.Oversampler.unique())
    assert oversamplers_names == set(experiment.oversamplers_names_)

    classifiers_names = set(experiment.optimal_.Classifier.unique())
    assert classifiers_names == set(experiment.classifiers_names_)

    optimal_n_rows = len(experiment.optimal_)
    assert optimal_n_rows == len(datasets_names) * len(oversamplers_names) * len(
        classifiers_names
    )

    # Wide optimal results
    datasets_names = set(experiment.wide_optimal_.Dataset.unique())
    assert datasets_names == set(experiment.datasets_names_)

    classifiers_names = set(experiment.wide_optimal_.Classifier.unique())
    assert classifiers_names == set(experiment.classifiers_names_)

    assert set(experiment.oversamplers_names_).issubset(
        experiment.wide_optimal_.columns
    )
    assert len(experiment.wide_optimal_) == len(datasets_names) * len(classifiers_names)


def test_dump():
    """Test the dump method."""
    # Clone and fit experiment
    experiment = clone(EXPERIMENT).fit(DATASETS)

    # Dump experiment
    experiment.dump()

    # Assertions
    file_name = f'{experiment.name}.pkl'
    with open(file_name, 'rb') as file:
        experiment = load(file)
        attr_names = [
            attr_name for attr_name in vars(experiment).keys() if attr_name[-1] == '_'
        ]
        for attr_name in attr_names:
            attr1, attr2 = (
                getattr(experiment, attr_name),
                getattr(experiment, attr_name),
            )
            if isinstance(attr1, pd.core.frame.DataFrame):
                pd.testing.assert_frame_equal(attr1, attr2)

    # Remove pickled file
    remove(file_name)
