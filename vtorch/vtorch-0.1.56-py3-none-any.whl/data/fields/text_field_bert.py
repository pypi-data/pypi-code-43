from .text_field import TextField
from overrides import overrides
from typing import Union

from vtorch.data.tokenizers import Tokenizer


from pytorch_transformers.tokenization_utils import PreTrainedTokenizer


class TextFieldBert(TextField):
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
                 max_padding_length: int = None, text_namespace: str = "text",
                 classification_task: bool = True) -> None:
        super().__init__(text, preprocessor, tokenizer, max_padding_length, text_namespace)
        self._classification_task = classification_task

    @overrides
    def _prepare(self, use_pretrained_tokenizer: bool = False):
        preprocessed_text = self._preprocess(self.text)
        self._tokenized_text = self._tokenize(preprocessed_text)
        if use_pretrained_tokenizer:
            if self._classification_task and self.tokenizer.sep_token is not None:
                self._tokenized_text = [self.tokenizer.cls_token] + self._tokenized_text + [self.tokenizer.sep_token]
            self._indexed_tokens = self.tokenizer.convert_tokens_to_ids(self._tokenized_text)
