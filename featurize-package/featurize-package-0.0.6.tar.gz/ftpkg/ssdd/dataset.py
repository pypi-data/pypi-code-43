from featurize_jupyterlab.core import dataset, option, metadata
import numpy as np
import pandas as pd
import cv2
from torchvision import datasets, transforms
import os
import kaggle
import zipfile
from pathlib import Path
import torch
from sklearn.model_selection import train_test_split
import albumentations as albu
from albumentations import (HorizontalFlip, VerticalFlip, IAAPiecewiseAffine, ElasticTransform, IAASharpen, RandomBrightness,  ShiftScaleRotate, OneOf, Flip, Normalize, Resize, Compose, GaussNoise, ElasticTransform)
from albumentations.imgaug.transforms import IAASharpen
from torchvision.transforms import ToTensor


def make_transforms(phase, mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)):
    list_transforms = []
    if phase == "train":
         list_transforms.extend(
            [
                albu.HorizontalFlip(p=0.5),
                albu.IAAAdditiveGaussianNoise(p=0.2),
                albu.IAAPerspective(p=0.5),
                albu.OneOf(
                    [
                        albu.CLAHE(p=1),
                        albu.RandomBrightness(p=1),
                        albu.RandomGamma(p=1),],
                    p=0.9,),
                albu.OneOf(
                    [
                        albu.IAASharpen(p=1),
                        albu.Blur(blur_limit=3, p=1),
                        albu.MotionBlur(blur_limit=3, p=1),
                    ],p=0.9,),
                albu.OneOf(
                    [
                        albu.RandomContrast(p=1),
                        albu.HueSaturationValue(p=1),],
                    p=0.9,),
            ])
    list_transforms.extend(
        [
            Normalize(mean=mean, std=std, p=1),
            ToTensor(),
        ]
    )
    list_trfms = Compose(list_transforms)
    return list_trfms



class SSDDDataset(torch.utils.data.Dataset):

    def __init__(self, df, data_folder, transforms):
        self.df = df
        self.root = data_folder
        self.transforms = transforms
        self.fnames = self.df.index.tolist()

    def make_mask(self, df_row):
        '''Given a row index, return image_id and mask (256, 1600, 4)'''
        fname = df_row.name
        labels = df_row[:4]
        masks = np.zeros((256, 1600, 4), dtype=np.float32)

        for idx, label in enumerate(labels.values):
            if label is not np.nan:
                label = label.split(" ")
                positions = map(int, label[0::2])
                length = map(int, label[1::2])
                mask = np.zeros(256 * 1600, dtype=np.uint8)
                for pos, le in zip(positions, length):
                    mask[pos:(pos + le)] = 1
                masks[:, :, idx] = mask.reshape(256, 1600, order='F')
        return fname, masks

    def __getitem__(self, idx):
        df_row = self.df.iloc[idx]
        image_id, mask = self.make_mask(df_row)
        image_path = os.path.join(self.root, image_id)
        img = cv2.imread(image_path)
        if self.transforms is not None:
            augmented = self.transforms(image=img, mask=mask)
            img = augmented['image']
            mask = augmented['mask']
        mask = mask[0].permute(2, 0, 1)
        return img, mask, image_id, (df_row.defects != 0).astype(np.int64)

    def __len__(self):
        return len(self.fnames)


def prepare_datasets(folder):
    if os.path.isdir(folder / 'train'):
        return

    os.environ['KAGGLE_USERNAME'] = 'snaker'
    os.environ['KAGGLE_KEY'] = 'fa14a05cbcc69c74d8c98ff91c8385a8'
    kaggle.api.competition_download_files('severstal-steel-defect-detection', folder, False, False)
    with zipfile.ZipFile(folder / 'severstal-steel-defect-detection.zip', 'r') as zip_ref:
        zip_ref.extractall(folder)
    for category in ('train', 'test'):
        images_dir = folder / category
        try:
            os.mkdir(images_dir)
        except:
            pass
        with zipfile.ZipFile(folder / f'{category}_images.zip') as f:
            f.extractall(images_dir)


@dataset('SSDD Dataset', 'Kaggle Severstal: Steel Defect Detection')
@option('folder', help='The folder to donwload the datasets', default='/datasets')
@option('validation_percentage', help='The percentage(float from 0 to 1) to split as validation set', default='0.1', type='number')
@option('random_split_seed', help='The seed for spliting the dataset', type='number')
@option('force_download', help='Redownload the datasets', default=True, type='boolean')
def ssdd_dataset(folder, validation_percentage=0.1, random_split_seed=666, force_download=False):
    folder = Path(folder)
    prepare_datasets(folder)
    df = pd.read_csv(folder / 'train.csv')
    train_df, val_df = train_test_split(df, test_size=0.1, random_state=random_split_seed)
    return (
        SSDDDataset(train_df, folder, make_transforms('train')),
        SSDDDataset(val_df, folder, make_transforms('val'))
    )
