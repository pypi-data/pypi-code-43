"""
It supports the design and execution of
machine learning experiments.
"""

# Author: Georgios Douzas <gdouzas@icloud.com>
# Licence: MIT

from os.path import join
from pickle import dump

from tqdm import tqdm
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, clone
from sklearn.model_selection import StratifiedKFold

from ..utils import check_datasets, check_oversamplers_classifiers
from ..model_selection import ModelSearchCV

GROUP_KEYS = ['Dataset', 'Oversampler', 'Classifier', 'params']


def filter_experiment(
    experiment,
    oversamplers_names=None,
    classifiers_names=None,
    datasets_names=None,
    scoring_cols=None,
):
    """Filter experimental results and return an experiment object."""

    # Check input parameters
    error_msg = 'Parameter `{}` should be `None` or a subset '
    'of the experiments corresponding attribute.'
    if oversamplers_names is not None:
        try:
            if not set(oversamplers_names).issubset(experiment.oversamplers_names_):
                raise ValueError(error_msg.format(oversamplers_names))
        except TypeError:
            raise ValueError(error_msg.format(oversamplers_names))
    if classifiers_names is not None:
        try:
            if not set(classifiers_names).issubset(experiment.classifiers_names_):
                raise ValueError(error_msg.format(classifiers_names))
        except TypeError:
            raise ValueError(error_msg.format(classifiers_names))
    if datasets_names is not None:
        try:
            if not set(datasets_names).issubset(experiment.datasets_names_):
                raise ValueError(error_msg.format(datasets_names))
        except TypeError:
            raise ValueError(error_msg.format(datasets_names))
    if scoring_cols is not None:
        try:
            if not set(scoring_cols).issubset(experiment.scoring_cols_):
                raise ValueError(error_msg.format(scoring_cols))
        except TypeError:
            raise ValueError(error_msg.format(scoring_cols))

    # Clone experiment
    filtered_experiment = clone(experiment)

    # Extract results
    results = experiment.results_.reset_index()

    # Oversamplers
    if oversamplers_names is not None:
        mask_ovr = results.Oversampler.isin(oversamplers_names)
        filtered_experiment.oversamplers = [
            ovs
            for ovs in filtered_experiment.oversamplers
            if ovs[0] in oversamplers_names
        ]
        filtered_experiment.oversamplers_names_ = tuple(oversamplers_names)
    else:
        mask_ovr = True
        filtered_experiment.oversamplers_names_ = experiment.oversamplers_names_

    # Classifiers
    if classifiers_names is not None:
        mask_clf = results.Classifier.isin(classifiers_names)
        filtered_experiment.classifiers = [
            clf
            for clf in filtered_experiment.classifiers
            if clf[0] in classifiers_names
        ]
        filtered_experiment.classifiers_names_ = tuple(classifiers_names)
    else:
        mask_clf = True
        filtered_experiment.classifiers_names_ = experiment.classifiers_names_

    # Datasets
    if datasets_names is not None:
        mask_ds = results.Classifier.isin(datasets_names)
        filtered_experiment.datasets_names_ = tuple(datasets_names)
    else:
        mask_ds = True
        filtered_experiment.datasets_names_ = experiment.datasets_names_

    # Define boolean mask
    mask = mask_ovr & mask_clf & mask_ds
    if mask is True:
        mask = np.repeat(True, len(results)).reshape(-1, 1)
    else:
        mask = mask.values.reshape(-1, 1)

    # Set scoring columns and results
    filtered_experiment.scoring_cols_ = (
        experiment.scoring_cols_ if scoring_cols is None else scoring_cols
    )
    filtered_experiment.results_ = experiment.results_[mask][
        filtered_experiment.scoring_cols_
    ]

    return filtered_experiment


