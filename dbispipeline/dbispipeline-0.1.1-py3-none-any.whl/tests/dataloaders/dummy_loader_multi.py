"""Dummy implementation of dataloaders."""
from dbispipeline import base
import numpy as np
from sklearn.datasets import make_multilabel_classification


class DummyLoader(base.Loader):
    """Dummy loader class, not distinguishing data."""

    def load(self):
        """Loads data as np array in range [1,100]."""
        return np.arange(1, 100)

    @property
    def configuration(self):
        """Returns the name of the loader for testing."""
        return {"name": "DummyLoader"}


class DummyTrainTestLoader(base.TrainTestLoader):
    """Dummy loader class, destinguishing train and test data."""

    def load_train(self):
        """Loads train data as np array in range [1,100]."""
        return (np.arange(0, 99), np.arange(1, 100))

    def load_test(self):
        """Loads test data as np array in range [1,49]."""
        return (np.arange(2, 50), np.arange(1, 49))

    @property
    def configuration(self):
        """Returns the name of the loader for testing."""
        return {"name": "DummyTrainTestLoader"}


class DummyTrainValidateTestLoader(base.TrainValidateTestLoader,
                                   DummyTrainTestLoader):
    """Dummy loader class, destinguishing train, validate and test data."""

    def load_validate(self):
        """Loads validate data as np array in the range [1,26]."""
        return (np.arange(0, 25), np.arange(1, 26))

    @property
    def configuration(self):
        """Returns the name of the loader for testing."""
        return {"name": "DummyTrainValidateTestLoader"}


class MockTrainTestLoader(base.TrainTestLoader):
    """Fakes train and test data."""

    def __init__(self, n_features=1, n_classes=4, n_samples=50):
        """Sets default values."""
        self.n_features = n_features
        self.n_classes = n_classes
        self.n_samples = n_samples

    def load_train(self):
        """Loads train data as np array."""
        x, y = make_multilabel_classification(
            n_features=self.n_features,
            n_samples=self.n_samples,
            n_classes=self.n_classes,
            random_state=0)
        if self.n_classes == 1:
            y = y.reshape((self.n_samples,))
        return x, y

    def load_test(self):
        """Loads test data as np array."""
        x, y = make_multilabel_classification(
            n_features=self.n_features,
            n_samples=self.n_samples,
            n_classes=self.n_classes,
            random_state=1)
        if self.n_classes == 1:
            y = y.reshape((self.n_samples,))
        return x, y

    @property
    def configuration(self):
        """Returns the name of the loader for testing."""
        return {"name": "MockTrainTestLoader"}
