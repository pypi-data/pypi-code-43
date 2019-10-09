import numpy as np
import torch

__all__ = ['safe_div', 'Metric', 'MetricMean', 'MetricAccuracy',
           'Metric', 'MetricConfusionMatrix', 'MetricAUC', 'MetricPearsonCorrelation',
           'MetricSpearmanCorrelation', 'MetricMAE', 'MetricMSE', 'MetricComoment', 'MetricVar', 'MetricR2']


def safe_div(x, y):
    return torch.where(y != 0, x / y, torch.zeros_like(x))


class Metric:
    def __init__(self, name='metric'):
        self._name = name

    @property
    def name(self):
        return self._name

    def update(self):
        raise NotImplementedError

    @property
    def result(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError


class MetricMean(Metric):
    def __init__(self, device=None, name='mean'):
        super(MetricMean, self).__init__(name=name)
        self.total = torch.zeros([], dtype=torch.float32, device=device)
        self.count = torch.zeros([], dtype=torch.float32, device=device)

    def update(self, values, weights=None):
        values = torch.squeeze(values).type(torch.float32)
        if weights is None:
            num_values = values.numel()
        else:
            weights = torch.squeeze(weights).type(torch.float32)
            values = values * weights
            num_values = torch.sum(weights)
        self.total += torch.sum(values)
        self.count += num_values

    @property
    def result(self):
        if self.count == 0:
            raise ValueError('Count == 0')
        return self.total / self.count

    def reset(self):
        self.total *= 0
        self.count *= 0


class MetricAccuracy(Metric):
    '''Accuracy for multi-class classification
    labels: [N, d1, d2...];
    predictions: [N, d1, d2..., C]
    '''

    def __init__(self, device=None, name='accuracy'):
        super(MetricAccuracy, self).__init__(name=name)
        self.metric_mean = MetricMean(device=device)

    def update(self, labels, predictions, weights=None):
        labels = torch.flatten(labels)
        predictions = torch.flatten(predictions, 0, -2).argmax(
            dim=-1).type(labels.dtype)
        if weights is not None:
            weights = torch.flatten(weights)
        is_correct = torch.eq(labels, predictions).type(torch.float32)
        self.metric_mean.update(is_correct, weights)

    @property
    def result(self):
        return self.metric_mean.result

    def reset(self):
        return self.metric_mean.reset()


class MetricConfusionMatrix(Metric):
    '''Computes true_positives, false_negatives, true_negatives, false_positives.

     This function creates up to four local variables, `true_positives`, `true_negatives`, `false_positives` and `false_negatives`.
     `true_positive[i]` is defined as the total weight of values in `predictions` above `thresholds[i]` whose corresponding entry in `labels` is `True`.
     `false_negatives[i]` is defined as the total weight of values in `predictions` at most `thresholds[i]` whose corresponding entry in `labels` is `True`.
     `true_negatives[i]` is defined as the total weight of values in `predictions` at most `thresholds[i]` whose corresponding entry in `labels` is `False`.
     `false_positives[i]` is defined as the total weight of values in `predictions` above `thresholds[i]` whose corresponding entry in `labels` is `False`.
    '''

    def __init__(self, num_thresholds, device=None, name='confusion_matrix'):
        super(MetricConfusionMatrix, self).__init__(name=name)
        self.num_thresholds = num_thresholds
        kepsilon = 1e-7
        thresholds = [0.0 - kepsilon] + [(i+1) * 1.0 / (num_thresholds - 1)
                                         for i in range(num_thresholds - 2)] + [1.0 + kepsilon]
        self.thresholds = torch.as_tensor(thresholds, dtype=torch.float32, device=device)
        self.tp = torch.zeros([num_thresholds], dtype=torch.float32, device=device)
        self.fn = torch.zeros([num_thresholds], dtype=torch.float32, device=device)
        self.tn = torch.zeros([num_thresholds], dtype=torch.float32, device=device)
        self.fp = torch.zeros([num_thresholds], dtype=torch.float32, device=device)
        self.confusion_matrix = {'tp': self.tp,
                                 'fn': self.fn, 'tn': self.tn, 'fp': self.fp}

    def update(self, labels, predictions, weights=None):
        predictions = torch.squeeze(predictions).type(torch.float32)
        labels = torch.squeeze(labels).type(torch.bool)
        if weights is not None:
            weights_tiled = torch.reshape(
                weights, [1, -1]).type(torch.float32).repeat([self.num_thresholds, 1])
        else:
            weights_tiled = None
        predictions_2d = torch.reshape(predictions, [-1, 1])
        labels_2d = torch.reshape(labels, [1, -1])
        num_predictions = predictions.numel()
        thresh_tiled = self.thresholds.unsqueeze(
            dim=1).repeat([1, num_predictions])

        # Tile the predictions after thresholding them across different thresholds
        pred_is_pos = predictions_2d.T.repeat(
            [self.num_thresholds, 1]) > thresh_tiled
        pred_is_neg = ~pred_is_pos

        # Tile labels by number of thresholds
        label_is_pos = labels_2d.repeat([self.num_thresholds, 1])
        label_is_neg = ~label_is_pos

        is_true_positive = (label_is_pos & pred_is_pos).type(torch.float32)
        is_false_negative = (label_is_pos & pred_is_neg).type(torch.float32)
        is_true_negative = (label_is_neg & pred_is_neg).type(torch.float32)
        is_false_positive = (label_is_neg & pred_is_pos).type(torch.float32)
        if weights_tiled is not None:
            is_true_positive *= weights_tiled
            is_false_negative *= weights_tiled
            is_true_negative *= weights_tiled
            is_false_positive *= weights_tiled
        self.tp += torch.sum(is_true_positive, dim=1)
        self.fn += torch.sum(is_false_negative, dim=1)
        self.tn += torch.sum(is_true_negative, dim=1)
        self.fp += torch.sum(is_false_positive, dim=1)

    @property
    def result(self):
        return self.confusion_matrix

    def reset(self):
        self.tp *= 0
        self.fn *= 0
        self.tn *= 0
        self.fp *= 0


class MetricAUC(Metric):
    '''Computes the approximate AUC via a Riemann sum.
    To discretize the AUC curve, a linearly spaced set of thresholds is used to compute pairs of recall and precision values.
    The area under the ROC-curve is therefore computed using the height of the recall values by the false positive rate, while the area under the PR-curve is the computed using the height of the precision values by the recall.

    This value is ultimately returned as `auc`, an idempotent operation that computes the area under a discretized curve of precision versus recall values (computed using the aforementioned variables).
    The `num_thresholds` variable controls the degree of discretization with larger numbers of thresholds more closely approximating the true AUC.
    The quality of the approximation may vary dramatically depending on `num_thresholds`.

    For best results, `predictions` should be distributed approximately uniformly in the range [0, 1] and not peaked around 0 or 1.
    The quality of the AUC approximation may be poor if this is not the case.

    If `weights` is `None`, weights default to 1. Use weights of 0 to mask values.

    curve: Specifies the name of the curve to be computed, 'ROC' [default] or 'PR' for the Precision-Recall-curve.
    '''

    def __init__(self, curve='ROC', normalized=False, from_softmax=True, num_thresholds=200, device=None, name='auc'):
        super(MetricAUC, self).__init__(name=name)
        assert curve in ('ROC', 'PR'), 'curve must be either ROC or PR!'
        self.curve = curve
        self.normalized = normalized
        self.from_softmax = from_softmax
        self.num_thresholds = num_thresholds
        self.metric_confusion_matrix = MetricConfusionMatrix(
            num_thresholds, device=device)

    def update(self, labels, predictions, weights=None):
        if not self.normalized:
            self.from_softmax = True
            predictions = torch.softmax(predictions, dim=1)
        if self.from_softmax:
            predictions = predictions[:, 1]
        else:
            predictions = predictions
        self.metric_confusion_matrix.update(
            labels, predictions, weights=weights)

    @classmethod
    def interpolate_pr_auc(cls, tp, fp, fn, num_thresholds):

        dtp = tp[:num_thresholds-1] - tp[1:]
        p = tp + fp
        prec_slope = safe_div(dtp, p[:num_thresholds-1]-p[1:])
        intercept = tp[1:] - prec_slope * p[1:]
        safe_p_ratio = torch.where((p[:num_thresholds-1] > 0) & (
            p[1:] > 0), safe_div(p[:num_thresholds-1], p[1:]), torch.ones_like(p[1:]))
        pr_auc = torch.sum(safe_div(prec_slope * (dtp + intercept *
                                                  torch.log(safe_p_ratio)), tp[1:]+fn[1:]))
        return pr_auc

    @classmethod
    def compute_auc(cls, tp, fn, tn, fp, num_thresholds, curve):
        epsilon = 1e-6
        if curve == 'PR':
            return cls.interpolate_pr_auc(tp, fp, fn, num_thresholds)
        rec = (tp + epsilon) / (tp + fn + epsilon)
        fp_rate = fp / (fp + tn + epsilon)
        x = fp_rate
        y = rec
        return torch.sum((x[:num_thresholds-1] - x[1:]) * (y[:num_thresholds-1] + y[1:]) / 2)

    @property
    def result(self):
        confusion_matrix = self.metric_confusion_matrix.result
        auc = self.compute_auc(confusion_matrix['tp'], confusion_matrix['fn'],
                               confusion_matrix['tn'], confusion_matrix['fp'], self.num_thresholds, self.curve)
        return auc

    def reset(self):
        self.metric_confusion_matrix.reset()


class MetricSpearmanCorrelation(Metric):
    def __init__(self, rank_method='average', device=None, name='spearman_corr'):
        super(MetricSpearmanCorrelation, self).__init__(name=name)
        self.rank_method = rank_method
        self.vx = torch.zeros([1], dtype=torch.float32, device=device)
        self.vy = torch.zeros([1], dtype=torch.float32, device=device)
        self.vw = torch.ones([1], dtype=torch.float32, device=device)

    def update(self, x, y, weights=None):
        x = torch.squeeze(x).type(torch.float32)
        y = torch.squeeze(y).type(torch.float32)
        if weights is not None:
            weights = torch.squeeze(weights).type(torch.float32)
        else:
            weights = torch.ones_like(x)

        self.vx = torch.cat([self.vx, x], dim=0)
        self.vy = torch.cat([self.vy, y], dim=0)
        self.vw = torch.cat([self.vw, weights], dim=0)

    @classmethod
    def weighted_pearson(cls, x, y, w):
        xd = x - torch.sum(x * w) / torch.sum(w)
        yd = y - torch.sum(y * w) / torch.sum(w)
        corr = torch.sum(w * yd * xd) / torch.sum(w) / torch.sqrt(
            torch.sum(w * yd ** 2) * torch.sum(w * xd ** 2) / (torch.sum(w) ** 2))
        return corr

    @classmethod
    def rankdata(cls, a, method):
        arr = a.reshape([-1])
        _, sorter = torch.topk(-arr, arr.numel())
        inv = torch.argsort(sorter)
        if method == 'ordinal':
            res = inv + 1
        else:
            arr = torch.gather(arr, 0, sorter)
            obs = (arr[1:] != arr[:-1]).type(torch.long)
            obs = torch.cat([torch.ones_like(obs)[:1], obs], dim=0)
            dense = torch.gather(torch.cumsum(obs, dim=0), 0, inv)
            if method == 'dense':
                res = dense
            else:
                count = torch.cat(
                    [torch.nonzero(obs)[:, 0], torch.ones_like(obs)[:1] * obs.numel()])
                if method == 'max':
                    res = torch.gather(count, 0, dense)
                elif method == 'min':
                    res = torch.gather(count, 0, dense - 1) + 1
                elif method == 'average':
                    res = (torch.gather(count, 0, dense) + torch.gather(count,
                                                                        0, dense - 1) + 1).type(torch.float32) * 0.5
                else:
                    raise ValueError('Invalid method!')
        return res.type(torch.float32)

    @property
    def result(self):
        x = self.vx[1:]
        y = self.vy[1:]
        w = self.vw[1:]
        rx = self.rankdata(x, method=self.rank_method)
        ry = self.rankdata(y, method=self.rank_method)
        rs = self.weighted_pearson(rx, ry, w)
        return rs

    def reset(self):
        self.vx = self.vx[:1]
        self.vy = self.vy[:1]
        self.vw = self.vw[:1]


class MetricMAE(Metric):
    '''Mean absolute error
    '''

    def __init__(self, device=None, name='mae'):
        super(MetricMAE, self).__init__(name=name)
        self.metric_mean = MetricMean(device=device)

    def update(self, labels, predictions, weights=None):
        labels = torch.squeeze(labels).type(torch.float32)
        predictions = torch.squeeze(predictions).type(torch.float32)
        absolute_errors = torch.abs(predictions - labels)
        self.metric_mean.update(absolute_errors, weights)

    @property
    def result(self):
        return self.metric_mean.result

    def reset(self):
        return self.metric_mean.reset()


class MetricMSE(Metric):
    '''Mean squared error
    '''

    def __init__(self, device=None, name='mse'):
        super(MetricMSE, self).__init__(name=name)
        self.metric_mean = MetricMean(device=device)

    def update(self, labels, predictions, weights=None):
        labels = torch.squeeze(labels).type(torch.float32)
        predictions = torch.squeeze(predictions).type(torch.float32)
        squared_errors = (labels - predictions) ** 2
        self.metric_mean.update(squared_errors, weights)

    @property
    def result(self):
        return self.metric_mean.result

    def reset(self):
        self.metric_mean.reset()


class MetricComoment(Metric):
    '''Comoment for covariance calculation.
      The algorithm used for this online computation is described in
      https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance.
      Specifically, the formula used to combine two sample comoments is
      `C_AB = C_A + C_B + (E[x_A] - E[x_B]) * (E[y_A] - E[y_B]) * n_A * n_B / n_AB`
      The comoment for a single batch of data is simply
      `sum((x - E[x]) * (y - E[y]))`, optionally weighted.

    '''

    def __init__(self, device=None, name='comoment'):
        super(MetricComoment, self).__init__(name=name)
        self.count = torch.zeros([], dtype=torch.float32, device=device)
        self.mean_x = torch.zeros([], dtype=torch.float32, device=device)
        self.mean_y = torch.zeros([], dtype=torch.float32, device=device)
        self.comoment = torch.zeros([], dtype=torch.float32, device=device)

    def update(self, x, y, weights=None):
        x = torch.squeeze(x).type(torch.float32)
        y = torch.squeeze(y).type(torch.float32)
        if weights is not None:
            weights = torch.squeeze(weights).type(torch.float32)
        else:
            weights = torch.ones_like(x)
        n_b = torch.sum(weights)
        weighted_x = x * weights
        weighted_y = y * weights
        self.count += n_b
        n_a = self.count - n_b

        mean_x_b = torch.sum(weighted_x) / n_b
        delta_x_b = (mean_x_b - self.mean_x) * n_b / self.count
        self.mean_x += delta_x_b
        mean_x_a = self.mean_x - delta_x_b

        mean_y_b = torch.sum(weighted_y) / n_b
        delta_y_b = (mean_y_b - self.mean_y) * n_b / self.count
        self.mean_y += delta_y_b
        mean_y_a = self.mean_y - delta_y_b

        weighted_coresiduals = (x - mean_x_b) * (y - mean_y_b) * weights
        c_b = torch.sum(weighted_coresiduals)
        delta_comoment = c_b + (mean_x_b - mean_x_a) * \
            (mean_y_b - mean_y_a) * n_a * n_b / self.count
        self.comoment += delta_comoment

    @property
    def result(self):
        return self.comoment * 1.0

    def reset(self):
        self.count *= 0
        self.mean_x *= 0
        self.mean_y *= 0
        self.comoment *= 0


class MetricVar(Metric):
    def __init__(self, unbiasing=True, device=None, name='var'):
        super(MetricVar, self).__init__(name=name)
        self.unbiasing = unbiasing
        self.metric_comoment = MetricComoment(device)

    def update(self, x, y, weights=None):
        self.metric_comoment.update(x, y, weights)

    @property
    def result(self):
        if self.unbiasing:
            if self.metric_comoment.count.type(torch.int64) == 1:
                raise ValueError(
                    'Count should not be 1 for unbiasing variance')
            return self.metric_comoment.comoment / (self.metric_comoment.count - 1)
        else:
            return self.metric_comoment.comoment / self.metric_comoment.count

    def reset(self):
        self.metric_comoment.reset()


class MetricPearsonCorrelation(Metric):
    def __init__(self, device=None, name='pearson_corr'):
        super(MetricPearsonCorrelation, self).__init__(name=name)
        self.metric_var_x = MetricVar(unbiasing=False, device=device)
        self.metric_var_y = MetricVar(unbiasing=False, device=device)
        self.metric_covar_xy = MetricVar(unbiasing=False, device=device)

    def update(self, x, y, weights=None):
        self.metric_var_x.update(x, x, weights)
        self.metric_var_y.update(y, y, weights)
        self.metric_covar_xy.update(x, y, weights)

    @property
    def result(self):
        covar_xy = self.metric_covar_xy.result
        var_x = self.metric_var_x.result
        var_y = self.metric_var_y.result
        return covar_xy / torch.sqrt(var_x * var_y)

    def reset(self):
        self.metric_covar_xy.reset()
        self.metric_var_x.reset()
        self.metric_var_y.reset()


class MetricR2(Metric):
    def __init__(self, device=None, name='r2'):
        super(MetricR2, self).__init__(name=name)
        self.metric_mse = MetricMSE(device)
        self.metric_var = MetricVar(unbiasing=False, device=device)

    def update(self, labels, predictions, weights=None):
        self.metric_mse.update(labels, predictions, weights)
        self.metric_var.update(labels, labels, weights)

    @property
    def result(self):
        r2 = 1.0 - self.metric_mse.result / self.metric_var.result
        return r2

    def reset(self):
        self.metric_mse.reset()
        self.metric_var.reset()
