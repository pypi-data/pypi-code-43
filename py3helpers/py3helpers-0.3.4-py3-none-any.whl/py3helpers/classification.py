#!/usr/bin/env python
"""Classification output analysis functions and classes"""
########################################################################
# File: classification.py
#  executable: classification.py
#
# Author: Andrew Bailey
# History: 12/19/18 Created
########################################################################

import os
import pandas as pd
import numpy as np
import platform
import matplotlib as mpl

if os.environ.get('DISPLAY', '') == '':
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')
# if platform.system() == "Darwin":
#     mpl.use("macosx")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from sklearn.metrics import roc_curve, auc, confusion_matrix, average_precision_score, brier_score_loss, \
    precision_recall_curve
from sklearn.calibration import calibration_curve
from sklearn.utils import column_or_1d, assert_all_finite, check_consistent_length
from sklearn.utils.extmath import stable_cumsum
from inspect import signature
from scipy import interp
from py3helpers.utils import binary_search
from itertools import cycle


class ClassificationMetrics(object):

    def __init__(self, binary_labels, class_probabilities, class_ns=None, label_ids=None):
        """Initialize binary labels and class probabilities"""
        assert isinstance(binary_labels, pd.DataFrame), \
            "binary_labels must be a pandas dataframe: type {}".format(type(binary_labels))
        assert isinstance(class_probabilities, pd.DataFrame), \
            "class_probabilities must be a pandas dataframe: type {}".format(type(class_probabilities))

        self.fps = dict()
        self.tps = dict()
        self.fns = dict()
        self.tns = dict()

        self.fpr = dict()
        self.tpr = dict()
        self.fnr = dict()
        self.tnr = dict()
        self.ppv = dict()
        self.fdr = dict()
        self.for1 = dict()
        self.npv = dict()
        self.thresholds = dict()
        self.roc_auc = dict()
        self.average_precision = dict()
        self.sorted_ids = dict()

        self.total = 0
        self.class_totals = dict()
        if label_ids is not None:
            assert len(label_ids) == len(binary_labels), \
                "label_ids length must match the length of binary labels. " \
                "len(label_ids) = {}, len(binary_labels) = {}".format(len(label_ids), len(binary_labels))

        self.label_ids = label_ids
        self.binary_labels = binary_labels
        self.class_probabilities = class_probabilities
        assert len(self.binary_labels) > 1, "binary_labels need to be longer than 1: {}".format(self.binary_labels)
        assert len(self.class_probabilities) > 1, "class_probabilities need to be longer than 1: {}".format(
            self.class_probabilities)

        self.class_ns = class_ns
        self.n_classes = 0
        self._set_check_class_ns()
        self._calculate_fp_tp_rate()

    def _set_check_class_ns(self):
        """Check class names from input data and optional argument

        Note: if class_ns is not passed in then we will will throw error
        """
        if self.class_ns is None:
            tmp_class_ns = [str(x) for x in self.binary_labels.dtypes.index]
            tmp_class_ns_2 = [str(x) for x in self.class_probabilities.dtypes.index]
            assert tmp_class_ns == tmp_class_ns_2, \
                "binary_labels and class_probabilities must have same column names: " \
                "binary_labels - {}, class_probabilities - {}".format(tmp_class_ns, tmp_class_ns_2)
            self.class_ns = tmp_class_ns
        assert len(self.class_ns) == self.binary_labels.shape[1]
        assert len(self.class_ns) == self.class_probabilities.shape[1]
        self.n_classes = len(self.class_ns)

    def _calculate_fp_tp_rate(self):
        """Calculate false positives and true positive rates"""
        # Compute false and true positives, ROC data and other important binary classification metrics
        for class_n in self.class_ns:
            self.fps[class_n], self.tps[class_n], self.thresholds[class_n], self.sorted_ids[class_n] = \
                binary_clf_curve_with_ids(self.binary_labels[class_n], self.class_probabilities[class_n],
                                          y_true_ids=self.label_ids)
            if self.tps[class_n].size == 0 or self.fps[class_n][0] != 0 or self.tps[class_n][0] != 0:
                # Add an extra threshold position if necessary
                self.tps[class_n] = np.r_[0, self.tps[class_n]]
                self.fps[class_n] = np.r_[0, self.fps[class_n]]
                self.sorted_ids[class_n] = np.r_[None, self.sorted_ids[class_n]]
                self.thresholds[class_n] = np.r_[self.thresholds[class_n][0] + 1, self.thresholds[class_n]]

            self.fns[class_n] = self.tps[class_n][-1] - self.tps[class_n]
            self.tns[class_n] = self.fps[class_n][-1] - self.fps[class_n]
            # positive predictive value
            self.ppv[class_n] = self.tps[class_n] / (self.tps[class_n] + self.fps[class_n])
            # false discovery rate
            self.fdr[class_n] = self.fps[class_n] / (self.tps[class_n] + self.fps[class_n])
            # negative predictive value
            self.npv[class_n] = self.tns[class_n] / (self.tns[class_n] + self.fns[class_n])
            # false omission rate
            self.for1[class_n] = self.fns[class_n] / (self.tns[class_n] + self.fns[class_n])

            # true/false positive/negative rates
            self.fpr[class_n] = self.fps[class_n] / self.fps[class_n][-1]
            self.tpr[class_n] = self.tps[class_n] / self.tps[class_n][-1]
            self.tnr[class_n] = 1 - self.fpr[class_n]
            self.fnr[class_n] = 1 - self.tpr[class_n]
            self.roc_auc[class_n] = auc(self.fpr[class_n], self.tpr[class_n])
            self.average_precision[class_n] = average_precision_score(self.binary_labels[class_n],
                                                                      self.class_probabilities[class_n])

        self.fpr["roc_micro"], self.tpr["roc_micro"], self.thresholds["roc_micro"] = \
            roc_curve(self.binary_labels.values.ravel(), self.class_probabilities.values.ravel())
        self.tnr["roc_micro"] = 1 - self.fpr["roc_micro"]
        self.fnr["roc_micro"] = 1 - self.tpr["roc_micro"]
        self.roc_auc["roc_micro"] = auc(self.fpr["roc_micro"], self.tpr["roc_micro"])
        self.average_precision["pr_micro"] = average_precision_score(self.binary_labels.values.ravel(),
                                                                     self.class_probabilities.values.ravel())
        self.ppv["pr_micro"], self.tpr["pr_micro"], _ = precision_recall_curve(self.binary_labels.values.ravel(),
                                                                               self.class_probabilities.values.ravel())

        all_fpr = np.unique(np.concatenate([self.fpr[i] for i in self.class_ns]))

        # Then interpolate all ROC curves at this points
        mean_tpr = np.zeros_like(all_fpr)
        for class_n in self.class_ns:
            mean_tpr += interp(all_fpr, self.fpr[class_n], self.tpr[class_n])

        # Finally average it and compute AUC
        mean_tpr /= self.n_classes

        self.fpr["macro"] = all_fpr
        self.tpr["macro"] = mean_tpr
        self.tnr["macro"] = 1 - self.fpr["macro"]
        self.fnr["macro"] = 1 - self.tpr["macro"]

        self.roc_auc["macro"] = auc(self.fpr["macro"], self.tpr["macro"])

    def _get_index_from_threshold(self, class_n, threshold):
        """Get correct index from any arbitrary probability threshold cutoff"""
        assert class_n in self.class_ns, \
            "Class name is not in class names. {} not in {}".format(class_n, self.class_ns)
        index = binary_search(self.thresholds[class_n][::-1], threshold, exact_match=False)
        if index == len(self.thresholds[class_n]) - 1:
            return 0
        elif index == 0:
            true_index = len(self.thresholds[class_n]) - 1
            if self.thresholds[class_n][true_index] >= threshold:
                return true_index
            else:
                return true_index - 1
        else:
            return len(self.thresholds[class_n]) - index - 2

    def recall(self, class_n, threshold):
        return self.true_positive_rate(class_n, threshold)

    def sensitivity(self, class_n, threshold):
        return self.true_positive_rate(class_n, threshold)

    def specificity(self, class_n, threshold):
        return self.true_negative_rate(class_n, threshold)

    def true_positive_rate(self, class_n, threshold):
        return self.tpr[class_n][self._get_index_from_threshold(class_n, threshold)]

    def false_positive_rate(self, class_n, threshold):
        return self.fpr[class_n][self._get_index_from_threshold(class_n, threshold)]

    def true_negative_rate(self, class_n, threshold):
        return self.tnr[class_n][self._get_index_from_threshold(class_n, threshold)]

    def false_negative_rate(self, class_n, threshold):
        return self.fnr[class_n][self._get_index_from_threshold(class_n, threshold)]

    def positive_likelihood_ratio(self, class_n, threshold):
        fpr = self.false_positive_rate(class_n, threshold)
        tpr = self.true_positive_rate(class_n, threshold)
        return tpr / fpr

    def negative_likelihood_ratio(self, class_n, threshold):
        fpr = self.false_positive_rate(class_n, threshold)
        tpr = self.true_positive_rate(class_n, threshold)
        return fpr / tpr

    def diagnostic_odds_ratio(self, class_n, threshold):
        plr = self.positive_likelihood_ratio(class_n, threshold)
        nlr = self.negative_likelihood_ratio(class_n, threshold)
        return plr / nlr

    def positive_predictive_value(self, class_n, threshold):
        return self.ppv[class_n][self._get_index_from_threshold(class_n, threshold)]

    def precision(self, class_n, threshold):
        return self.positive_predictive_value(class_n, threshold)

    def accuracy(self, class_n, threshold):
        return (self.get_n_tps(class_n, threshold) + self.get_n_tns(class_n, threshold)) / len(self.binary_labels)

    def false_discovery_rate(self, class_n, threshold):
        return self.fdr[class_n][self._get_index_from_threshold(class_n, threshold)]

    def negative_predictive_value(self, class_n, threshold):
        return self.npv[class_n][self._get_index_from_threshold(class_n, threshold)]

    def false_omission_rate(self, class_n, threshold):
        return self.for1[class_n][self._get_index_from_threshold(class_n, threshold)]

    def f1_score(self, class_n, threshold):
        precision = self.precision(class_n, threshold)
        recall = self.recall(class_n, threshold)
        return 2 / ((1 / precision) + (1 / recall))

    def prevalence(self, class_n):
        return np.count_nonzero(self.binary_labels[class_n]) / len(self.binary_labels)

    def confusion_matrix(self):
        labels = self.binary_labels.idxmax(1)
        predictions = self.class_probabilities.idxmax(1)
        return confusion_matrix(labels, predictions, labels=self.class_ns)

    def plot_calibration_curve(self, class_n, save_fig_path=None):
        if save_fig_path is not None:
            assert os.path.exists(os.path.dirname(save_fig_path)), \
                "Output directory does not exist: {}".format(save_fig_path)

        labels = self.binary_labels[class_n]
        predictions = self.class_probabilities[class_n]
        clf_score = brier_score_loss(labels, predictions)
        fraction_of_positives, mean_predicted_value = \
            calibration_curve(labels, predictions, n_bins=10)

        plt.figure(figsize=(10, 10))
        ax1 = plt.subplot2grid((3, 1), (0, 0), rowspan=2)
        ax2 = plt.subplot2grid((3, 1), (2, 0))

        ax1.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")

        ax1.plot(mean_predicted_value, fraction_of_positives, "s-",
                 label="%s (%1.3f)" % (class_n, clf_score))

        ax2.hist(predictions, range=(0, 1), bins=10, label=class_n,
                 histtype="step", lw=2)
        ax1.set_ylabel("Fraction of positives")
        ax1.set_ylim([-0.05, 1.05])
        ax1.legend(loc="lower right")
        ax1.set_title('Calibration plots  (reliability curve)')

        ax2.set_xlabel("Mean predicted value")
        ax2.set_ylabel("Count")
        ax2.legend(loc="upper center", ncol=2)
        if save_fig_path is not None:
            plt.savefig(save_fig_path)
        else:
            plt.show()
            pass

    def get_fp_ids(self, class_n, threshold=0.5):
        """Get the false positive ids given a class and threshold"""
        return self._get_ids(self.fps, class_n, threshold)

    def get_tp_ids(self, class_n, threshold=0.5):
        """Get the false positive ids given a class and threshold"""
        return self._get_ids(self.tps, class_n, threshold)

    def get_fn_ids(self, class_n, threshold=0.5):
        """Get the false positive ids given a class and threshold"""
        return self._get_ids2(self.fns, class_n, threshold)

    def get_tn_ids(self, class_n, threshold=0.5):
        """Get the false positive ids given a class and threshold"""
        return self._get_ids2(self.tns, class_n, threshold)

    def get_n_tps(self, class_n, threshold=0.5):
        """Get number of false positives"""
        return self._get_n(self.tps, class_n, threshold=threshold)

    def get_n_fps(self, class_n, threshold=0.5):
        """Get number of false positives"""
        return self._get_n(self.fps, class_n, threshold=threshold)

    def get_n_tns(self, class_n, threshold=0.5):
        """Get number of false positives"""
        return self._get_n(self.tns, class_n, threshold=threshold)

    def get_n_fns(self, class_n, threshold=0.5):
        """Get number of false positives"""
        return self._get_n(self.fns, class_n, threshold=threshold)

    def _get_n(self, place, class_n, threshold=0.5):
        """Get number of false positives"""
        return place[class_n][self._get_index_from_threshold(class_n, threshold=threshold)]

    def _get_ids(self, place, class_n, threshold=0.5):
        """Get the false and true positive ids given a class and threshold"""
        assert self.label_ids is not None, "Cannot get ids if you do not pass in label_ids to class."
        index = self._get_index_from_threshold(class_n, threshold)
        data = place[class_n]
        names = []
        prev_n_calls = 0
        for x in range(index + 1):
            n_calls = data[x]
            if 0 < n_calls != prev_n_calls:
                if x >= len(self.sorted_ids[class_n]):
                    print("Wait what?")
                names.append(self.sorted_ids[class_n][x])
            prev_n_calls = n_calls
        return names

    def _get_ids2(self, place, class_n, threshold=0.5):
        """Get the false and true negative ids given a class and threshold"""
        assert self.label_ids is not None, "Cannot get ids if you do not pass in label_ids to class."
        index = self._get_index_from_threshold(class_n, threshold)
        data = place[class_n]
        names = []
        prev_n_calls = 0
        for x in reversed(range(index, len(place[class_n]))):
            n_calls = data[x]
            if n_calls != prev_n_calls:
                if x >= len(self.sorted_ids[class_n]):
                    print("Wait what?")
                names.append(self.sorted_ids[class_n][x + 1])
            prev_n_calls = n_calls
        return names

    def plot_roc(self, class_n, save_fig_path=None, title="Receiver operating characteristic"):
        if save_fig_path is not None:
            assert os.path.exists(os.path.dirname(save_fig_path)), \
                "Output directory does not exist: {}".format(save_fig_path)

        plt.figure()
        lw = 2
        plt.plot(self.fpr[class_n], self.tpr[class_n], color='darkorange',
                 lw=lw, label='ROC curve (area = %0.2f)' % self.roc_auc[class_n])
        plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(title)
        plt.legend(loc="lower right")
        if save_fig_path is not None:
            plt.savefig(save_fig_path)
        else:
            plt.show()
            pass

    def plot_multiclass_roc(self, lw=2, save_fig_path=None):
        # Plot all ROC curves
        if save_fig_path is not None:
            assert os.path.exists(os.path.dirname(save_fig_path)), \
                "Output directory does not exist: {}".format(save_fig_path)

        plt.figure()
        plt.plot(self.fpr["roc_micro"], self.tpr["roc_micro"],
                 label='micro-average ROC curve (area = {0:0.2f})'
                       ''.format(self.roc_auc["roc_micro"]),
                 color='deeppink', linestyle=':', linewidth=4)

        plt.plot(self.fpr["macro"], self.tpr["macro"],
                 label='macro-average ROC curve (area = {0:0.2f})'
                       ''.format(self.roc_auc["macro"]),
                 color='navy', linestyle=':', linewidth=4)

        colors = cycle(['aqua', 'darkorange', 'cornflowerblue'])
        for i, color in zip(self.class_ns, colors):
            plt.plot(self.fpr[i], self.tpr[i], color=color, lw=lw,
                     label='ROC curve of class {0} (area = {1:0.2f})'
                           ''.format(i, self.roc_auc[i]))

        plt.plot([0, 1], [0, 1], 'k--', lw=lw)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Some extension of Receiver operating characteristic to multi-class')
        plt.legend(loc="lower right")
        if save_fig_path is not None:
            plt.savefig(save_fig_path)
        else:
            plt.show()
            pass

    def plot_precision_recall(self, class_n, save_fig_path=None, title="Precision Recall curve"):
        if save_fig_path is not None:
            assert os.path.exists(os.path.dirname(save_fig_path)), \
                "Output directory does not exist: {}".format(save_fig_path)

        plt.figure()
        lw = 2
        plt.plot(self.tpr[class_n], self.ppv[class_n], color='darkblue',
                 lw=lw, label='Precision Recall curve (Average Precision = %0.2f)' % self.average_precision[class_n])
        plt.fill_between(self.tpr[class_n], self.ppv[class_n], alpha=0.2, color='darkblue')

        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('Recall (Positive predictive Value')
        plt.ylabel('Precision (True Positive Rate')
        plt.title(title)
        plt.legend(loc="lower right")
        if save_fig_path is not None:
            plt.savefig(save_fig_path)
        else:
            plt.show()
            pass

    def plot_micro_average_precision_score(self, save_fig_path=None):
        if save_fig_path is not None:
            assert os.path.exists(os.path.dirname(save_fig_path)), \
                "Output directory does not exist: {}".format(save_fig_path)

        step_kwargs = ({'step': 'post'}
                       if 'step' in signature(plt.fill_between).parameters
                       else {})

        plt.figure()
        plt.step(self.tpr['pr_micro'], self.ppv['pr_micro'], color='b', alpha=0.2,
                 where='post')
        plt.fill_between(self.tpr["pr_micro"], self.ppv["pr_micro"], alpha=0.2, color='b',
                         **step_kwargs)

        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.ylim([0.0, 1.05])
        plt.xlim([0.0, 1.0])
        plt.title('Average precision score, micro-averaged over all classes: '
                  'AP={0:0.2f}'.format(self.average_precision["pr_micro"]))
        if save_fig_path is not None:
            plt.savefig(save_fig_path)
        else:
            plt.show()
            pass

    def plot_multiclass_precision_recall(self, save_fig_path=None):
        if save_fig_path is not None:
            assert os.path.exists(os.path.dirname(save_fig_path)), \
                "Output directory does not exist: {}".format(save_fig_path)

        # setup plot details
        colors = cycle(['navy', 'turquoise', 'darkorange', 'cornflowerblue', 'teal'])

        plt.figure(figsize=(7, 8))
        f_scores = np.linspace(0.2, 0.8, num=4)
        lines = []
        labels = []
        for f_score in f_scores:
            x = np.linspace(0.01, 1)
            y = f_score * x / (2 * x - f_score)
            l, = plt.plot(x[y >= 0], y[y >= 0], color='gray', alpha=0.2)
            plt.annotate('f1={0:0.1f}'.format(f_score), xy=(0.9, y[45] + 0.02))

        lines.append(l)
        labels.append('iso-f1 curves')
        l, = plt.plot(self.tpr["pr_micro"], self.ppv["pr_micro"], color='gold', lw=2)
        lines.append(l)
        labels.append('micro-average Precision-recall (area = {0:0.2f})'
                      ''.format(self.average_precision["pr_micro"]))

        for class_name, color in zip(self.class_ns, colors):
            l, = plt.plot(self.tpr[class_name], self.ppv[class_name], color=color, lw=2)
            lines.append(l)
            labels.append('Precision-recall for class {0} (area = {1:0.2f})'
                          ''.format(class_name, self.average_precision[class_name]))

        fig = plt.gcf()
        fig.subplots_adjust(bottom=0.25)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Extension of Precision-Recall curve to multi-class')
        plt.legend(lines, labels, loc=(0, -.38), prop=dict(size=14))

        if save_fig_path is not None:
            plt.savefig(save_fig_path)
        else:
            plt.show()
            pass

    def get_confusion_matrix(self, threshold=0.5):
        """Get confusion matrix from binary classification
        :param threshold: threshold for cutoff between classes
        """
        assert len(self.class_ns) == 2, "Only two classes can be used for get_confusion_matrix"
        class_n = self.class_ns[0]
        tp = self.tps[class_n][self._get_index_from_threshold(class_n, threshold)]
        fn = self.fns[class_n][self._get_index_from_threshold(class_n, threshold)]
        tn = self.tns[class_n][self._get_index_from_threshold(class_n, threshold)]
        fp = self.fps[class_n][self._get_index_from_threshold(class_n, threshold)]

        false_discovery_rate = fp / (tp + fp)
        precision = tp / (tp + fp)
        false_omission_rate = fn / (tn + fn)
        negative_predictive_value = tn / (tn + fn)

        true_positive_rate_recall = tp / (tp + fn)
        false_negative_rate = fn / (tp + fn)

        false_positive_rate = fp / (fp + tn)
        true_negative_rate_specificity = tn / (tn + fp)

        positive_likelihood_ratio = true_positive_rate_recall / false_positive_rate
        negative_likelihood_ratio = false_negative_rate / true_negative_rate_specificity

        diagnostic_odds_ratio = positive_likelihood_ratio / negative_likelihood_ratio

        f1_score = 2 * ((precision * true_positive_rate_recall) / (precision + true_positive_rate_recall))

        return (np.asarray(
            [[tp, fp, precision, false_discovery_rate],
             [fn, tn, false_omission_rate, negative_predictive_value],
             [true_positive_rate_recall, false_positive_rate, positive_likelihood_ratio, diagnostic_odds_ratio],
             [false_negative_rate, true_negative_rate_specificity, negative_likelihood_ratio, f1_score]]))

    def plot_confusion_matrix(self, threshold=0.5, title="Confusion Matrix", save_fig_path=None, class_n=None):
        """Plot the confusion matrix with the information of each box explained
        :param threshold: classification threshold to plot
        :param title: Title of the confusion matrix
        :param save_fig_path: path to save figure
        :param class_n: class name to make as the positive condition
        """
        assert len(self.class_ns) == 2, "Only two classes can be used to plot confusion matrix"
        if class_n is None:
            class_n = self.class_ns[0]
        positive_threshold = threshold
        negative_threshold = 1-threshold
        tp = self.get_n_tps(class_n, positive_threshold)
        fp = self.get_n_fps(class_n, positive_threshold)
        fn = self.get_n_fns(class_n, negative_threshold)
        tn = self.get_n_tns(class_n, negative_threshold)

        return self.plot_confusion_matrix_helper(tp, fp, fn, tn, title=title, save_fig_path=save_fig_path)

    @staticmethod
    def plot_confusion_matrix_helper(tp, fp, fn, tn, title="Confusion Matrix", save_fig_path=None):
        """Plot the confusion matrix with the information of each box explained
        :param tp: true positives
        :param fp: false positives
        :param fn: false negatives
        :param tn: true negatives
        :return:
        :param title: Title of the confusion matrix
        :param save_fig_path: path to save figure
        """
        false_discovery_rate = fp / (tp + fp)
        precision = tp / (tp + fp)
        false_omission_rate = fn / (tn + fn)
        negative_predictive_value = tn / (tn + fn)

        true_positive_rate_recall = tp / (tp + fn)
        false_negative_rate = fn / (tp + fn)

        false_positive_rate = fp / (fp + tn)
        true_negative_rate_specificity = tn / (tn + fp)

        positive_likelihood_ratio = true_positive_rate_recall / false_positive_rate
        negative_likelihood_ratio = false_negative_rate / true_negative_rate_specificity

        diagnostic_odds_ratio = positive_likelihood_ratio / negative_likelihood_ratio

        f1_score = 2 * ((precision * true_positive_rate_recall) / (precision + true_positive_rate_recall))

        data = \
            np.asarray([[tp, fp,
                         "Precision\nPositive Predictive Value\ntp / (tp + fp)\n{0:.3f}".format(
                             precision),
                         "False Discovery Rate\nfp / (tp + fp)\n{0:.3f}".format(false_discovery_rate)],
                        [fn, tn,
                         "False Omission Rate\nfn / (tn + fn)\n{0:.3f}".format(false_omission_rate),
                         "Negative Predictive Value\ntn / (tn + fn)\n{0:.3f}".format(negative_predictive_value)],
                        ["Recall\nTrue Positive Rate\ntp / (tp + fn)\n{0:.3f}".format(true_positive_rate_recall),
                         "False Positive Rate\nfp / (fp + tn)\n{0:.3f}".format(false_positive_rate),
                         "Positive Likelihood Ratio\ntpr / fpr\n{0:.3f}".format(positive_likelihood_ratio),
                         "Diagnostic Odds Ratio\nplr / nlr \n{0:.3f}".format(diagnostic_odds_ratio)],
                        ["False Negative Rate\nfn / (tp + fn)\n{0:.3f}".format(false_negative_rate),
                         "Specificity\nTrue Negative Rate\ntn / (tn + fp)\n{0:.3f}".format(
                             true_negative_rate_specificity),
                         "Negative Likelihood Ratio\nfnr/tnr\n{0:.3f}".format(negative_likelihood_ratio),
                         "F1 Score\n2*[(ppv * tpr) / (ppv + tpr)]\n{0:.3f}".format(f1_score)]])

        fig = plt.figure(figsize=(15, 5))
        cp = tp + fn
        cn = tn + fp
        total = tn + fp + fn + tp

        col_labels = ['Condition Positive (cp):\n{}'.format(cp), "Condition Negative (cn):\n{}".format(cn),
                      "Prevalence\n cp / total\n{0:.3f}".format(cp / total),
                      "Accuracy\n[sum(tp) + sum(tn)] / total\n{0:.3f}".format((tp + tn) / total)]
        row_labels = ["Predicted Condition Positive:\n{}".format(tp + fp),
                      "Predicted Condition Negative:\n{}".format(tn + fn), "", ""]
        table_vals = data
        cmap = mpl.cm.get_cmap('Blues')
        blank = (0, 0, 0, 0)
        total_p = sum([tp, fp])
        total_n = sum([tn, fn])
        colors = [[cmap(tp / total_p), cmap(fp / total_p), blank, blank],
                  [cmap(fn / total_n), cmap(tn / total_n), blank, blank],
                  [blank] * 4, [blank] * 4]
        # Draw table
        the_table = plt.table(cellText=table_vals,
                              cellColours=colors,
                              colWidths=[0.05] * 4,
                              rowLabels=row_labels,
                              colLabels=col_labels,
                              loc='center')
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(10)
        the_table.scale(4, 4)
        plt.title(title)
        # Removing ticks and spines enables you to get the figure only with table
        plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
        plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)
        for pos in ['right', 'top', 'bottom', 'left']:
            plt.gca().spines[pos].set_visible(False)
        if save_fig_path is not None:
            plt.savefig(save_fig_path)
        else:
            plt.show()
        plt.close()
        return True

    def plot_probability_hist(self, class_n, save_fig_path=None, bins=None, normalize=False):
        """Plot histogram of the probabilities for a specific class
        :param class_n: class name
        :param save_fig_path: if set will save figure to path otherwise will just show
        :param bins: number of bins
        :param normalize: normalize histogram
        """
        title = "Histogram of Probabilities for class {}".format(class_n)

        if normalize:
            y_label = "density"
        else:
            y_label = "Count"

        fig = plt.figure(figsize=(12, 8))
        panel1 = plt.axes([0.1, 0.1, .8, .8])
        panel1.set_xlabel('probability')
        panel1.set_ylabel(y_label)
        panel1.grid(color='black', linestyle='-', linewidth=1, alpha=0.5)
        panel1.xaxis.set_major_locator(ticker.AutoLocator())
        panel1.xaxis.set_minor_locator(ticker.AutoMinorLocator())

        panel1.set_xlim(0, 1)
        panel1.set_title(label=title)

        if bins is None:
            bins = 30

        panel1.hist(self.class_probabilities[class_n], bins=bins, ls='dashed', normed=normalize, alpha=1)

        # option to save figure or just show it
        if save_fig_path is not None:
            plt.savefig(save_fig_path)
        else:
            plt.show()
        plt.close(fig)


