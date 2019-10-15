from abc import ABC, abstractmethod
from numpy.random import RandomState

from trojai.datagen.merge_interface import Merge
from .text_entity import TextEntity

class TextMerge(Merge):
    """
    Subclass of merges for text entities. 
    Prevents the usage of an image merge on a text entity, which has a distinct underlying data structure.
    """
    @abstractmethod
    def do(self, obj1: TextEntity, obj2: TextEntity, random_state_obj: RandomState) -> TextEntity:
        pass
