import torch
import logging
from typing import Dict, Union
from overrides import overrides

from .field import Field
from ..vocabulary import Vocabulary

logger = logging.getLogger(__name__)


class CategoricalField(Field):
    """
    A ``CategoricalField`` is a categorical label of some kind, where the categories are either strings of
    text or 0-indexed integers (if you wish to skip indexing by passing skip_indexing=True).
    If the categories need indexing, we will use a :class:`Vocabulary` to convert the string categories
    into integers.
    This field will get converted into an integer index representing the class category.
    Parameters
    ----------
    category : ``Union[str, int]``
    category_namespace : ``str``, optional (default="category")
        The namespace to use for converting category strings into integers.  We map category strings to
        integers for you (e.g., "entailment" and "contradiction" get converted to 0, 1, ...),
        and this namespace tells the ``Vocabulary`` object which mapping from strings to integers
        to use (so "entailment" as a label doesn't get the same integer id as "entailment" as a
        word).  If you have multiple different category fields in your data, you should make sure you
        use different namespaces for each one, always using the suffix "category" (e.g.,
        "passage_category" and "question_category").
    skip_indexing : ``bool``, optional (default=False)
        If your labels are 0-indexed integers, you can pass in this flag, and we'll skip the indexing
        step.  If this is ``False`` and your labels are not strings, this throws a ``ConfigurationError``.
    """

    def __init__(self,
                 category: Union[str, int],
                 category_namespace: str = 'category',
                 category_to_id: Dict[str, int] = None,
                 skip_indexing: bool = False) -> None:
        self.category = category
        self._category_namespace = category_namespace
        self._category_id = None
        self._category_to_id = category_to_id

        if skip_indexing:
            if not isinstance(category, int):
                raise ValueError("In order to skip indexing, your labels must be integers. "
                                 "Found labels = {}".format(category))
            else:
                self._label_ids = category
        else:
            if not isinstance(category, str):
                raise ValueError("LabelFields expects string label if skip_indexing=False. "
                                 "Found label: {}".format(category))

    @overrides
    def get_padding_lengths(self) -> Dict[str, int]:  # pylint: disable=no-self-use
        return {}

    @overrides
    def count_vocab_items(self, counter: Dict[str, Dict[str, int]]):
        if self._category_id is None:
            counter[self._category_namespace][self.category] += 1
        return counter

    @overrides
    def index(self, vocab: Vocabulary, use_pretrained_tokenizer: bool = False):
        if self._category_id is None:
            if self._category_to_id is None:
                self._category_id = vocab.get_token_index(self.category, self._category_namespace)
            else:
                self._category_id = self._category_to_id[self.category]

    @overrides
    def as_tensor(self, padding_lengths: Dict[str, int]) -> torch.Tensor:
        tensor = torch.tensor(self._category_id, dtype=torch.long)
        return tensor

    @overrides
    def empty_field(self):
        return CategoricalField(-1, self._category_namespace, skip_indexing=True)

    @overrides
    def __str__(self) -> str:
        return f"LabelField with label: {self.category} in namespace: '{self._category_namespace}'.'"
