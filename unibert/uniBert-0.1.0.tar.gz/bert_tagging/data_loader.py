import csv
from collections import defaultdict

from torch.utils import data


class loadDataset(data.Dataset):
    def __init__(self, fpaths, eval_task=None):
        samples = []
        tasks = defaultdict(list)
        for fpath in fpaths:
            with open(fpath, 'r', encoding='utf8', newline='') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader, None)
                for row in reader:
                    start_pos = 1
                    for pos, item in enumerate(row[start_pos:]):
                        pos += start_pos
                        if eval_task is None or headers[pos] in eval_task:
                            task = headers[0] + "_" + headers[pos]
                            row_dict = dict()
                            row_dict['input'] = row[0]
                            item = item.strip()
                            if '/' in item:
                                for i in item.split("/"):
                                    tasks[task].append(i) if i not in tasks[task] else tasks[task]
                            else:
                                tasks[task].append(item) if item not in tasks[task] else tasks[task]
                            tasks[task].sort()
                            row_dict['task'] = task
                            row_dict['label'] = item
                            samples.append(row_dict)
                self.sample = samples
                self.task = tasks

    def __len__(self):
        return len(self.sample)

    def __getitem__(self, idx):
        return self.sample[idx]
