"""Dummy implementation of dataloaders."""
from dbispipeline import base
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_multilabel_classification


class MockLoader(base.Loader):

    def __init__(self,
                 n_features=10,
                 n_samples=80,
                 n_classes=4,
                 random_state=0):
        self.n_features = n_features
        self.n_samples = n_samples
        self.n_classes = n_classes
        self.random_state = random_state

    def load(self):
        return make_multilabel_classification(
            n_features=self.n_features,
            n_samples=self.n_samples,
            n_classes=self.n_classes,
            random_state=self.random_state)

    @property
    def configuration(self):
        return {
            'n_features': self.n_features,
            'n_samples': self.n_samples,
            'n_classes': self.n_classes,
            'random_state': self.random_state,
        }


class MockTrainTestLoader(MockLoader):

    def __init__(self,
                 n_features=10,
                 n_samples=80,
                 n_classes=4,
                 random_state=0,
                 test_ratio=0.3):
        super().__init__(n_features, n_samples, n_classes, random_state)
        self.test_ratio = test_ratio

    def load(self):
        X, y = super().load()
        xtrain, xtest, ytrain, ytest = train_test_split(
            X, y, test_size=self.test_ratio, random_state=self.random_state)
        return (xtrain, ytrain), (xtest, ytest)

    @property
    def configuration(self):
        config = super().configuration
        config['test_ratio'] = self.test_ratio
        return config


class MockTrainTestValidateLoader(MockTrainTestLoader):

    def __init__(self,
                 n_features=10,
                 n_samples=160,
                 n_classes=4,
                 random_state=0,
                 test_ratio=0.2,
                 validation_ratio=0.2):
        super().__init__(n_features, n_samples, n_classes, random_state,
                         test_ratio)
        self.validation_ratio = validation_ratio

    def load(self):
        (xtrain, ytrain), (xtest, ytest) = super().load()
        xtrain, xvalid, ytrain, yvalid = train_test_split(
            xtrain, ytrain, test_size=self.validation_ratio)
        return (xtrain, ytrain), (xvalid, yvalid), (xtest, ytest)

    @property
    def configuration(self):
        config = super().configuration
        config['validation_ratio'] = self.test_ratio
        return config


class MockMultiLoader(MockLoader):
    """ Mocking loader which loads a list of valid runs"""

    def __init__(self,
                 run_count,
                 n_features=10,
                 n_samples=80,
                 n_classes=4,
                 random_state=0):
        super().__init__(n_features, n_samples, n_classes, random_state)
        self._run_count = run_count

    @property
    def run_count(self):
        return self._run_count

    @property
    def configuration(self):
        configurations = []
        for i in range(self.run_count):
            conf = super().configuration
            conf['run_number'] = i
            configurations.append(conf)
        return configurations

    def load(self):
        for i in range(self.run_count):
            yield (super().load())
