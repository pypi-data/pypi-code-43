from random_survival_forest import RandomSurvivalForest
from lifelines import CoxPHFitter, KaplanMeierFitter
from .feature_creator import drop_correlated_features
from lifelines.metrics import concordance_index


def c_index(prediction, labels):
    """
    From the lifelines documentation: Calculates the concordance index (C-index) between two series of event times.
    The first is the real survival times from the experimental data, and the other is the predicted survival times
    from a model of some kind.
    The c-index is the average of how often a model says X is greater than Y when, in the observed data, X is indeed
    greater than Y. The c-index also handles how to handle censored values (obviously, if Y is censored,
    it’s hard to know if X is truly greater than Y).
    :param prediction: The predicted scores
    :param labels: The two-dimensional survival label matrix
    :return: c-index - a value between 0 and 1.
    """
    return concordance_index(labels["donor_survival_time"], prediction, labels["donor_vital_status"])


def kaplan_meier(labels):
    """
    Returns a Kaplan-Meier model fitted by the survival labels.
    :param labels: Survival labels
    :return: Fitted Kaplan-Meier model
    """
    kmf = KaplanMeierFitter()
    kmf.fit(labels['donor_survival_time'], labels['donor_vital_status'])

    return kmf


def cox_proportional_hazard(features, labels, penalizer=0, corr=0.95, drop_features=None):
    """
    Returns a fitted CoxPH regression model.
    :param features: Feature matrix
    :param labels: Survival labels
    :param penalizer: From the lifelines documentation: Attach an L2 penalizer to the size of the coefficients during
        regression. This improves stability of the estimates and controls for high correlation between covariates.
        For example, this shrinks the absolute value of :math:`\beta_i`.
        The penalty is :math:`\frac{1}{2} \text{penalizer} ||\beta||^2`
    :param corr: Correlation threshold. Remove features with higher correlation than corr.
    :param drop_features: List of features that should be dropped.
    :return: Fitted CoxPHFitter model
    """
    if drop_features is not None:
        features = features.drop(drop_features, axis=1)
    features = drop_correlated_features(features, corr)
    features.loc[:, "donor_survival_time"] = labels["donor_survival_time"]
    features.loc[:, "donor_vital_status"] = labels["donor_vital_status"]
    cph = CoxPHFitter(penalizer=penalizer)
    cph.fit(features, 'donor_survival_time', 'donor_vital_status')

    return cph


def random_survival_forest(features, labels, timeline=range(0, 10, 1), n_estimators=100,
                                      n_jobs=-1,  min_leaf=3, unique_deaths=3, random_state=None):
    """
    Returns a fitted Random Survival Forest Model.
    :param features: Feature matrix
    :param labels: Survival labels
    :param timeline: Timeline for prediction, e.g. range(0, 10, 1)
    :param n_estimators: Number of trees in the survival forest
    :param n_jobs: Number of cores to use for parallelization
    :param min_leaf: Minimum number of samples in a leaf node
    :param unique_deaths: Minimum number of unique deaths in a leaf node
    :param random_state: Random state for reproducible results.
    :return: Fitted RandomSurvivalForest model.
    """
    rsf = RandomSurvivalForest(n_estimators=n_estimators, timeline=timeline, n_jobs=n_jobs, min_leaf=min_leaf,
                               unique_deaths=unique_deaths, random_state=random_state)
    rsf.fit(features, labels)
    return rsf
