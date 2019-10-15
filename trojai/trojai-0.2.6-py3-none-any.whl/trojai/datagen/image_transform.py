from abc import abstractmethod
from numpy.random import RandomState
from trojai.datagen.image_entity import ImageEntity
from trojai.datagen.transform_interface import Transform


class ImageTransform(Transform):
    @abstractmethod
    def do(self, input_obj: ImageEntity, random_state_obj: RandomState) -> ImageEntity:
        pass
