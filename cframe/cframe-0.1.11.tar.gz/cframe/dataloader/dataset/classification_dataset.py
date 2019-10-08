import os

import cv2
import pandas as pd
from torch.utils.data import Dataset


class ClassificationDataset(Dataset):
    def __init__(self, configer, phase, img_transform, aug_transform=None):
        self.configer = configer
        self.phase = phase
        self.root_dir = self.configer['root_dir']
        self.dataset_dir = self.configer['dataset_dir']
        self.csv_dir = self.configer['csv_dir']
        self.data_name = self.configer['data_name']

        self.img_transform = img_transform
        self.aug_transform = aug_transform

        self.imgs, self.labels = self.get_data_list()

    def __len__(self):
        return len(self.imgs)

    def __getitem__(self, index):
        img = cv2.imread(self.imgs[index])
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        label = self.labels[index]

        if self.aug_transform is not None:
            img = self.aug_transform(img)

        img = self.img_transform(img)

        return dict(img=img,
                    label=label,
                    name=self.imgs[index].split('\\')[-1])

    def get_data_list(self):
        df = pd.read_csv(
            os.path.join(self.root_dir,
                         self.csv_dir,
                         self.data_name,
                         '{}.csv'.format(self.phase))
        )

        imgs = []
        labels = []

        for i in range(len(df)):
            imgs.append(os.path.join(self.root_dir,
                                     df.loc[i, 'img'])
                        )
            labels.append(df.loc[i, 'label'])
        return imgs, labels
