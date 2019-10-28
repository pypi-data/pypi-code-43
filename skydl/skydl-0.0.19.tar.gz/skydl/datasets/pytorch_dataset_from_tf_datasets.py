# -*- coding: utf-8 -*-
from py_common_util.pytorch.torch_utils import TorchUtils

import torch
from py_common_util.common.common_utils import CommonUtils
import tensorflow_datasets as tfds
from skydl.datasets.super_tf_dataset_builder import SuperDatasetBuilder
from torch.utils.data.dataset import Dataset


class PytorchDatasetFromTfDatasets(Dataset):
    """
    自定义pytorch数据集
    TODO 改成多worker高性能读取数据
    :param tf_dataset_class 支持字符串和class名 e.g. "mnist" or MovieLensDatasetBuilder
    :param all_dataset_splits e.g. ["all"|"train"|"validation"|"test"]
    :param selected_split  按照分隔参数指定的比例来分隔数据集，只能选1个 i.e. "train"|"validation"|"test"
    """
    def __init__(self, tf_dataset_class: SuperDatasetBuilder,
                 all_datasets=["all"],
                 batch_size=128,
                 shuffle=1,
                 epochs=1,
                 train_size=0.7,
                 validation_size=0,
                 test_size=0.3,
                 selected_split="train",
                 features_transforms=None,
                 target_transforms=None):
        self._features_transforms = features_transforms
        self._target_transforms = target_transforms
        if isinstance(tf_dataset_class, str):
            tf_dataset_class_name = tf_dataset_class
            tf_dataset_class = SuperDatasetBuilder
        else:
            tf_dataset_class_name = tf_dataset_class.__name__
        snakecase_dataset_cls_name = SuperDatasetBuilder.camelcase_to_snakecase(tf_dataset_class_name)
        # 计算dataset splits
        selected_all_datasets = []
        for name in all_datasets:
            if name == "train":
                selected_all_datasets.append(tfds.Split.TRAIN)
            elif name == "test":
                selected_all_datasets.append(tfds.Split.TEST)
            elif name == "validation":
                selected_all_datasets.append(tfds.Split.VALIDATION)
            elif name == "all":  # convert "all" to ["train", "validation", "test"]
                all_splits = SuperDatasetBuilder.get_split_name_list(snakecase_dataset_cls_name)
                for name in all_splits:
                    if name == "train":
                        selected_all_datasets.append(tfds.Split.TRAIN)
                    elif name == "validation":
                        selected_all_datasets.append(tfds.Split.VALIDATION)
                    elif name == "test":
                        selected_all_datasets.append(tfds.Split.TEST)
                    else:
                        raise Exception("发现未知的Split类型: %s" % name)
        full_datasets = tf_dataset_class.load_batched_datasets(snakecase_dataset_cls_name,
                                                              split=selected_all_datasets,
                                                              shuffle=shuffle,
                                                              batch_size=batch_size,
                                                              epochs=epochs)
        all_length = 0
        for dataset_split in selected_all_datasets:
            all_length += SuperDatasetBuilder.get_num_examples(snakecase_dataset_cls_name, split=dataset_split)
        self._num_batch = SuperDatasetBuilder.get_total_num_batch(all_length, batch_size)
        train_dataset, validation_dataset, test_dataset = SuperDatasetBuilder.split_full_datasets(full_datasets, self._num_batch, train_size, validation_size, test_size)
        if selected_split == "train":
            self._length = int(train_size * self._num_batch)
            self._dataset = train_dataset
        elif selected_split == "validation":
            self._length = int(validation_size * self._num_batch)
            self._dataset = validation_dataset
        elif selected_split == "test":
            self._length = int(test_size * self._num_batch)
            self._dataset = test_dataset
        print("PytorchDatasetFromTfDatasets#all_length=%d，all_num_batch=%d，selected_num_batch=%d" % (all_length, self._num_batch, self._length))
        self._dataset_iter = self._dataset.__iter__()

    def __getitem__(self, index):
        return tfds.as_numpy(self._dataset_iter.next())

    def __len__(self):
        return self._length


@CommonUtils.print_exec_time
def do_main():
    datasets = {split: PytorchDatasetFromTfDatasets(tf_dataset_class="mnist",
                                            all_datasets=["all"],
                                            batch_size=128,
                                            shuffle=1,
                                            epochs=1,
                                            train_size=0.7,
                                            validation_size=0,
                                            test_size=0.2,
                                            selected_split=split) for split in ["train", "test"]}
    for features, labels in datasets["train"]:
        print(features, torch.nn.functional.one_hot(TorchUtils.np_to_tensor(labels)))
    print("finished reading pytorch dataset!!!")


if __name__ == '__main__':
    do_main()



