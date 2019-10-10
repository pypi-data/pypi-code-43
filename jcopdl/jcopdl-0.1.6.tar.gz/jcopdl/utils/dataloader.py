import pandas as pd
import PIL
import os

import torch
from torch.utils.data import Dataset


class TimeSeriesDataset(Dataset):
    """
    Time Series Dataset for PyTorch
    The folder structur should be
        _________________________________
        data/
            train/
                img1.jpg
                2.jpg
                three.jpg
                ... all train images ...
            test/
                a.jpg
                b.jpg
                c.jpg
                ... all test images ...
            train_label.csv
            test_label.csv
        _________________________________

    train_label.csv and test_label.csv are the metadata. It should contain file name and its corresponding labels
    For example:
        __________________________
        fname,label1,label2,label3
        img1.jpg,1,1,0
        2.jpg,1,0,0
        three.jpg,1,1,1
        ...
        __________________________

    == Arguments ==
    csv_path: string
        the metadata file

    csv_path: string
        the img folder

    transform: torchvision.transform
        torchvision data augmentation

    fname_col: string
        header of file name used in the metadata
    """
    def __init__(self, X, y):
        self.X = X
        self.y = y

        self.X = torch.FloatTensor(self.X.values)
        self.y = torch.FloatTensor(self.y.values)

    def __getitem__(self, i):
        return self.X[i], self.y[i]

    def __len__(self):
        return len(self.X)


class MultilabelDataset(Dataset):
    """
    Multilabel Dataset for PyTorch
    The folder structur should be
        _________________________________
        data/
            train/
                img1.jpg
                2.jpg
                three.jpg
                ... all train images ...
            test/
                a.jpg
                b.jpg
                c.jpg
                ... all test images ...
            train_label.csv
            test_label.csv
        _________________________________

    train_label.csv and test_label.csv are the metadata. It should contain file name and its corresponding labels
    For example:
        __________________________
        fname,label1,label2,label3
        img1.jpg,1,1,0
        2.jpg,1,0,0
        three.jpg,1,1,1
        ...
        __________________________

    == Arguments ==
    csv_path: string
        the metadata file

    csv_path: string
        the img folder

    transform: torchvision.transform
        torchvision data augmentation

    fname_col: string
        header of file name used in the metadata
    """
    def __init__(self, csv_path, img_path, transform=None, fname_col='fname'):
        df = pd.read_csv(csv_path)
        assert df[fname_col].apply(lambda x: os.path.isfile(img_path + x)).all

        self.classes = df.columns[1:].to_list()

        self.img_path = img_path
        self.transform = transform

        self.X = df[fname_col]
        self.y = df.drop(columns=fname_col)

    def __getitem__(self, index):
        img = PIL.Image.open(self.img_path + self.X[index])
        if self.transform is not None:
            img = self.transform(img)

        label = torch.from_numpy(self.y.iloc[index].values).type(torch.FloatTensor)
        return img, label

    def __len__(self):
        return len(self.X)
