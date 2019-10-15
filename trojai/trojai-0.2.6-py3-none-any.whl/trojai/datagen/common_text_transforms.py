from numpy.random import RandomState

from .text_transform import TextTransform
from .text_entity import TextEntity

class IdentityTextTransform(TextTransform):
    def __init__(self):
        pass
    def do(self, input_obj: TextEntity, random_state_obj: RandomState) -> TextEntity:
        return input_obj
