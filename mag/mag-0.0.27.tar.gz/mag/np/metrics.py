import numpy as np
CONFUSION_METRIC_NAMES = [
    'True Positive Rate', 'True Negative Rate', 'Positive Predicitve Value',
    'Negative Predicitive Value', 'False Negative Rate', 'False Positive Rate',
    'False Discovery Rate', 'False Omission Rate', 'Threat Score', 'Accuracy',
    'F1 Score', 'Matthew\'s Correlation Coefficient', 'Informedness', 'Markedness'
]

def confusion_indicator_matrices(y_pred:list, y_true:list, threshold:float=0.5):
    '''
    Arguments:
        y_pred (list): the output matrix.
        y_true (list): the target matrix.
        threshold (float): values above `threshold` are `1`, rest are `0` for
            both `output` and `target`.
    Returns:
        tp (list): true postitives indicator matrix
        tn (list): true negatives indicator matrix
        fp (list): false positives indicator matrix
        fn (list): false negatives indicator matrix
    '''
    label_is_pos = np.greater(y_true, threshold)
    preds_is_pos = np.greater(y_pred, threshold)
    label_is_neg = np.logical_not(label_is_pos)
    preds_is_neg = np.logical_not(preds_is_pos)

    tp = np.logical_and(preds_is_pos, label_is_pos)
    tn = np.logical_and(preds_is_neg, label_is_neg)
    fp = np.logical_and(preds_is_pos, label_is_neg)
    fn = np.logical_and(preds_is_neg, label_is_pos)
    return tp, tn, fp, fn

def label_based_confusion_metrics(tp, tn, fp, fn):
    '''
    Notes:
        - expected arguments are output of `confusion_indicator_matrices`.

    Arguments:
        tp (list): true postitives indicator matrix
        tn (list): true negatives indicator matrix
        fp (list): false positives indicator matrix
        fn (list): false negatives indicator matrix

    Returns:
        label_confusion_metrics (np.ndarray): matrix with shape `[4, q]`, where
            `q` is the number of labels. The first 4 dimensions are the tp, tn,
            fp, and fn respectively.
    '''
    return np.array(list(map(lambda m: np.sum(m, axis=0), [tp, tn, fp, fn]))).T

def label_cardinality(labels):
    '''
    Arguments:
        labels (list): the 2d matrix of labels
    Returns:
        cardinality (float): average number of labels per example
    '''
    n_examples, n_labels = labels.shape
    return np.sum(labels) / n_examples

def label_density(labels, cardinality=None):
    '''
    Arguments:
        labels (list): the 2d matrix of labels
        cardinality (float): the `label_cardinality`. By default `None`. If
            `None` calculates the `label_cardinality`.
    Returns:
        density (float): normalized cardinality by possible number of labels
    '''
    n_examples, n_labels = labels.shape
    if cardinality is None:
        cardinality = label_cardinality(labels)
    return (1 / n_labels) * cardinality

def label_diversity(labels):
    '''
    Arguments:
        labels (list): the 2d matrix of labels
    Returns:
        diveristy (int): number of unique label sets that could occur
    '''
    n_examples, n_labels = labels.shape
    if n_examples > 10000:
        print('Calculating label diversity with {} examples.'.format(n_examples))
        print('This may take a while')

    return len(np.unique(labels, axis=0))

def proportional_label_diversity(labels, diversity=None):
    '''
    Arguments:
        labels (list): the 2d matrix of labels
        diveristy (int): The `label_diversity`. By default `None`. If `None`
            calculates the `label_diversity`.
    Returns:
        proportional_diversity (float): normalized diveristy by possible number
            examples
    '''
    n_examples, n_labels = labels.shape
    if diversity is None:
        diversity = label_diversity(labels)
    return (1 / n_examples) * diversity

