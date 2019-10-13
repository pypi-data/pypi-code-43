import logging
from overrides import overrides
from typing import List, Iterable, Union, Dict
from pynlple.processing.preprocessor import StackingPreprocessor


from vtorch.data import Instance
from vtorch.data.tokenizers import Tokenizer
from vtorch.common.loading import load_pickle
from vtorch.data.fields import Field, TextField, MultiLabelField
from vtorch.data.dataset_readers.dataset_reader import DatasetReader
from vtorch.data.preprocessors.pynlple_preprocessors import get_pynlple_preprocessors


logger = logging.getLogger(__name__)


@DatasetReader.register("test_dataset_reader")
class TestDatasetReader(DatasetReader):
    def __init__(self, preprocessors: List[List], tokenizer_type: str, to_lower: bool = True,
                 max_padding_length: int = None, lazy: bool = False):
        super().__init__(lazy=lazy)
        self.preprocessor = StackingPreprocessor(get_pynlple_preprocessors(preprocessors))
        self.tokenizer: Tokenizer = Tokenizer.by_name(tokenizer_type)
        self.to_lower = to_lower
        self.max_padding_length = max_padding_length

    @overrides
    def _read(self, file_path: str) -> Iterable[Instance]:
        data = load_pickle(file_path)
        for sample in data:
            text = sample["text"]
            labels = sample["labels"]
            instance = self.text_to_instance(text=text, labels=labels)
            if instance is not None:
                yield instance

    @overrides
    def text_to_instance(self, text: str, labels: Union[str, int] = None) -> Instance:
        fields: Dict[str, Field] = {}
        if self.to_lower:
            text = text.lower()
        fields["text"] = TextField(text=text, preprocessor=self.preprocessor, tokenizer=self.tokenizer,
                                   max_padding_length=self.max_padding_length)
        if labels is not None:
            fields["labels"] = MultiLabelField(labels=labels)
        return Instance(fields)
