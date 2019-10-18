from abc import abstractmethod
from numpy.random import RandomState

from .merge import Merge
from .image_entity import ImageEntity


class ImageMerge(Merge):
    """
    Subclass of merges for image entities. 
    Prevents the usage of a text merge on an image wentity, which has a distinct underlying data structure.
    """
    @abstractmethod
    def do(self, obj1: ImageEntity, obj2: ImageEntity, random_state_obj: RandomState) -> ImageEntity:
        pass