DESCRIPTIVE_MULTI_LABEL_METRICS = {
    'label_cardinality': label_cardinality,
    'label_density': label_density,
    'label_diversity': label_diversity,
    'proportional_label_diversity': proportional_label_diversity
}
def descriptive_multi_label_metrics(
    y_true,
    threshold=0.5,
    metrics=list(DESCRIPTIVE_MULTI_LABEL_METRICS.keys())
):
    '''
    As defined in ["A review on Multi-Label Learning Algorithms"]
    (https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=6471714&tag=1).

    Arguments:
        y_true (list): the target matrix.
        threshold (float): masks `y_true` (in the case of soft labeling).
        metrics (list): list of which metrics to compute. Choices include:
            label_cardinality: average number of labels per example.
            label_density: normalized cardinality by possible number of
                labels.
            label_diversity: number of unique label sets.
            proportional_label_diversity: normalized diversity by number of
                examples.
    Returns:
        results (dict): dictionary containing only the corresponding specified
            metrics, with types:
                label_cardinality (float)
                label_density (float)
                label_diversity (int)
                proportional_label_diversity (float)
    '''
    label_is_pos = np.greater(y_true, threshold)

    results = {}
    for metric in metrics:
        fn = DESCRIPTIVE_MULTI_LABEL_METRICS[metric]
        if fn is None: continue

        # save recomputation when possible
        if metric == 'label_density':
            if 'label_cardinality' in results:
                res = fn(label_is_pos, results['label_cardinality'])
            else:
                res = fn(label_is_pos)

        elif metric == 'proportional_label_diversity':
            if 'label_diversity' in results:
                res = fn(label_is_pos, results['label_diversity'])
            else:
                res = fn(label_is_pos)

        else:
            res = fn(label_is_pos)

        results[metric] = res
    return results


def true_positive_rate(tp, tn, fp, fn):
    '''
    Aliases:
        - recall
        - sensitivity
    Arguments:
        tp (int): number of true positives
        tn (int): number of true negatives
        fp (int): number of false positives
        fn (int): number of false negatives
    Returns:
        (float): [0, 1]
    '''

    return tp / (tp + fn)
recall = true_positive_rate
sensitivity = true_positive_rate

def true_negative_rate(tp, tn, fp, fn):
    '''
    Aliases:
        - specificity
    Arguments:
        tp (int): number of true positives
        tn (int): number of true negatives
        fp (int): number of false positives
        fn (int): number of false negatives
    Returns:
        (float): [0, 1]
    '''
    return tn / (tn + fp)
specificity = true_negative_rate

def positive_predictive_value(tp, tn, fp, fn):
    '''
    Aliases:
        - precision
    Arguments:
        tp (int): number of true positives
        tn (int): number of true negatives
        fp (int): number of false positives
        fn (int): number of false negatives
    Returns:
        (float): [0, 1]
    '''

    return tp / (tp + fp)
precision = positive_predictive_value

def negative_predictive_value(tp, tn, fp, fn):
    '''
    Arguments:
        tp (int): number of true positives
        tn (int): number of true negatives
        fp (int): number of false positives
        fn (int): number of false negatives
    Returns:
        (float): [0, 1]
    '''
    return tn / (tn + fn)

def false_negative_rate(tp, tn, fp, fn):
    '''
    Arguments:
        tp (int): number of true positives
        tn (int): number of true negatives
        fp (int): number of false positives
        fn (int): number of false negatives
    Returns:
        (float): [0, 1]
    '''
    return fn / (fn + tp)

def false_positive_rate(tp, tn, fp, fn):
    '''
    Arguments:
        tp (int): number of true positives
        tn (int): number of true negatives
        fp (int): number of false positives
        fn (int): number of false negatives
    Returns:
        (float): [0, 1]
    '''
    return fp / (fp + tn)

def false_discovery_rate(tp, tn, fp, fn):
    '''
    Arguments:
        tp (int): number of true positives
        tn (int): number of true negatives
        fp (int): number of false positives
        fn (int): number of false negatives
    Returns:
        (float): [0, 1]
    '''
    return fp / (fp + tp)

def false_omission_rate(tp, tn, fp, fn):
    '''
    Arguments:
        tp (int): number of true positives
        tn (int): number of true negatives
        fp (int): number of false positives
        fn (int): number of false negatives
    Returns:
        (float): [0, 1]
    '''
    return fn / (fn + tn)

def threat_score(tp, tn, fp, fn):
    '''
    Arguments:
        tp (int): number of true positives
        tn (int): number of true negatives
        fp (int): number of false positives
        fn (int): number of false negatives
    Returns:
        (float): [0, 1]
    '''
    return tp / (tp + fn + fp)

def accuracy(tp, tn, fp, fn):
    '''
    Arguments:
        tp (int): number of true positives
        tn (int): number of true negatives
        fp (int): number of false positives
        fn (int): number of false negatives
    Returns:
        (float): [0, 1]
    '''
    return (tp + tn) / (tp + tn + fp + fn)

def f1_score(tp, tn, fp, fn):
    '''
    Arguments:
        tp (int): number of true positives
        tn (int): number of true negatives
        fp (int): number of false positives
        fn (int): number of false negatives
    Returns:
        (float): [0, 1]
    '''
    return (2 * tp) / (2 * tp + fp + fn)

def matthews_correlation_coefficient(tp, tn, fp, fn):
    '''
    Arguments:
        tp (int): number of true positives
        tn (int): number of true negatives
        fp (int): number of false positives
        fn (int): number of false negatives
    Returns:
        (float): [0, 1]
    '''
    denominator = np.sqrt((tp + fp)*(tp + fn)*(tn + fp)*(tn + fn))
    return (tp * tn - fp * fn) / denominator

