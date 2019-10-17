from sklearn.metrics import (
    explained_variance_score,
    mean_absolute_error,
    mean_squared_error,
    mean_squared_log_error,
    median_absolute_error,
    r2_score,
)


# To align with PyMC3 and BayesOpt, we want to always maximize a metric.
# Hence if the metric is an error (like MSE), ensure it is negative.
# As scipy can only minimise, we will need to make the error terms positive again (
# i.e. take a double negative) before passing them to scipy. Hence our backend is a
# bit convoluted, but the user experience is clean.


def neg(f):
    def _wrapper(y, y_pred, sample_weight=None):
        return -f(y, y_pred, sample_weight=sample_weight)

    return _wrapper


def _med_abs_err(y_true, y_pred, sample_weight=None):
    return median_absolute_error(y_true, y_pred)


LARGE_NEG_ERR = -1e9

metrics = {
    "r_squared": r2_score,
    "explained_variance": explained_variance_score,
    "neg_mean_sq_err": neg(mean_squared_error),
    "neg_mean_abs_err": neg(mean_absolute_error),
    "neg_mean_sq_log_err": neg(mean_squared_log_error),
    "neg_median_abs_err": neg(_med_abs_err),
}


def get_metric(metric):
    """Get the function for the metric used to determine goodness of fit

    The returned function returns a single float goodness of fit value from two input
    vectors.

    Notes
    -----
    - More information about the available metrics is available from
        https://scikit-learn.org/stable/modules/model_evaluation.html#regression-metrics

    Parameters
    ----------
    metric :
        Case insensitive string containing the selected metric. Options include

        - r_squared: R^2 value
        - explained_variance: Measure to which the modelled data accounts for the variation
        - neg_mean_sq_err: Mean square error (MSE)
        - neg_mean_abs_err: Mean absolute error (MAE)
        - neg_mean_sq_log_err: Mean square log error (MSLE)
        - neg_median_abs_err: Median absolute error (MedAE)

        The signature for the metric functions are ``(y, y_pred, sample_weight=None) -> float`` where y is the

        - y_true : array-like of shape = (n_samples)
            Ground truth (correct) target values.
        - y_pred : array-like of shape = (n_samples)
            Estimated target values.
        - sample_weight : array-like of shape = (n_samples), optional
            Sample weights.

    Returns
    -------
    function
        A function taking the sample time series and the expected time series as arguments. The functions all return a single float.

    """
    try:
        return metrics[metric]
    except KeyError:
        raise ValueError("No metric named: {}".format(metric))
