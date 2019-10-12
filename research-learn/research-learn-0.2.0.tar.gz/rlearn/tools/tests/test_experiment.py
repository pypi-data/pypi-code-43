"""
Test the imbalanced_analysis module.
"""

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
    select_results,
    combine_results,
    ImbalancedExperiment,
    GROUP_KEYS,
)

RND_SEED = 23
X1, y1 = make_classification(random_state=RND_SEED, n_features=10, n_samples=50)
X2, y2 = make_classification(random_state=RND_SEED + 2, n_features=20, n_samples=50)
X3, y3 = make_classification(random_state=RND_SEED + 5, n_features=5, n_samples=50)
EXPERIMENT = ImbalancedExperiment(
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


def test_select_results_raise_error():
    """Test raising of error on selection of results."""
    imbalanced_results = clone(EXPERIMENT).fit(DATASETS).results_
    with pytest.raises(ValueError):
        select_results(imbalanced_results, oversamplers_names=['random', 'bsmote'])
    with pytest.raises(ValueError):
        select_results(imbalanced_results, classifiers_names=['kn'])
    with pytest.raises(ValueError):
        select_results(imbalanced_results, datasets_names=['D', 'A'])
    with pytest.raises(ValueError):
        select_results(imbalanced_results, datasets_names=['f1'])


@pytest.mark.parametrize(
    'oversamplers_names, classifiers_names, datasets_names, scoring_cols',
    [(None, None, None, None), (['random'], ['knc'], ['A', 'C'], ['f1'])],
)
def test_select_results(
    oversamplers_names, classifiers_names, datasets_names, scoring_cols
):
    """Test selection of results."""
    experiment = clone(EXPERIMENT).set_params(scoring=['f1', 'accuracy']).fit(DATASETS)
    selected_results = select_results(
        experiment.results_,
        oversamplers_names,
        classifiers_names,
        datasets_names,
        scoring_cols,
    )
    results = selected_results.reset_index()
    if oversamplers_names is not None:
        assert set(results.Oversampler) == set(oversamplers_names)
    else:
        assert set(results.Oversampler) == set(experiment.oversamplers_names_)
    if classifiers_names is not None:
        assert set(results.Classifier) == set(classifiers_names)
    else:
        assert set(results.Classifier) == set(experiment.classifiers_names_)
    if datasets_names is not None:
        assert set(results.Dataset) == set(datasets_names)
    else:
        assert set(results.Dataset) == set(experiment.datasets_names_)
    unique_scoring_cols = set([scorer[0] for scorer in selected_results.columns])
    if scoring_cols is not None:
        assert unique_scoring_cols == set(scoring_cols)
    else:
        assert unique_scoring_cols == set(experiment.scoring_cols_)


def test_combine_results_datasets():
    """Test the combination of experimental results for different datasets."""

    # Clone and fit experiments
    experiment1 = clone(EXPERIMENT).fit(DATASETS[:-1])
    experiment2 = clone(EXPERIMENT).fit(DATASETS[-1:])

    # Extract combined results
    combined_results = combine_results(experiment1.results_, experiment2.results_)
    results = combined_results.reset_index()

    # Assertions
    assert set(results.Dataset) == {'A', 'B', 'C'}
    assert set(results.Oversampler) == {'random', 'smote'}
    assert set(results.Classifier) == {'dtc', 'knc'}
    assert set([scorer[0] for scorer in combined_results.columns]) == set(['accuracy'])
    pd.testing.assert_frame_equal(
        combined_results,
        pd.concat([experiment1.results_, experiment2.results_]).sort_index(),
    )


def test_combine_results_ovrs():
    """Test the combination of experimental results for different oversamplers."""

    # Clone and fit experiments
    experiment1 = (
        clone(EXPERIMENT)
        .set_params(
            oversamplers=[('bsmote', BorderlineSMOTE(), {'k_neighbors': [2, 5]})]
        )
        .fit(DATASETS)
    )
    experiment2 = clone(EXPERIMENT).fit(DATASETS)

    # Extract combined results
    combined_results = combine_results(experiment1.results_, experiment2.results_)
    results = combined_results.reset_index()

    # Assertions
    assert set(results.Dataset) == {'A', 'B', 'C'}
    assert set(results.Oversampler) == {'random', 'smote', 'bsmote'}
    assert set(results.Classifier) == {'dtc', 'knc'}
    assert set([scorer[0] for scorer in combined_results.columns]) == set(['accuracy'])
    pd.testing.assert_frame_equal(
        combined_results,
        pd.concat([experiment1.results_, experiment2.results_]).sort_index(),
    )


def test_combine_results_clfs():
    """Test the combination of experimental results for different classifiers."""

    # Clone and fit experiments
    experiment1 = (
        clone(EXPERIMENT)
        .set_params(classifiers=[('gbc', GradientBoostingClassifier(), {})])
        .fit(DATASETS)
    )
    experiment2 = clone(EXPERIMENT).fit(DATASETS)

    # Extract combined results
    combined_results = combine_results(experiment1.results_, experiment2.results_)
    results = combined_results.reset_index()

    # Assertions
    assert set(results.Dataset) == {'A', 'B', 'C'}
    assert set(results.Oversampler) == {'random', 'smote'}
    assert set(results.Classifier) == {'dtc', 'knc', 'gbc'}
    assert set([scorer[0] for scorer in combined_results.columns]) == set(['accuracy'])
    pd.testing.assert_frame_equal(
        combined_results,
        pd.concat([experiment1.results_, experiment2.results_]).sort_index(),
    )


def test_combine_results_multiple():
    """Test the combination of experimental results for different
    datasets, oversamplers and classifiers."""

    # Clone and fit experiments
    experiment1 = (
        clone(EXPERIMENT)
        .set_params(
            oversamplers=[('bsmote', BorderlineSMOTE(), {'k_neighbors': [2, 5]})],
            classifiers=[('gbc', GradientBoostingClassifier(), {})],
            scoring=['accuracy', 'f1'],
        )
        .fit(DATASETS[:-1])
    )
    experiment2 = (
        clone(EXPERIMENT).set_params(scoring=['accuracy', 'f1']).fit(DATASETS[-1:])
    )

    # Extract combined results
    combined_results = combine_results(experiment1.results_, experiment2.results_)
    results = combined_results.reset_index()

    # Assertions
    assert set(results.Dataset) == {'A', 'B', 'C'}
    assert set(results.Oversampler) == {'random', 'smote', 'bsmote'}
    assert set(results.Classifier) == {'dtc', 'knc', 'gbc'}
    assert set([scorer[0] for scorer in combined_results.columns]) == set(
        ['accuracy', 'f1']
    )
    pd.testing.assert_frame_equal(
        combined_results,
        pd.concat([experiment1.results_, experiment2.results_]).sort_index(),
    )


def test_combine_experiments_wrong_multiple():
    """Test the combination of experimental results for different
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
        combine_results(experiment1.results_, experiment2.results_)


def test_combine_experiments_scoring():
    """Test the combination of experiments for different
    scorers."""

    # Clone and fit experiments
    experiment1 = clone(EXPERIMENT).set_params(scoring='f1').fit(DATASETS)
    experiment2 = clone(EXPERIMENT).fit(DATASETS)

    # Extract combined results
    combined_results = combine_results(experiment1.results_, experiment2.results_)
    results = combined_results.reset_index()

    # Assertions
    assert set(results.Dataset) == {'A', 'B', 'C'}
    assert set(results.Oversampler) == {'random', 'smote'}
    assert set(results.Classifier) == {'dtc', 'knc'}
    assert set([scorer[0] for scorer in combined_results.columns]) == set(
        ['accuracy', 'f1']
    )
    pd.testing.assert_frame_equal(
        combined_results,
        pd.concat(
            [experiment1.results_, experiment2.results_[['accuracy']]], axis=1
        ).sort_index(),
    )


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
    results_cols = results_cols.get_level_values(0).tolist()[: len(GROUP_KEYS)]
    assert results_cols == GROUP_KEYS

    n_params = len(ParameterGrid(experiment.param_grids_))
    assert len(experiment.results_) == len(DATASETS) * n_params // experiment.n_runs