def bookmaker_informedness(tp, tn, fp, fn):
    '''
    Arguments:
        tp (int): number of true positives
        tn (int): number of true negatives
        fp (int): number of false positives
        fn (int): number of false negatives
    Returns:
        (float): [0, 1]
    '''
    sensitivity = true_positive_rate(tp, tn, fp, fn)
    specificity = true_negative_rate(tp, tn, fp, fn)
    return sensitivity + specificity - 1

def markedness(tp, tn, fp, fn):
    '''
    Arguments:
        tp (int): number of true positives
        tn (int): number of true negatives
        fp (int): number of false positives
        fn (int): number of false negatives
    Returns:
        (float): [0, 1]
    '''
    precision = positive_predictive_value(tp, tn, fp, fn)
    npv = negative_predictive_value(tp, tn, fp, fn)
    return precision + npv - 1

def micro_average_multi_label_metric(fn, lbcm:list):
    '''
    Arguments:
        fn (function): one of the `derived_confusion_metrics`, or a custom
            metric function with arguments signature `(tp, tn, fp, fn)`.
        lbcm (np.ndarray): The output of the function
            `label_based_confusion_metrics` or a matrix of shape `(4, q)`, where
            `q` is the number of label classes.
    Returns:
        result (float): the evaluated metric
    '''
    # sum over all label classes the [tp, tn, fn, fp]
    confusion_metrics = np.sum(lbcm, axis=0)
    try:
        result = fn(*confusion_metrics)
    except ZeroDivisionError:
        msg = (
            'Attempted to calculate the micro-average of {}'.format(fn.__name__)+
            'However, the denominator was 0. Returning `None`'
        )
        print(msg)
        return None
    return result

def individual_multi_label_metric(fn, lbcm:list):
    '''
    Arguments:
        fn (function): one of the `derived_confusion_metrics`, or a custom
            metric function with arguments signature `(tp, tn, fp, fn)`.
        lbcm (np.ndarray): The output of the function
            `label_based_confusion_metrics` or a matrix of shape `(4, q)`, where
            `q` is the number of label classes.
    Returns:
        result (list): the evaluated metric, per label
    '''
    res_per_label = []
    for i, cm in enumerate(lbcm):
        try:
            res_per_label.append(fn(*cm))
        except ZeroDivisionError:
            msg = (
                'Attempted to calculate the {} for label {}'.format(fn.__name__, i)+
                'However, the denominator was 0. Returning `None`'
            )
            print(msg)
            res_per_label.append(None)
    return res_per_label
    # res_per_label = list(map(lambda args: fn(*args), lbcm))
    return res_per_label

def macro_average_multi_label_metric(fn, lbcm:list):
    '''
    Arguments:
        fn (function): one of the `derived_confusion_metrics`, or a custom
            metric function with arguments signature `(tp, tn, fp, fn)`.
        lbcm (np.ndarray): The output of the function
            `label_based_confusion_metrics` or a matrix of shape `(4, q)`, where
            `q` is the number of label classes.
    Returns:
        result (float): the evaluated metric
    '''
    # average metric by number of label classes
    div = 1 / lbcm.shape[0]
    try:
        res_per_label = individual_multi_label_metric(fn, lbcm)
        results = div * np.sum(res_per_label)
    except TypeError:
        nones = np.where(([1, None], None))[0].tolist()
        msg = (
            'Label classes at indicies {} are None.'.format(nones)+
            'Can not sum with unevaluateable metrics. Returning `None`.'
        )
        if nones:
            print(msg)
        return None
    return results