def combine_experiments(experiments, name='combined_experiment'):
    """Combines the results of multiple experiments into a single one."""

    # Check compatibility
    attributes = ['n_splits', 'n_runs', 'random_state']
    for attr_name in attributes:
        values = []
        for experiment in experiments:
            values.append(getattr(experiment, attr_name))
        values = set(values)
        if len(values) > 1:
            raise ValueError(
                f'Experiments can not be combined. Parameter `{attr_name}` '
                f'should be unique across different experiments.'
            )

    # Extract results
    try:
        results = pd.concat(
            [experiment.results_ for experiment in experiments], axis=1, sort=True
        )
        if len(set([scoring for scoring, _ in results.columns])) == 1:
            values = np.apply_along_axis(
                arr=results.values, func1d=lambda row: row[~np.isnan(row)][0:2], axis=1
            )
            results = pd.DataFrame(
                values, index=results.index, columns=results.columns[0:2]
            )
        if results.isna().any().any():
            raise ValueError(
                'Experiment with different oversamplers, classifiers or datasets '
                'should have the same scoring and vice-versa.'
            )
    except AttributeError:
        raise AttributeError('All experiments should be run before combined.')

    # Generate experiment parameters
    oversamplers, classifiers, scoring = [], [], set()
    for experiment in experiments:
        scoring = scoring.union(experiment.scoring_cols_)
        for ovs in experiment.oversamplers or not oversamplers:
            ovs_names = [name for name, *_ in oversamplers]
            if ovs[0] not in ovs_names:
                oversamplers.append(ovs)
        for clf in experiment.classifiers or not classifiers:
            clf_names = [name for name, *_ in classifiers]
            if clf[0] not in clf_names:
                classifiers.append(clf)
    scoring = sorted(scoring)

    # Combine results
    combined_experiment = ImbalancedExperiment(
        name,
        oversamplers,
        classifiers,
        scoring,
        experiments[0].n_splits,
        experiments[0].n_runs,
        experiments[0].random_state,
    )
    combined_experiment.datasets_names_ = tuple(
        np.unique(results.index.get_level_values('Dataset'))
    )
    combined_experiment._initialize()
    combined_experiment.results_ = results

    # Create attributes
    combined_experiment._calculate_optimal_results()._calculate_wide_optimal_results()

    return combined_experiment


