import csv
from collections import defaultdict

from torch.utils import data
from tqdm import tqdm


class loadTaggerDataset(data.Dataset):
    def __init__(self, fpaths, text_index: int = 0,
                 label_index: int = 1):
        samples = []
        labels = []
        for fpath in fpaths:
            with open(fpath, 'r', encoding='utf-8') as f:
                lines = f.read().splitlines()
                x, y = "", ""
                for line in tqdm(lines):
                    rows = line.split(' ')
                    if len(rows) == 1 or len(x.strip().split(" ")) >= 510:
                        row_dict = dict()
                        row_dict['input'] = x.strip()
                        row_dict['label'] = y.strip()
                        samples.append(row_dict)
                        x, y = "", ""
                    else:
                        x += rows[text_index] + " "
                        y += rows[label_index] + " "
                        if rows[label_index] not in labels and len(rows[label_index]) > 0:
                            labels.append(rows[label_index])
                            labels.sort()
        self.sample = samples
        self.label = labels

    def __len__(self):
        return len(self.sample)

    def __getitem__(self, idx):
        return self.sample[idx]
