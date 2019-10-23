"""Dummy models that can be used to test the evaluators."""
import numpy as np
from sklearn.base import BaseEstimator

train_split_correct = False
test_split_correct = False

split_checking = {
    'train_correct': False,
    'test_correct': False,
}


class SplitCheckingModel(BaseEstimator):

    def __init__(self, dataloader):
        """
        Creates teh SplitCheckingModel object.

        Args:
            test: needs to be the test class instance.
            dataloader: needs to be the dataloader used to run the evaluation.
        """
        self.dataloader = dataloader
        self.train_split_correct = False
        self.test_split_correct = False
        split_checking['train_correct'] = self.train_split_correct
        split_checking['test_correct'] = self.test_split_correct

    def fit(self, x, y):
        """Runns tests if the train data split is preserved."""
        (xtrain, ytrain), test = self.dataloader.load()
        xtrain_is_same = np.equal(x, xtrain).all()
        ytrain_is_same = np.equal(y, ytrain).all()
        split_checking['train_correct'] = xtrain_is_same and ytrain_is_same
        self.train_split_correct = split_checking['train_correct']

    def predict(self, x):
        """Checks if test split is preserved and predicts the true labels."""
        train, (xtest, ytest) = self.dataloader.load()
        split_checking['test_correct'] = np.equal(x, xtest).all()
        self.test_split_correct = split_checking['test_correct']
        return ytest

    def predict_proba(self, x):
        """Checks if test split is preserved and predicts the true labels."""
        return self.predict(x) * .5

    def score(self, x, y):
        """Returns True if the prediction is y and otherwise False."""
        return np.equal(self.predict_proba(x), y).all()