class ImbalancedExperiment(BaseEstimator):
    """Define a classification experiment on multiple imbalanced datasets."""

    def __init__(
        self,
        name,
        oversamplers,
        classifiers,
        scoring=None,
        n_splits=5,
        n_runs=2,
        random_state=None,
        n_jobs=-1,
        verbose=0,
    ):
        self.name = name
        self.oversamplers = oversamplers
        self.classifiers = classifiers
        self.scoring = scoring
        self.n_splits = n_splits
        self.n_runs = n_runs
        self.random_state = random_state
        self.n_jobs = n_jobs
        self.verbose = verbose

    def _initialize(self):
        """Initialize experiment's parameters."""

        # Check oversamplers and classifiers
        self.estimators_, self.param_grids_ = check_oversamplers_classifiers(
            self.oversamplers, self.classifiers, self.random_state, self.n_runs
        )

        # Create model search cv
        self.mscv_ = ModelSearchCV(
            self.estimators_,
            self.param_grids_,
            scoring=self.scoring,
            refit=False,
            cv=StratifiedKFold(
                n_splits=self.n_splits, shuffle=True, random_state=self.random_state
            ),
            return_train_score=False,
            n_jobs=self.n_jobs,
            verbose=self.verbose,
        )

        # Extract oversamplers and classifiers names
        self.oversamplers_names_, *_ = zip(*self.oversamplers)
        self.classifiers_names_, *_ = zip(*self.classifiers)

        # Extract scoring columns
        if isinstance(self.scoring, list):
            self.scoring_cols_ = self.scoring
        elif isinstance(self.scoring, str):
            self.scoring_cols_ = [self.scoring]
        else:
            self.scoring_cols_ = (
                ['accuracy']
                if self.mscv_.estimator._estimator_type == 'classifier'
                else ['r2']
            )

    def _calculate_results(self, results):
        """"Calculate aggregated results across runs."""
        results['params'] = results['params'].apply(
            lambda param_grid: str(
                {
                    param: val
                    for param, val in param_grid.items()
                    if 'random_state' not in param
                }
            )
        )
        scoring_mapping = {
            scorer_name: [np.mean, np.std] for scorer_name in self.scoring_cols_
        }
        self.results_ = results.groupby(GROUP_KEYS).agg(scoring_mapping)
        return self

    def _calculate_optimal_results(self):
        """"Calculate optimal results across hyperparameters for any
        combination of datasets, overamplers, classifiers and metrics."""

        # Select mean scores
        optimal = self.results_[
            [(score, 'mean') for score in self.scoring_cols_]
        ].reset_index()

        # Flatten columns
        optimal.columns = optimal.columns.get_level_values(0)

        # Calculate maximum score per gorup key
        agg_measures = {score: max for score in self.scoring_cols_}
        optimal = optimal.groupby(GROUP_KEYS[:-1], as_index=False).agg(agg_measures)

        # Format as long table
        optimal = optimal.melt(
            id_vars=GROUP_KEYS[:-1],
            value_vars=self.scoring_cols_,
            var_name='Metric',
            value_name='Score',
        )

        # Cast to categorical columns
        optimal_cols = GROUP_KEYS[:-1] + ['Metric']
        names = [
            self.datasets_names_,
            self.oversamplers_names_,
            self.classifiers_names_,
            self.scoring_cols_,
        ]
        for col, name in zip(optimal_cols, names):
            optimal[col] = pd.Categorical(optimal[col], name)

        # Sort values
        self.optimal_ = optimal.sort_values(optimal_cols).reset_index(drop=True)

        return self

    def _calculate_wide_optimal_results(self):
        """Calculate optimal results in wide format."""

        # Format as wide table
        wide_optimal = self.optimal_.pivot_table(
            index=['Dataset', 'Classifier', 'Metric'],
            columns=['Oversampler'],
            values='Score',
        )
        wide_optimal.columns = wide_optimal.columns.tolist()
        wide_optimal.reset_index(inplace=True)

        # Cast column
        wide_optimal['Metric'] = pd.Categorical(
            wide_optimal['Metric'],
            categories=self.scoring if isinstance(self.scoring, list) else None,
        )

        self.wide_optimal_ = wide_optimal

        return self

    def fit(self, datasets):
        """Fit experiment."""

        self.datasets_names_, _ = zip(*datasets)
        self._initialize()

        # Define empty results
        results = []

        # Populate results table
        datasets = check_datasets(datasets)
        for dataset_name, (X, y) in tqdm(datasets, desc='Datasets'):

            # Fit model search
            self.mscv_.fit(X, y)

            # Get results
            result = pd.DataFrame(self.mscv_.cv_results_)
            scoring_cols = [col for col in result.columns if 'mean_test' in col]
            result.rename(
                columns=dict(zip(scoring_cols, self.scoring_cols_)), inplace=True
            )
            result = result.loc[:, ['models', 'params'] + self.scoring_cols_]

            # Append dataset name column
            result = result.assign(Dataset=dataset_name)

            # Append result
            results.append(result)

        # Split models
        results = pd.concat(results, ignore_index=True)
        results.loc[:, 'models'] = results.loc[:, 'models'].apply(
            lambda model: model.split('|')
        )
        results[['Oversampler', 'Classifier']] = pd.DataFrame(
            results.models.values.tolist()
        )

        # Drop models columns
        results.drop(columns='models', inplace=True)

        # Calculate results in various formats
        self._calculate_results(
            results
        )._calculate_optimal_results()._calculate_wide_optimal_results()

        return self

    def dump(self, path='.'):
        """Dump the experiment object."""
        with open(join(path, f'{self.name}.pkl'), 'wb') as file:
            dump(self, file)
