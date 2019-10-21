import pandas as pd
import PIL
import os

import torch
from torch.utils.data import Dataset, DataLoader


class TimeSeriesDataset(Dataset):
    """
    Time Series Dataset for PyTorch RNN

    == Arguments ==
    time_series: pandas DataFrame
        the time series data

    target_col_name: string
        target column name in the DataFrame

    seq_len: int
        sequence length. How far would the model backpropagate when training.

    batch_size: int
        the size when using time series batching

    n_feature: int
        number of input features

    report: bool
        print the batched dataset information
    """
    def __init__(self, time_series, target_col_name, seq_len, batch_size, n_feature, report=True):
        self.seq_len = seq_len
        self.batch_size = batch_size
        self.n_feature = n_feature

        # Calculate maximum step
        n_step = (len(time_series) - 1) // (seq_len * batch_size)
        self.n_step = n_step

        n_used_data = n_step * seq_len * batch_size

        if report:
            print(f"Using \x1b[31m{seq_len} previous data\x1b[0m as context with \x1b[31mbatching " \
                  f"of {batch_size}\x1b[0m\nThere would be \x1b[31m{n_step} complete time steps\x1b[0m " \
                  f"with last \x1b[31m{len(time_series)-n_used_data} data excluded\x1b[0m\n")

        # Trim series to complete steps
        input_series = time_series[:n_used_data]
        target_series = time_series[target_col_name][1:n_used_data + 1]

        if hasattr(time_series, 'index'):
            self.input_ticks = input_series.index
            self.target_ticks = target_series.index

        # Data engineering for RNN
        batched_input_series = input_series.values.reshape(batch_size, n_step, seq_len, n_feature)
        self.X = torch.FloatTensor(batched_input_series).transpose(0, 1)

        batched_target_series = target_series.values.reshape(batch_size, n_step, seq_len, 1)
        self.y = torch.FloatTensor(batched_target_series).transpose(0, 1)

    def __getitem__(self, i):
        return self.X[i], self.y[i]

    def __len__(self):
        return len(self.X)


class TimeSeriesDataloader(DataLoader):
    """
    Time Series Dataloader when to complement jcopdl's TimeSeriesDataset

    == Arguments ==
    dataset: jcopdl.utils.TimeSeriesDataset
        the time series dataset object

    num_workers: int
        how many subprocesses to use for data loading. 0 means that the data will be loaded in the main process.
    """
    def __init__(self, dataset, num_workers=0):
        super().__init__(dataset, batch_size=1, num_workers=num_workers, collate_fn=lambda x: x[0])


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
