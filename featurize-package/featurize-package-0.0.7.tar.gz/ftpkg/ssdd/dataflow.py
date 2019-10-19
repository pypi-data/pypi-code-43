from featurize_jupyterlab.core import Dataflow, Option
from featurize_jupyterlab.transform import BasicImageTransformation, DualImageTransformation
import json
import albumentations as albu


class Resize(DualImageTransformation):
    """Resize image to any size
    """
    columns_config = Option(type='string', default='{"image": 0, "mask": 1}', post_process=lambda x: json.loads(x))
    width = Option(type='number', help='resize width of target image')
    height = Option(type='number', help='resize height of target image')

    def create_aug(self):
        return albu.Resize(self.height, self.width)


class RandomHorizontalFlip(DualImageTransformation):
    """Randomly horizontal flip an image
    """
    columns_config = Option(type='string', default='{"image": 0, "mask": 1}', post_process=lambda x: json.loads(x))

    def create_aug(self):
        return albu.HorizontalFlip(p=self.probability)


class Normalize(BasicImageTransformation):
    """Normalize image
    """
    columns_config = Option(type='string', default='[0]', post_process=lambda x: json.loads(x))
    normalize_type = Option(type='collection', default='imagenet', collection=[['imagenet', 'imagenet']])

    def create_aug(self):
        if self.normalize_type == 'imagenet':
            params = {
                'mean': (0.485, 0.456, 0.406),
                'std': (0.229, 0.224, 0.225)
            }
        return albu.Normalize(**params, p=self.probability)


class RandomCrop(DualImageTransformation):
    """Randomly crop an image
    """
    columns_config = Option(type='string', default='{"image": 0, "mask": 1}', post_process=lambda x: json.loads(x))
    width = Option(type='number', help='width to crop')
    height = Option(type='number', help='height to crop')
    def create_aug(self):
        return albu.RandomCrop(self.height, self.width, p=self.probability)
