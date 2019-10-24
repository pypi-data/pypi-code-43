import csv
import os
import pickle

from torch.utils import data


class loadOnceDataset(data.Dataset):
    def __init__(self, fpath, model, max_size=128):
        sample = []
        cache_path = fpath + ".cache"
        if os.path.isfile(cache_path):
            with open(cache_path, "rb") as cf:
                sample = pickle.load(cf)
        else:
            with open(fpath, encoding='utf') as csvfile:
                for i in list(csv.reader(csvfile)):
                    target_text = i[1]
                    source_text = i[0].split(" ")
                    if len(source_text) == len(target_text):
                        input = "[CLS] " + " ".join(source_text) + " [SEP]"
                        sample.append(model.get_feature_id_from_input(input, target_text + " [SEP]"))
                with open(cache_path, 'wb') as cf:
                    pickle.dump(sample, cf)

        self.sample = sample

    def __len__(self):
        return len(self.sample)

    def __getitem__(self, idx):
        return self.sample[idx]