def binary_clf_curve_with_ids(y_true, y_score, pos_label=None, sample_weight=None, y_true_ids=None):
    """Calculate true and false positives per binary classification threshold.

    Parameters
    ----------
    y_true : array, shape = [n_samples]
        True targets of binary classification

    y_score : array, shape = [n_samples]
        Estimated probabilities or decision function

    pos_label : int or str, default=None
        The label of the positive class

    sample_weight : array-like of shape = [n_samples], optional
        Sample weights.

    Returns
    -------
    fps : array, shape = [n_thresholds]
        A count of false positives, at index i being the number of negative
        samples assigned a score >= thresholds[i]. The total number of
        negative samples is equal to fps[-1] (thus true negatives are given by
        fps[-1] - fps).

    tps : array, shape = [n_thresholds <= len(np.unique(y_score))]
        An increasing count of true positives, at index i being the number
        of positive samples assigned a score >= thresholds[i]. The total
        number of positive samples is equal to tps[-1] (thus false negatives
        are given by tps[-1] - tps).

    thresholds : array, shape = [n_thresholds]
        Decreasing score values.
    """
    check_consistent_length(y_true, y_score)
    y_true = column_or_1d(y_true)
    y_score = column_or_1d(y_score)
    assert_all_finite(y_true)
    assert_all_finite(y_score)

    if sample_weight is not None:
        sample_weight = column_or_1d(sample_weight)

    # ensure binary classification if pos_label is not specified
    classes = np.unique(y_true)
    if (pos_label is None and
            not (np.array_equal(classes, [0, 1]) or
                 np.array_equal(classes, [-1, 1]) or
                 np.array_equal(classes, [0]) or
                 np.array_equal(classes, [-1]) or
                 np.array_equal(classes, [1]))):
        raise ValueError("Data is not binary and pos_label is not specified")
    elif pos_label is None:
        pos_label = 1.

    # make y_true a boolean vector
    y_true = (y_true == pos_label)

    # sort scores and corresponding truth values
    desc_score_indices = np.argsort(y_score, kind="mergesort")[::-1]
    if y_true_ids is not None:
        y_true_ids = [y_true_ids[i] for i in desc_score_indices]
    y_score = y_score[desc_score_indices]
    y_true = y_true[desc_score_indices]
    if sample_weight is not None:
        weight = sample_weight[desc_score_indices]
    else:
        weight = 1.

    # y_score typically has many tied values. Here we extract
    # the indices associated with the distinct values. We also
    # concatenate a value for the end of the curve.
    distinct_value_indices = np.where(np.diff(y_score))[0]
    threshold_idxs = np.r_[distinct_value_indices, y_true.size - 1]

    # accumulate the true positives with decreasing threshold
    tps = stable_cumsum(y_true * weight)[threshold_idxs]
    if sample_weight is not None:
        fps = stable_cumsum(weight)[threshold_idxs] - tps
    else:
        fps = 1 + threshold_idxs - tps

    return fps, tps, y_score[threshold_idxs], y_true_ids
