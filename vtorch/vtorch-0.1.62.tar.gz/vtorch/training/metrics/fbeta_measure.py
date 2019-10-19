import torch
from overrides import overrides
from typing import Union, Optional, List
from vtorch.training.metrics import Metric
from vtorch.common.utils import tensor_to_ohe
from vtorch.common.checks import ConfigurationError


@Metric.register("fscore")
class FBetaMeasure(Metric):
    NAMES = ["precision", "recall", "fscore"]

    """Compute precision, recall, F-measure and support for each class.
        The precision is the ratio ``tp / (tp + fp)`` where ``tp`` is the number of
        true positives and ``fp`` the number of false positives. The precision is
        intuitively the ability of the classifier not to label as positive a sample
        that is negative.
        The recall is the ratio ``tp / (tp + fn)`` where ``tp`` is the number of
        true positives and ``fn`` the number of false negatives. The recall is
        intuitively the ability of the classifier to find all the positive samples.
        The F-beta score can be interpreted as a weighted harmonic mean of
        the precision and recall, where an F-beta score reaches its best
        value at 1 and worst score at 0.
        If we have precision and recall, the F-beta score is simply:
        ``F-beta = (1 + beta ** 2) * precision * recall / (beta ** 2 * precision + recall)``
        The F-beta score weights recall more than precision by a factor of
        ``beta``. ``beta == 1.0`` means recall and precision are equally important.
        The support is the number of occurrences of each class in ``y_true``.
        Parameters
        ----------
        beta : ``float``, optional (default = 1.0)
            The strength of recall versus precision in the F-score.
        average : string, [None (default), 'micro', 'macro']
            If ``None``, the scores for each class are returned. Otherwise, this
            determines the type of averaging performed on the data:
            ``'micro'``:
                Calculate metrics globally by counting the total true positives,
                false negatives and false positives.
            ``'macro'``:
                Calculate metrics for each label, and find their unweighted mean.
                This does not take label imbalance into account.
        labels: list, optional
            The set of labels to include and their order if ``average is None``.
            Labels present in the data can be excluded, for example to calculate a
            multi-class average ignoring a majority negative class. Labels not present
            in the data will result in 0 components in a macro average.
        """

    def __init__(self,
                 beta: float = 1.0,
                 average: str = None,
                 labels: List[int] = None) -> None:
        average_options = (None, 'micro', 'macro')
        if average not in average_options:
            raise ConfigurationError(f"`average` has to be one of {average_options}.")
        if beta <= 0:
            raise ConfigurationError("`beta` should be >0 in the F-beta score.")

        self._beta = beta
        self._average = average
        self._labels = labels

        # statistics
        # the total number of true positive instances under each class
        # Shape: (num_classes, )
        self._true_positive_sum: Union[None, torch.Tensor] = None
        # the total number of instances
        # Shape: (num_classes, )
        self._total_sum: Union[None, torch.Tensor] = None
        # the total number of instances under each _predicted_ class,
        # including true positives and false positives
        # Shape: (num_classes, )
        self._pred_sum: Union[None, torch.Tensor] = None
        # the total number of instances under each _true_ class,
        # including true positives and false negatives
        # Shape: (num_classes, )
        self._true_sum: Union[None, torch.Tensor] = None

    def __call__(self, predictions: torch.Tensor, gold_labels: torch.Tensor, mask: Optional[torch.Tensor] = None):
        predictions, gold_labels, mask = self.unwrap_to_tensors(predictions, gold_labels, mask)
        num_classes = predictions.size(-1)
        if len(gold_labels.size()) == 1:
            gold_labels = tensor_to_ohe(gold_labels, predictions.size(1))
        assert num_classes == gold_labels.size(-1)

        if self._true_positive_sum is None:
            self._true_positive_sum = torch.zeros(num_classes)
            self._true_sum = torch.zeros(num_classes)
            self._pred_sum = torch.zeros(num_classes)
            self._total_sum = torch.zeros(num_classes)

        true_sum = (gold_labels == 1).sum(dim=0).float()
        true_positive_sum = torch.where(predictions == 1, gold_labels,
                                        torch.tensor([0.0])).sum(dim=0)
        pred_sum = (predictions == 1).sum(dim=0).float()

        self._true_positive_sum += true_positive_sum
        self._true_sum += true_sum
        self._pred_sum += pred_sum
        self._total_sum += len(predictions)

    def get_metric(self, reset: bool = False):
        if self._true_positive_sum is None:
            raise RuntimeError("You never call this metric before.")

        tp_sum = self._true_positive_sum
        pred_sum = self._pred_sum
        true_sum = self._true_sum

        if self._average == 'micro':
            tp_sum = tp_sum.sum()
            pred_sum = pred_sum.sum()
            true_sum = true_sum.sum()

        beta2 = self._beta ** 2
        # Finally, we have all our sufficient statistics.
        precision = _prf_divide(tp_sum, pred_sum)
        recall = _prf_divide(tp_sum, true_sum)
        fscore = ((1 + beta2) * precision * recall /
                  (beta2 * precision + recall))
        fscore[tp_sum == 0] = 0.0

        if self._average == 'macro':
            precision = precision.mean()
            recall = recall.mean()
            fscore = fscore.mean()

        if reset:
            self.reset()

        if self._average is None:
            return {
                "precision": precision.tolist(),
                "recall": recall.tolist(),
                "fscore": fscore.tolist()
            }
        else:
            return {
                "precision": precision.item(),
                "recall": recall.item(),
                "fscore": fscore.item()
            }

    @overrides
    def reset(self) -> None:
        self._true_positive_sum = None
        self._pred_sum = None
        self._true_sum = None
        self._total_sum = None


def _prf_divide(numerator, denominator):
    """Performs division and handles divide-by-zero.
    On zero-division, sets the corresponding result elements to zero.
    """
    result = numerator / denominator
    mask = denominator == 0.0
    if not mask.any():
        return result

    # remove nan
    result[mask] = 0.0
    return result
