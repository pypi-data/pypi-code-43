from typing import List
from .tokenizer import Tokenizer


@Tokenizer.register("base_tokenizer")
class BaseTokenizer(Tokenizer):
    @staticmethod
    def tokenize(text: str) -> List[str]:
        return text.split()
