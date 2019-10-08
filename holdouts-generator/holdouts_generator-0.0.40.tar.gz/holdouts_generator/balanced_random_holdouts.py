from typing import Callable, List, Tuple
import itertools
from sklearn.model_selection import train_test_split
import numpy as np


def balanced_random_holdout(test_size: float, random_state: int)->[Callable, str, Tuple[float, int]]:
    """Return a function to create an holdout with given test_size and random_state and the path where to store it.
        test_size:float, float from 0 to 1, representing how many datapoints should be reserved to the test set.
        random_state:int, random state to reproduce experiment.
    """
    def holdout(dataset:Tuple):
        """
            dataset, the dataset to split. It must finish with an array containing the classes.
        """
        results = []
        rnd = np.random.RandomState(seed=random_state)
        for row in np.array([
            train_test_split(*[d[dataset[-1]==label] for d in dataset], test_size=test_size, random_state=random_state)
            for label in np.unique(dataset[-1])
        ]).T:
            array = np.array(list(itertools.chain.from_iterable(row)))
            rnd.shuffle(array)
            results.append(array)
        return results

    return holdout, {
        "test_size": test_size,
        "random_state": random_state
    }


def balanced_random_holdouts(test_sizes: List[float], quantities: List[int], random_state: int = 42)->List[Tuple[Callable, str, List]]:
    """Return a Generator of functions to create an holdouts with given test_sizes.
        test_sizes:List[float], floats from 0 to 1, representing how many datapoints should be reserved to the test set.
        quantities:List[int], quantities of holdouts for each test_size.
        random_state:int=42, random state to reproduce experiment.
    """
    if len(test_sizes) > 1:
        return [
            (
                *balanced_random_holdout(test_sizes[0], random_state+i),
                balanced_random_holdouts(test_sizes[1:], quantities[1:], random_state+i)
            ) for i in range(quantities[0])
        ]
    return [(*balanced_random_holdout(test_sizes[0], random_state+i), None) for i in range(quantities[0])]
