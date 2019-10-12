from pathlib import Path
import torch
from torch.utils.data.dataset import Dataset as TorchDataset
from torch.utils.data import random_split, DataLoader
from collections import OrderedDict
import mrcfile as mrc
import numpy as np
np.set_printoptions(precision=2)
import warnings
import json
from tqdm import tqdm
warnings.filterwarnings("ignore")
import random
from kinlin import Dataset

class SHRECDataset(TorchDataset):

    def __init__(self, path: Path, mrcs: list, patch_size: int, augmentation: bool = True,
                 full_tomo: bool = True, classmasks: bool = True, grandmodel: bool = False, even_odd: bool = False):
        # inputs
        self.path = path
        self.mrcs = mrcs
        self.patch_size = patch_size
        self.augmentation = augmentation

        # find tomograms
        self.tomo_dirs = [f for f in self.path.iterdir() if f.is_dir() and f.name.isdigit() and int(f.name) in mrcs]
        self.tomo_dirs.sort()
        self.tomo_count = len(self.tomo_dirs)

        # loading progressbar settings
        total = full_tomo * self.tomo_count + classmasks * self.tomo_count + grandmodel * self.tomo_count \
                + even_odd * 2 * self.tomo_count

        t = tqdm(total=total, desc=f'Loading data', unit='mrc', ncols=100, mininterval=0.5)

        # reconstructions
        if full_tomo:
            self.reconstructions = []

            for f in self.tomo_dirs:
                with mrc.open(f / f'cropped_reconstruction_{f.name}.mrc', mode='r', permissive=True) as m:
                    tomo_data = m.data.copy().astype(np.float32)
                    tomo_data = (tomo_data - np.mean(tomo_data)) / np.std(tomo_data)
                    tomo_data = (tomo_data - np.min(tomo_data)) / (np.max(tomo_data) - np.min(tomo_data))
                    self.reconstructions.append(tomo_data)
                t.update()
        else:
            self.reconstructions = None

        # classmasks
        if classmasks:
            self.classmasks = []

            for f in self.tomo_dirs:
                with mrc.open(f / f'dilated_classmask_{f.name}.mrc', mode='r', permissive=True) as m:
                    tomo_data = m.data.copy().astype(np.int64)
                    self.classmasks.append(tomo_data)
                t.update()
        else:
            self.classmasks = None

        # even and odd reconstructions
        if even_odd:
            self.evens = []
            self.odds = []

            for f in self.tomo_dirs:
                with mrc.open(f / f'cropped_new_reconstruction_{f.name}_even.mrc', mode='r', permissive=True) as m:
                    tomo_data = m.data.copy().astype(np.float32)
                    tomo_data = (tomo_data - np.mean(tomo_data)) / np.std(tomo_data)
                    tomo_data = (tomo_data - np.min(tomo_data)) / (np.max(tomo_data) - np.min(tomo_data))
                    self.evens.append(tomo_data)
                t.update()

            for f in self.tomo_dirs:
                with mrc.open(f / f'dilated_classmask_{f.name}_odd.mrc', mode='r', permissive=True) as m:
                    tomo_data = m.data.copy().astype(np.float32)
                    tomo_data = (tomo_data - np.mean(tomo_data)) / np.std(tomo_data)
                    tomo_data = (tomo_data - np.min(tomo_data)) / (np.max(tomo_data) - np.min(tomo_data))
                    self.odds.append(tomo_data)
                t.update()
        else:
            self.evens = None
            self.odds = None

        # ground truth
        if grandmodel:
            self.gts = []
            for f in self.tomo_dirs:
                with mrc.open(f / f'grandmodel_{f.name}.mrc', mode='r', permissive=True) as m:
                    tomo_data = m.data.copy().astype(np.float32)
                    tomo_data = (tomo_data - np.mean(tomo_data)) / np.std(tomo_data)
                    tomo_data = (tomo_data - np.min(tomo_data)) / (np.max(tomo_data) - np.min(tomo_data))
                    self.gts.append(tomo_data)
                t.update()
        else:
            self.gts = None
        t.close()

        # load glossaries
        with open(str(self.path / 'num2pdb.json'), 'r') as fp:
            self.num2pdb = json.load(fp)
            # json dict keys are always strings, convert them to ints
            self.num2pdb = OrderedDict({int(k): v for k, v in self.num2pdb.items()})
        with open(str(self.path / 'pdb2num.json'), 'r') as fp:
            self.pdb2num = json.load(fp)

        # calculate classes count
        self.n_cl = len(self.num2pdb.keys())

        # tomograms shape
        try:
            self.tomo_dim = self.reconstructions[0].shape
        except:
            self.tomo_dim = self.classmasks[0].shape

        # patches calculation
        self.patch_side = self.patch_size // 2
        self.patch_overlap = self.patch_size // 3

        self.step = self.patch_size + 1 - self.patch_overlap
        self.p_centerZ = list(range(self.patch_side, self.tomo_dim[0] - self.patch_side, self.step))
        self.p_centerY = list(range(self.patch_side, self.tomo_dim[1] - self.patch_side, self.step))
        self.p_centerX = list(range(self.patch_side, self.tomo_dim[2] - self.patch_side, self.step))

        self.i_patches = np.array(np.meshgrid(list(range(self.tomo_count)),
                                              self.p_centerZ, self.p_centerY, self.p_centerX)).T.reshape(-1, 4)
        self.n_patches = self.i_patches.shape[0]

        t.write(f'Loaded {self.tomo_count} tomograms, split into {self.n_patches} patches of {self.patch_size}^3 voxels.')
        t.write(f'Each tomogram has: {"reconstructions," if full_tomo else ""} {"classmasks," if classmasks else ""}'
                f'{"ground truth," if grandmodel else ""} {"even and odd reconstructions" if even_odd else ""}\n')

    def __len__(self):
        return self.n_patches

    def __sample(self, item):

        # sample configuration
        tid = self.i_patches[item][0]  # tomo id
        center_position = self.i_patches[item][1:4]
        dim = list(zip(np.maximum(center_position - self.patch_side, 0),
                       np.minimum(center_position + self.patch_side, self.reconstructions[tid].shape)))

        # sanity checks, should never happen
        if dim[0][1] - dim[0][0] < self.patch_size or \
           dim[1][1] - dim[1][0] < self.patch_size or \
           dim[2][1] - dim[2][0] < self.patch_size:
            raise IOError

        sample = {
            'reconstruction': self.reconstructions[tid][dim[0][0]:dim[0][1], dim[1][0]:dim[1][1], dim[2][0]:dim[2][1]].copy() if self.reconstructions else None,
            'classmask': self.classmasks[tid][dim[0][0]:dim[0][1], dim[1][0]:dim[1][1], dim[2][0]:dim[2][1]].copy() if self.classmasks else None,
            'odd_reconstruction': self.odds[tid][dim[0][0]:dim[0][1], dim[1][0]:dim[1][1], dim[2][0]:dim[2][1]].copy() if self.odds else None,
            'even_reconstruction': self.evens[tid][dim[0][0]:dim[0][1], dim[1][0]:dim[1][1], dim[2][0]:dim[2][1]].copy() if self.evens else None,
            'gt': self.gts[tid][dim[0][0]:dim[0][1], dim[1][0]:dim[1][1], dim[2][0]:dim[2][1]].copy() if self.gts else None
        }

        return sample

    def __augment(self, sample):

        # fliplr
        if np.random.uniform() < 0.5:
            for k in sample:
                if sample[k] is not None:
                    sample[k] = np.fliplr(sample[k]).copy()  # fliplr returns view

        # rot 180
        if np.random.uniform() > 0.5:
            for k in sample:
                if sample[k] is not None:
                    rotation = 2  # 180 deg
                    axes = (0, 2)  # tilt axis only?
                    sample[k] = np.rot90(sample[k], k=rotation, axes=axes).copy()  # rot90 returns view

        return sample

    def __expand_and_filter(self, sample):
        # add channel dimension in front
        add_dimension = ['reconstruction', 'odd_reconstruction', 'even_reconstruction']
        for k in sample:
            if k in add_dimension and sample[k] is not None:
                sample[k] = sample[k][np.newaxis, ...]

        # filter empty samples
        sample = {k: v for k, v in sample.items() if v is not None}

        return sample

    def __getitem__(self, item):  # 0 to self.n_patches

        # sample appropriate patches from tomograms and additional files
        sample = self.__sample(item)

        # import matplotlib.pyplot as plt
        # fig, ax = plt.subplots(2, 2)
        # ax[0, 0].imshow(sample['reconstruction'][32])
        # ax[1, 0].imshow(sample['classmask'][32])

        # augment samples
        if self.augmentation:
            sample = self.__augment(sample)

        # ax[0, 1].imshow(sample['reconstruction'][32])
        # ax[1, 1].imshow(sample['classmask'][32])
        # plt.show()

        # return expanded (added channel dimension for appropriate samples) and filtered (removed None samples) samples
        return self.__expand_and_filter(sample)

class SHREC(Dataset):
    def __init__(self, path_to_shrec: Path, subtomo_size, augmentation: bool):
        super(SHREC, self).__init__()

        self.train_dataset = SHRECDataset(path_to_shrec, list(range(7, 8)), subtomo_size, augmentation=augmentation)
        self.validation_dataset = SHRECDataset(path_to_shrec, [8], subtomo_size, augmentation=augmentation)
        self.test_dataset = SHRECDataset(path_to_shrec, [9], subtomo_size, augmentation=False)

    def training_dataloader(self, batch_size=1, shuffle=True):
        return DataLoader(self.train_dataset, batch_size=batch_size, shuffle=shuffle, pin_memory=True, drop_last=True)

    def validation_dataloader(self, batch_size=1, shuffle=True):
        return DataLoader(self.validation_dataset, batch_size=batch_size, shuffle=shuffle, pin_memory=True, drop_last=True)

    def test_dataloader(self, batch_size=1, shuffle=True):
        return DataLoader(self.test_dataset, batch_size=batch_size, shuffle=True, pin_memory=True, drop_last=True)