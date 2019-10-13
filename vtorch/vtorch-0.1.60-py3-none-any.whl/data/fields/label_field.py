import torch
import logging
from typing import Dict, Union
from overrides import overrides

from .field import Field
from ..vocabulary import Vocabulary

logger = logging.getLogger(__name__)


class LabelField(Field):
    """
    A ``LabelField`` is a categorical label of some kind, where the labels are either strings of
    text or 0-indexed integers (if you wish to skip indexing by passing skip_indexing=True).
    If the labels need indexing, we will use a :class:`Vocabulary` to convert the string labels
    into integers.
    This field will get converted into an integer index representing the class label.
    Parameters
    ----------
    label : ``Union[str, int]``
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
    """

    def __init__(self,
                 label: Union[str, int],
                 label_namespace: str = 'labels',
                 skip_indexing: bool = False) -> None:
        self.label = label
        self._label_namespace = label_namespace
        self._label_id = None

        if skip_indexing:
            if not isinstance(label, int):
                raise ValueError("In order to skip indexing, your labels must be integers. "
                                 "Found labels = {}".format(label))
            else:
                self._label_ids = label
        else:
            if not isinstance(label, str):
                raise ValueError("LabelFields expects string label if skip_indexing=False. "
                                 "Found label: {}".format(label))

    @overrides
    def get_padding_lengths(self) -> Dict[str, int]:  # pylint: disable=no-self-use
        return {}

    @overrides
    def count_vocab_items(self, counter: Dict[str, Dict[str, int]]):
        if self._label_id is None:
            counter[self._label_namespace][self.label] += 1
        return counter

    @overrides
    def index(self, vocab: Vocabulary, use_pretrained_tokenizer: bool = False):
        if self._label_id is None:
            self._label_id = vocab.get_token_index(self.label, self._label_namespace)

    @overrides
    def as_tensor(self, padding_lengths: Dict[str, int]) -> torch.Tensor:
        tensor = torch.tensor(self._label_id, dtype=torch.long)
        return tensor

    @overrides
    def empty_field(self):
        return LabelField(-1, self._label_namespace, skip_indexing=True)

    @overrides
    def __str__(self) -> str:
        return f"LabelField with label: {self.label} in namespace: '{self._label_namespace}'.'"
