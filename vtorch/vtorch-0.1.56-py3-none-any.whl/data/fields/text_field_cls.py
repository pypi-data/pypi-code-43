import torch
from .text_field import TextField
from overrides import overrides
from typing import Union, Dict, List

from vtorch.data.tokenizers import Tokenizer
from vtorch.common.checks import ConfigurationError


from pytorch_transformers.tokenization_utils import PreTrainedTokenizer


class TextFieldCLS(TextField):
    """
    A ``TextFieldCLS`` is a field for text storage, used for prepare text for a classification task.
    Moreover, the text is preprocessed and tokenized here.
    Available other methods as for base class ``TextField``

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
    cls_token_at_end: ``bool`` (default = False)
        If `False` place CLS token at start, ``True`` – at end (only for XLNet)
    pad_on_left: ``bool`` (default = False)
        Padding left only for XLNet
    """
    def __init__(self, text: str, preprocessor, tokenizer: Union[Tokenizer, PreTrainedTokenizer],
                 max_padding_length: int = None, text_namespace: str = "text", cls_token_at_end: bool = False,
                 pad_on_left: bool = False) -> None:
        super().__init__(text, preprocessor, tokenizer, max_padding_length, text_namespace)
        self._cls_token_at_end = cls_token_at_end
        self._pad_on_left = pad_on_left
        self._sep_token_index = self.tokenizer.convert_tokens_to_ids(self.tokenizer.sep_token)
        self._cls_token_index = self.tokenizer.convert_tokens_to_ids(self.tokenizer.cls_token)
        self._pad_token_index = self.tokenizer.convert_tokens_to_ids(self.tokenizer.pad_token)

    @overrides
    def _prepare(self, use_pretrained_tokenizer: bool = False):
        preprocessed_text = self._preprocess(self.text)
        self._tokenized_text = self._tokenize(preprocessed_text)
        self._indexed_tokens = self.tokenizer.convert_tokens_to_ids(self._tokenized_text)

    @overrides
    def as_tensor(self, padding_length: Dict[str, int]) -> torch.Tensor:

        if self.sequence_length() >= padding_length["num_tokens"]:
            return torch.LongTensor(self._post_processing_of_indexed_tokens(
                self._indexed_tokens[:padding_length["num_tokens"]]))
        n_padded_elements = padding_length["num_tokens"] - self.sequence_length()
        if self._pad_on_left:
            padded_indexed_tokens = torch.cat([torch.ones([n_padded_elements], dtype=torch.long)*self._pad_token_index,
                                               torch.LongTensor(self._post_processing_of_indexed_tokens(
                                                   self._indexed_tokens))])
        else:
            padded_indexed_tokens = torch.cat([torch.LongTensor(self._post_processing_of_indexed_tokens(
                self._indexed_tokens)),
                                               torch.zeros([n_padded_elements],
                                                           dtype=torch.long)*self._pad_token_index])
        return padded_indexed_tokens

    def _post_processing_of_indexed_tokens(self, indexed_tokens: List[int]) -> List[int]:
        pp_indexed_tokens = indexed_tokens + [self._sep_token_index]
        if self._cls_token_at_end:
            pp_indexed_tokens = pp_indexed_tokens + [self._cls_token_index]
        else:
            pp_indexed_tokens = [self._cls_token_index] + pp_indexed_tokens
        return pp_indexed_tokens

    @overrides
    def get_padding_lengths(self) -> Dict[str, int]:
        if self._indexed_tokens is None:
            raise ConfigurationError("You must call .index(vocabulary) on a field before determining padding lengths.")
        if self._max_padding_length is not None:
            return {"num_tokens": min(len(self._indexed_tokens)+2, self._max_padding_length)}
        return {"num_tokens": len(self._indexed_tokens)+2}
