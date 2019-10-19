import torch
import logging
from .field import Field
from overrides import overrides
from ..vocabulary import Vocabulary
from typing import Dict, Union, Sequence, Optional, cast, List

logger = logging.getLogger(__name__)


class MultiLabelField(Field):
    """
    A ``MultiLabelField`` is an extension of the :class:`LabelField` that allows for multiple labels.
    It is particularly useful in multi-label classification where more than one label can be correct.
    As with the :class:`LabelField`, labels are either strings of text or 0-indexed integers (if you wish
    to skip indexing by passing skip_indexing=True).
    If the labels need indexing, we will use a :class:`Vocabulary` to convert the string labels
    into integers.
    This field will get converted into a vector of length equal to the vocabulary size with
    one hot encoding for the labels (all zeros, and ones for the labels).
    Parameters
    ----------
    labels : ``Sequence[Union[str, int]]``
    label_namespace : ``str``, optional (default="labels")
        The namespace to use for converting label strings into integers.  We map label strings to
        integers for you (e.g., "entailment" and "contradiction" get converted to 0, 1, ...),
        and this namespace tells the ``Vocabulary`` object which mapping from strings to integers
        to use (so "entailment" as a label doesn't get the same integer id as "entailment" as a
        word).  If you have multiple different label fields in your data, you should make sure you
        use different namespaces for each one, always using the suffix "labels" (e.g.,
        "passage_labels" and "question_labels").
    skip_indexing : ``bool``, optional (default=False)
        If your labels are 0-indexed integers, you can pass in this flag, and we'll skip the indexing
        step.  If this is ``False`` and your labels are not strings, this throws a ``ConfigurationError``.
    num_labels : ``int``, optional (default=None)
        If ``skip_indexing=True``, the total number of possible labels should be provided, which is required
        to decide the size of the output tensor. `num_labels` should equal largest label id + 1.
        If ``skip_indexing=False``, `num_labels` is not required.
    """

    def __init__(self,
                 labels: Sequence[Union[str, int]],
                 label_namespace: str = 'labels',
                 skip_indexing: bool = False,
                 num_labels: Optional[int] = None) -> None:
        self.labels = labels
        self._label_namespace = label_namespace
        self._label_ids = None
        self._num_labels = num_labels

        if skip_indexing:
            if not all(isinstance(label, int) for label in labels):
                raise ValueError("In order to skip indexing, your labels must be integers. "
                                 "Found labels = {}".format(labels))
            if not num_labels:
                raise ValueError("In order to skip indexing, num_labels can't be None.")

            if not all(cast(int, label) < num_labels for label in labels):
                raise ValueError("All labels should be < num_labels. "
                                 "Found num_labels = {} and labels = {} ".format(num_labels, labels))

            self._label_ids = labels
        else:
            if not all(isinstance(label, str) for label in labels):
                raise ValueError("MultiLabelFields expects string labels if skip_indexing=False. "
                                 "Found labels: {}".format(labels))

    @overrides
    def get_padding_lengths(self) -> Dict[str, int]:  # pylint: disable=no-self-use
        return {}

    @overrides
    def count_vocab_items(self, counter: Dict[str, Dict[str, int]]):
        if self._label_ids is None:
            for label in self.labels:
                counter[self._label_namespace][label] += 1
        return counter

    @overrides
    def index(self, vocab: Vocabulary, use_pretrained_tokenizer: bool = False):
        if self._label_ids is None:
            self._label_ids = [vocab.get_token_index(label, self._label_namespace)  # type: ignore
                               for label in self.labels]
        if not self._num_labels:
            self._num_labels = vocab.get_vocab_size(self._label_namespace)

    @overrides
    def as_tensor(self, padding_lengths: Dict[str, int]) -> torch.Tensor:
        tensor = torch.zeros(self._num_labels, dtype=torch.long)  # vector of zeros
        if self._label_ids:
            tensor.scatter_(0, torch.LongTensor(self._label_ids), 1)

        return tensor

    @overrides
    def batch_tensors(self, tensor_list: List[torch.Tensor], batch_first: bool = False) -> List[torch.Tensor]:
        return torch.stack(tensor_list).type(torch.FloatTensor)

    @overrides
    def empty_field(self):
        return MultiLabelField([], self._label_namespace)

    @overrides
    def __str__(self) -> str:
        return f"MultiLabelField with labels: {self.labels} in namespace: '{self._label_namespace}'.'"
