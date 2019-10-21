from sklearn.model_selection import train_test_split
from collections import Iterable
import json


def split_write_data(*data: Iterable, test_size: float = 0.1,
                     prefix: str = "demo"):
    """

    Args:
        *data: Your data, json type data expected
        test_size: split size for train_test_split
        prefix: target file prefix, default is demo

    """
    if len(data) == 1:
        #         one type data
        x_train, x_test = train_test_split(data, test_size=test_size,
                                           shuffle=True)
        with open(f"{prefix}.train", 'w') as tr:
            json.dump(x_train, tr)
        with open(f"{prefix}.test", "w") as te:
            json.dump(x_test, te)
    elif len(data) == 2:
        #         x and y
        x_train, x_test, y_train, y_test = train_test_split(data,
                                                            test_size=test_size,
                                                            shuffle=True)
        train_data = dict()
        train_data["x"] = x_train
        train_data["y"] = y_train

        test_data = dict()
        test_data["x"] = x_test
        test_data["y"] = y_test
        with open(f"{prefix}.train", 'w') as tr:
            json.dump(train_data, tr)
        with open(f"{prefix}.test", "w") as te:
            json.dump(test_data, te)


