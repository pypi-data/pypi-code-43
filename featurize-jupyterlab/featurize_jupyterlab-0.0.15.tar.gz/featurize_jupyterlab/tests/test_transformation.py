from featurize_jupyterlab.transform import Column, DualImageTransformation, BasicImageTransformation, Compose
from featurize_jupyterlab.core import Option, clear_registed_components
from albumentations import RandomCrop, RandomBrightnessContrast
import pytest
import numpy as np

Crop = None
Brightness = None

@pytest.fixture(scope='module', autouse=True)
def components():
    global Crop, Brightness

    clear_registed_components()

    class Brightness(BasicImageTransformation):
        """Add a fixed integer to all pixels of an image
        """
        brightness_limit = Option(type='number', default=0.2)
        contrast_limit = Option(type='number', default=0.2)
        brightness_by_max = Option(type='number')

        def create_aug(self):
            return RandomBrightnessContrast(
                self.brightness_limit,
                self.contrast_limit,
                self.brightness_by_max,
                p=self.probability
            )


    class Crop(DualImageTransformation):
        """Apply random crop to images
        """
        width = Option(type='number')
        height = Option(type='number')

        def create_aug(self):
            return RandomCrop(self.height, self.width, p=self.probability)


def test_component_features():
    assert Crop.description == 'Apply random crop to images'
    assert Crop.name == 'Crop'
    assert len(Crop.options) == 4
    assert Crop.options[0].key == 'columns_config'
    assert Crop.options[1].key == 'probability'
    assert Crop.options[2].key == 'width'
    assert Crop.options[3].key == 'height'


def test_transform_featurizes():
    assert len(Crop.columns) == 5
    assert Crop.columns[0].key == 'image'
    assert Crop.columns[4].key == 'bboxes'


def test_single_transform():
    image = np.zeros((100, 100, 3))
    mask = np.zeros((100, 100, 3))

    fake_row_data = [mask, 'image name', image]
    columns_config = {
        'image': 2,
        'mask': 0
    }

    crop = Crop(width=30, height=50, probability=1, columns_config=columns_config)
    processed_image, image_name, processed_mask = crop(fake_row_data)

    assert processed_image.shape[0] == 50
    assert processed_image.shape[1] == 30
    assert processed_mask.shape[0] == 50
    assert processed_mask.shape[1] == 30
    assert image_name == 'image name'


def test_multiple_transform():
    image = np.zeros((100, 100, 3))
    mask1 = np.zeros((100, 100))
    mask2 = np.zeros((100, 100))
    keypoints = ((20, 30, 60, 80), (10, 30, 50, 70))

    fake_row_data = [image, 'image name', mask1, mask2, keypoints]
    columns_config = {
        'image': 0,
        'masks': (2, 3),
        'keypoints': 4
    }

    crop = Crop(width=30, height=50, probability=1, columns_config=columns_config)
    processed_image, image_name, processed_mask_1, processed_mask_2, processed_keypoints \
        = crop(fake_row_data)

    assert image_name == 'image name'
    assert processed_image.shape[0] == 50
    assert processed_image.shape[1] == 30

    assert processed_mask_1.shape[0] == 50
    assert processed_mask_1.shape[1] == 30

    assert processed_mask_2.shape[0] == 50
    assert processed_mask_2.shape[1] == 30

    assert processed_keypoints[0] != (20, 30, 60, 80)
    assert processed_keypoints[1] != (10, 30, 60, 70)


def test_basic_transform():
    image_1 = np.ones((100, 100, 3), dtype=np.uint8) * 6
    image_2 = np.ones((100, 100, 3), dtype=np.uint8) * 10

    fake_row_data = [image_1, 'image name 1', image_2, 'image name 2']
    columns_config = [0, 2]

    brightness = Brightness(
        brightness_limit=(0.3, 0.6),
        contrast_limit=(.3, .6),
        probability=0,
        columns_config=columns_config)
    processed_image_1, image_name_1, processed_image_2, image_name_2 = \
        brightness(fake_row_data)

    assert image_name_1, 'image name 1'
    assert image_name_2, 'image name 2'
    assert image_1.sum() == processed_image_1.sum()
    assert image_2.sum() == processed_image_2.sum()

    brightness = Brightness(
        brightness_limit=(.3, .6),
        contrast_limit=(.3, .6),
        probability=1,
        columns_config=columns_config)
    processed_image_1, image_name_1, processed_image_2, image_name_2 = \
        brightness(fake_row_data)

    assert image_name_1, 'image name 1'
    assert image_name_2, 'image name 2'
    assert image_1.sum() != processed_image_1.sum()
    assert image_2.sum() != processed_image_2.sum()


def test_compose_transformations():
    image = np.ones((100, 100, 3), dtype=np.uint8) * 100
    mask = np.ones((100, 100), dtype=np.uint8)

    crop_columns_config = { 'image': 0, 'mask': 1 }
    brightness_columns_config = [0]

    aug = Compose(
        Crop(
            width=30,
            height=50,
            probability=1,
            columns_config=crop_columns_config),
        Brightness(
            brightness_limit=(.3, .6),
            contrast_limit=(.3, .6),
            probability=1,
            columns_config=brightness_columns_config)
    )

    processed_image, processed_mask = aug([image, mask])
    assert processed_image.shape[0] == 50
    assert processed_image.shape[1] == 30

    assert processed_mask.shape[0] == 50
    assert processed_mask.shape[1] == 30

    assert image[0][0][0] == 100
    assert processed_image[0][0][0] != 100
