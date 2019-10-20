import os
import logging
from overrides import overrides
from typing import List, Iterable, Union, Dict
from pynlple.processing.preprocessor import StackingPreprocessor

import transformers

from vtorch.data import Instance
from vtorch.data.tokenizers import Tokenizer
from vtorch.common.loading import load_pickle
from vtorch.data.fields import Field, TextFieldCLS, MultiLabelField
from vtorch.data.dataset_readers.dataset_reader import DatasetReader


logger = logging.getLogger(__name__)


@DatasetReader.register("json_dataset_bert_reader")
class JsonDatasetBertReader(DatasetReader):
    def __init__(self, tokenizer: str = None, transformer_tokenizer_type: str = None,
                 transformer_tokenizer_name: str = None, to_lower: bool = True,
                 max_padding_length: int = None, lazy: bool = False):
        super().__init__(lazy=lazy)
        self.preprocessor = StackingPreprocessor([])
        if tokenizer is not None:
            self.tokenizer = Tokenizer.by_name(tokenizer)
        elif transformer_tokenizer_type is not None and transformer_tokenizer_name is not None:
            vocab_file = os.path.join(transformer_tokenizer_name, "vocab.txt")
            self.tokenizer = getattr(transformers,
                                     transformer_tokenizer_type).from_pretrained(vocab_file, do_lower_case=to_lower)
        self.to_lower = to_lower
        self.max_padding_length = max_padding_length
        self._pad_on_left = "xlnet" in transformer_tokenizer_name
        self._cls_token_at_end = "xlnet" in transformer_tokenizer_name

    @overrides
    def _read(self, file_path: str) -> Iterable[Instance]:
        data: List[Dict] = load_pickle(file_path)
        for sample in data:
            text = sample["text"]
            labels = sample["tags"] if "tags" in sample else sample["labels"]
            instance = self.text_to_instance(text=text, labels=labels)
            if instance is not None:
                yield instance

    @overrides
    def text_to_instance(self, text: str, labels: Union[str, int] = None) -> Instance:
        fields: Dict[str, Field] = {}
        if self.to_lower:
            text = text.lower()
        fields["text"] = TextFieldCLS(text=text, preprocessor=self.preprocessor, tokenizer=self.tokenizer,
                                      max_padding_length=self.max_padding_length,
                                      cls_token_at_end=self._cls_token_at_end, pad_on_left=self._pad_on_left)
        if labels is not None:
            fields["labels"] = MultiLabelField(labels=labels)
        return Instance(fields)
