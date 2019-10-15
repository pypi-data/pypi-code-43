from abc import abstractmethod
from numpy.random import RandomState
from .text_entity import TextEntity
from .transform import Transform


class TextTransform(Transform):
    @abstractmethod
    def do(self, input_obj: TextEntity, random_state_obj: RandomState) -> TextEntity:
        pass