DERIVED_MULTI_LABEL_METRICS = {
    'true_positive_rate': true_positive_rate,
    'recall': true_positive_rate,
    'sensitivity': true_positive_rate,

    'true_negative_rate': true_negative_rate,
    'specificity': true_negative_rate,

    'positive_predictive_value': positive_predictive_value,
    'precision': positive_predictive_value,

    'negative_predictive_value': negative_predictive_value,
    'false_negative_rate': false_negative_rate,
    'false_positive_rate': false_positive_rate,
    'false_discovery_rate': false_discovery_rate,
    'false_omission_rate': false_omission_rate,
    'threat_score': threat_score,
    'accuracy': accuracy,
    'f1_score': f1_score,
    'matthews_correlation_coefficient': matthews_correlation_coefficient,
    'bookmaker_informedness': bookmaker_informedness,
    'markedness': markedness
}
def derived_multi_label_metrics(
    label_based_confusion_matrix:list,
    metrics=['accuracy', 'precision', 'recall', 'f1_score'],
    method='macro'
):
    '''
    Arguments:
        label_based_confusion_matrix (np.ndarray): a matrix with shape `(4, q)`
            where `q` is the number of label classes and the first dimension
            corresponds to tp, tn, fp, and fn respectively.

        metrics (list): list of metrics to calculate. By default,
            `['accuracy', 'precision', 'recall', 'f1_score']` Options include:
                true_positive_rate (alisases: recall, sensitivity)
                true_negative_rate (alias: specificity)
                positive_predictive_value (alias: precision)
                negative_predictive_value
                false_negative_rate
                false_positive_rate
                false_discovery_rate
                false_omission_rate
                threat_score
                accuracy
                f1_score
                matthews_correlation_coefficient
                sensitivity
                markedness

        method (str): how to apply the metrics specified, choices include:
            micro, macro and individual. Defaults to `macro`.

    Returns:
        results (dict): the specified metrics and corresponding value.
    '''
    if method not in {'macro', 'micro', 'individual'}:
        method = 'micro'

    if method == 'micro':
        eval_fn = micro_average_multi_label_metric
    elif method == 'individual':
        eval_fn = individual_multi_label_metric
    else:
        eval_fn = macro_average_multi_label_metric

    results = {}
    for metric in metrics:
        fn = DERIVED_MULTI_LABEL_METRICS[metric]
        if fn == None: continue
        try:
            res = eval_fn(fn, label_based_confusion_matrix)
        except Exception as e:
            print(e)
            res = None
        results['{}'.format(metric)] = res
    return results

def multi_label_metric_report(
    label_based_confusion_matrix:list,
    metrics:list=['accuracy', 'precision', 'recall', 'f1_score'],
    label_names:list=None,
    verbose:bool=False
):
    '''
    Arguments:
        label_based_confusion_matrix (np.ndarray): a matrix with shape `(4, q)`
            where `q` is the number of label classes and the first dimension
            corresponds to tp, tn, fp, and fn respectively.

        metrics (list): list of metrics to calculate. By default,
            `['accuracy', 'precision', 'recall', 'f1_score']` Options include:
                true_positive_rate (alisases: recall, sensitivity)
                true_negative_rate (alias: specificity)
                positive_predictive_value (alias: precision)
                negative_predictive_value
                false_negative_rate
                false_positive_rate
                false_discovery_rate
                false_omission_rate
                threat_score
                accuracy
                f1_score
                matthews_correlation_coefficient
                sensitivity
                markedness

        label_names (list): list of the label classes, used for printing the
            metrics report.

        verbose (bool): whether or not to print a formatted string of the
            results.

    Returns:
        results (dict): consists of three main keys, `macro`, `micro`, and
            `individual`, and their subdictionaries consiting of the specified
            metrics.
    '''
    macros = derived_multi_label_metrics(
        label_based_confusion_matrix,
        method='macro',
        metrics=metrics
    )

    micros = derived_multi_label_metrics(
        label_based_confusion_matrix,
        method='micro',
        metrics=metrics
    )

    indivs = derived_multi_label_metrics(
        label_based_confusion_matrix,
        method='individual',
        metrics=metrics
    )

    if label_names == None:
        names = ['Label {}'.format(i) for i in range(label_based_confusion_matrix.shape[0])]
    else:
        names = label_names

    outstring = 'Macros:\n------------------------------------------------\n'
    longest_metric_name = max(list(map(len, list(macros.keys()))))
    for k, v in macros.items():
        spaces = ' ' * (4 + longest_metric_name-len(k))
        outstring += '{}:{}{}\n'.format(k, spaces, np.round(v, 3))

    outstring += '\nMicros:\n------------------------------------------------\n'
    longest_metric_name = max(list(map(len, list(macros.keys()))))
    for k, v in micros.items():
        spaces = ' ' * (4 + longest_metric_name-len(k))
        outstring += '{}:{}{}\n'.format(k, spaces, np.round(v, 3))

    outstring += '\nPer Label:\n------------------------------------------------\n'


    longest_metric_name  = max(list(map(len, list(indivs.keys()))))
    longest_name = max(list(map(len, names)))
    for i, name in enumerate(names):
        outstring += '{}:\n'.format(name)
        for k, v in indivs.items():
            longest = (longest_metric_name+longest_name)
            spaces = ' ' * (4 + longest - len(k) - len(name))
            outstring += '\t{}:{}{}\n'.format(k, spaces, np.round(v[i], 3))

    if verbose:
        print(outstring)

    return {'macro': macros, 'micro': micros, 'individual': indivs}
