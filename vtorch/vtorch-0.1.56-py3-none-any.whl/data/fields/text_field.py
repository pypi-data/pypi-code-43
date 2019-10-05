import torch
from .field import Field
from overrides import overrides
from typing import Optional, List, Dict, Union

from vtorch.data.tokenizers import Tokenizer
from vtorch.data.vocabulary import Vocabulary
from vtorch.common.checks import ConfigurationError

from pytorch_transformers.tokenization_utils import PreTrainedTokenizer


class TextField(Field):
    """
    A ``TextField`` is a field for text storage. Moreover, the text is preprocessed and tokenized here.
    Available other methods as for base class ``Field``

    Parameters:
    ------------
    text: ``str``
        Raw text
    preprocessor:
        An object for text preprocessing. Should have ``preprocess`` method which returns ``str``
    tokenizer: ``Tokenizer``
        An object for text tokenization. Should have ``tokenize`` method which returns ``List[str]``
    max_padding_length: ``int`` (default = None)
        Maximum length for the padded sequence
    text_namespace: ``str`` (default = "text")
        The namespace to use for converting tokens into integers. We map tokens to
        integers for you (e.g., "I" and "am" get converted to 0, 1, ...),
        and this namespace tells the ``Vocabulary`` object which mapping from strings to integers
        to use.
    """
    def __init__(self, text: str, preprocessor, tokenizer: Union[Tokenizer, PreTrainedTokenizer],
                 max_padding_length: int = None, text_namespace: str = "text") -> None:
        self.text = text
        self._text_namespace = text_namespace
        if "preprocess" not in dir(preprocessor):
            raise ConfigurationError("Preprocessor must have `preprocess` method which returns ``str``")
        if "tokenize" not in dir(tokenizer):
            raise ConfigurationError("Tokenizer must have `tokenize` method which returns ``List[str]``")
        self.preprocessor = preprocessor
        self.tokenizer = tokenizer
        self._max_padding_length = max_padding_length

        self._tokenized_text: Optional[List[str]] = None
        self._indexed_tokens: Optional[List[int]] = None

    def _preprocess(self, text: str) -> str:
        return self.preprocessor.preprocess(text)

    def _tokenize(self, text: str) -> List[str]:
        return self.tokenizer.tokenize(text=text)

    def _prepare(self, use_pretrained_tokenizer: bool = False):
        preprocessed_text = self._preprocess(self.text)
        self._tokenized_text = self._tokenize(preprocessed_text)
        if use_pretrained_tokenizer:
            self._indexed_tokens = self.tokenizer.convert_tokens_to_ids(self._tokenized_text)

    @overrides
    def count_vocab_items(self, counter: Dict[str, Dict[str, int]]):
        if self._tokenized_text is None:
            self._prepare()
        for token in self._tokenized_text:
            counter[self._text_namespace][token] += 1

    @overrides
    def index(self, vocab: Vocabulary, use_pretrained_tokenizer: bool = False):
        if self._tokenized_text is None:
            self._prepare(use_pretrained_tokenizer)

        if not use_pretrained_tokenizer:
            self._indexed_tokens = [vocab.get_token_index(token, self._text_namespace) for token in self._tokenized_text]

    @overrides
    def get_padding_lengths(self) -> Dict[str, int]:
        if self._indexed_tokens is None:
            raise ConfigurationError("You must call .index(vocabulary) on a field before determining padding lengths.")
        if self._max_padding_length is not None:
            return {"num_tokens": min(len(self._indexed_tokens), self._max_padding_length)}
        return {"num_tokens": len(self._indexed_tokens)}

    def sequence_length(self) -> int:
        if self._indexed_tokens is None:
            raise ConfigurationError("You must call .index(vocabulary) on a field before determining padding lengths.")
        return len(self._indexed_tokens)

    @overrides
    def as_tensor(self, padding_length: Dict[str, int]) -> torch.Tensor:
        if self.sequence_length() >= padding_length["num_tokens"]:
            return torch.LongTensor(self._indexed_tokens[:padding_length["num_tokens"]])
        n_padded_elements = padding_length["num_tokens"] - self.sequence_length()
        return torch.cat([torch.LongTensor(self._indexed_tokens),
                          torch.zeros([n_padded_elements], dtype=torch.long)])

    @overrides
    def empty_field(self):
        text_field = TextField("", preprocessor=self.preprocessor, tokenizer=self.tokenizer)
        text_field._indexed_tokens = []
        text_field._tokenized_text = []
        return text_field

    @overrides
    def batch_tensors(self, tensor_list: List[torch.Tensor], batch_first: bool = False) -> List[torch.Tensor]:
        if batch_first:
            return torch.stack(tensor_list)
        return torch.stack(tensor_list).transpose(0, 1)

    def __len__(self) -> int:
        return len(self.text)

    def __str__(self):
        return self.text
