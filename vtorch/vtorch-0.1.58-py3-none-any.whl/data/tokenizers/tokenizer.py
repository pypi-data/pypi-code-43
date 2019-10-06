from typing import List
from vtorch.common.registrable import Registrable


class Tokenizer(Registrable):
    @staticmethod
    def tokenize(text: str) -> List[str]:
        raise NotImplementedError()
