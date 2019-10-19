import os
import zipfile
from pathlib import Path

import albumentations as albu
import cv2
import numpy as np
import pandas as pd
import torch
from albumentations import (Compose, ElasticTransform, Flip, GaussNoise,
                            HorizontalFlip, IAAPiecewiseAffine, IAASharpen,
                            Normalize, OneOf, RandomBrightness, Resize,
                            ShiftScaleRotate, VerticalFlip)
from albumentations.imgaug.transforms import IAASharpen
from sklearn.model_selection import train_test_split
from torchvision import datasets, transforms
from torchvision.transforms import ToTensor

from featurize_jupyterlab.core import Dataset, Option


class SSDDDataset(torch.utils.data.Dataset):

    def __init__(self, df, data_folder, transforms):
        self.df = df
        self.root = data_folder
        self.transforms = transforms
        self.fnames = self.df.index.tolist()
        self.to_tensor = ToTensor()

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
        image_path = os.path.join(self.root, 'train', image_id)
        img = cv2.imread(image_path)
        if self.transforms is not None:
            img, mask = self.transforms([img, mask])
        img = self.to_tensor(img)
        mask = self.to_tensor(mask)

        return img, mask, image_id, (df_row.defects != 0).astype(np.int64)

    def __len__(self):
        return len(self.fnames)


def prepare_datasets(folder):
    if os.path.isfile(folder / 'train_processed.csv'):
        return

    os.environ['KAGGLE_USERNAME'] = 'snaker'
    os.environ['KAGGLE_KEY'] = 'fa14a05cbcc69c74d8c98ff91c8385a8'
    import kaggle
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

    gen_processed_csv(folder)


def gen_processed_csv(folder):
    a = pd.read_csv(folder / 'train.csv')
    processed_csv_file = folder / 'train_processed.csv'
    if os.path.isfile(processed_csv_file):
        return
    b,c = [], []
    d,e = {}, {}
    for i,j in a.iterrows():
        if j['ImageId_ClassId'].split('_')[0] not in d.keys():
            d[j['ImageId_ClassId'].split('_')[0]] = []
            d[j['ImageId_ClassId'].split('_')[0]].append(j['EncodedPixels'])
        else:
            d[j['ImageId_ClassId'].split('_')[0]].append(j['EncodedPixels'])

    for i,j in d.items():
        x = []
        x.append(i)
        x.append(j[0])
        x.append(j[1])
        x.append(j[2])
        x.append(j[3])
        if j[0] is not np.nan or j[1] is not np.nan or j[2] is not np.nan or j[3] is not np.nan:
            defect = 1
        else:
            defect = 0
        x.append(defect)
        c.append(x)

    df = pd.DataFrame(c, columns=['ImageId','1','2','3','4','defects'])
    df.to_csv(processed_csv_file, index=False)


class FeaturizeSSDDDataset(Dataset):
    """Kaggle Severstal Steel Defect Detection Dataset
    """
    name = 'SSDD Dataset'

    folder = Option(default='/datasets')
    validation_percentage = Option(type='number')
    random_split_seed = Option(type='number')
    batch_size = Option(type='number', default=16)
    force_download = Option(type='boolean')

    train_dataloader = Option(type='hardcode', help='The `Train Dataloader` which should be already configured', required=False)
    val_dataloader = Option(type='hardcode', help='The `Val Dataloader` which should be already configured', required=False)

    def __call__(self):
        folder = Path(self.folder)
        prepare_datasets(folder)
        df = pd.read_csv(folder / 'train_processed.csv', index_col='ImageId')
        train_df, val_df = train_test_split(
            df,
            test_size=self.validation_percentage,
            random_state=self.random_split_seed
        )
        return (
            torch.utils.data.DataLoader(SSDDDataset(train_df, folder, self.train_dataloader), self.batch_size),
            torch.utils.data.DataLoader(SSDDDataset(val_df, folder, self.val_dataloader), self.batch_size)
        )
