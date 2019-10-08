import os

import numpy as np
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset


class SegmentDataset(Dataset):
    def __init__(self, configer, phase, img_transform,
                 segment_transform=None, aug_transform=None):
        self.configer = configer
        self.phase = phase
        self.root_dir = self.configer['root_dir']
        self.dataset_dir = self.configer['dataset_dir']
        self.csv_dir = self.configer['csv_dir']
        self.data_name = self.configer['data_name']

        self.img_transform = img_transform
        self.segment_transform = segment_transform
        self.aug_transform = aug_transform

        self.imgs, self.segments = self.get_data_list()

    def __len__(self):
        return len(self.imgs)

    def __getitem__(self, index):
        img = Image.open(self.imgs[index])
        img = np.array(img)

        segment = Image.open(self.segments[index])
        segment = np.array(segment)

        if self.aug_transform is not None:
            img, segment = self.aug_transform(img, segment)

        img = self.img_transform(img)

        if self.segment_transform is not None:
            segment = self.segment_transform(segment)

        return dict(img=img,
                    segment=segment,
                    name=self.imgs[index].split('\\')[-1])

    def get_data_list(self):
        df = pd.read_csv(
            os.path.join(self.root_dir,
                         self.csv_dir,
                         self.data_name,
                         '{}.csv'.format(self.phase))
        )

        imgs = []
        segments = []

        for i in range(len(df)):
            imgs.append(os.path.join(self.root_dir,
                                     df.loc[i, 'img'])
                        )
            segments.append(os.path.join(self.root_dir,
                                       df.loc[i, 'segment'])
                          )
        return imgs, segments
