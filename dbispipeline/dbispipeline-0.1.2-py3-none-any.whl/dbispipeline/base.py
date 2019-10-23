"""Base classes for the dbispipeline."""
from abc import ABC, abstractmethod

from sklearn.model_selection import ParameterGrid


class Loader(ABC):
    """Abstract base class of a dataloader."""

    @abstractmethod
    def load(self):
        """Returns the data loaded by the dataloader."""
        pass

    @property
    @abstractmethod
    def configuration(self):
        """Returns a dict-like representation of the configuration."""
        pass

    @property
    def run_count(self):
        return 0

    @property
    def is_multiloader(self):
        return self.run_count > 0


class MultiLoaderGenerator(Loader):
    """ this class dynamically constructs a multiloader by selecting a loader
    along with a set of parameters to be used by it.

    Args:
        loader_class: the class of the dataloader to be instantiated. Do not
            pass an instance.
        parameters: if passed a list, this generator will return one dataloader
            instance for each entry in the list, and each entry in the list is
            passed to the constructor of the loader.
            If passed a dict, a grid of all combinations is generated and
            passed to the loader.
    """

    def __init__(self, loader_class, parameters):
        self.loaders = []
        if isinstance(parameters, dict):
            for sample in ParameterGrid(parameters):
                # this produces only dicts
                self.loaders.append(loader_class(**sample))
        else:
            for sample in parameters:
                if isinstance(sample, dict):
                    self.loaders.append(loader_class(**sample))
                else:
                    self.loaders.append(loader_class(*sample))

    def load(self):
        for loader in self.loaders:
            yield loader.load()

    @property
    def configuration(self):
        for i, loader in enumerate(self.loaders):
            config = loader.configuration
            config['run_number'] = i
            config['class'] = loader.__class__.__name__
            yield config

    @property
    def run_count(self):
        return len(self.loaders)


class TrainTestLoader(Loader):
    """Abstract dataloader destinguishing trian and test data."""

    @abstractmethod
    def load_train(self):
        """Returns the train data."""
        pass

    @abstractmethod
    def load_test(self):
        """Returns the test data."""
        pass

    def load(self):
        """Returns the data as a train, test tuple."""
        return self.load_train(), self.load_test()


class TrainValidateTestLoader(TrainTestLoader):
    """Abstract dataloader destinguishing trian and test data."""

    @abstractmethod
    def load_validate(self):
        """Returns the validation data."""
        pass

    def load(self):
        """Returns the data as a train, validation, test tuple."""
        return self.load_train(), self.load_validate(), self.load_test()


class Evaluator(ABC):
    """Abstract base class of an evaluator."""

    @abstractmethod
    def evaluate(self, model, data):
        """
        Evaluates the pipline based on the given dataset.

        Args:
            model: the model given in the pipeline.
            dataloader: the data used to load the dataset.

        Returns: An dict result.
        """
        pass

    @property
    @abstractmethod
    def configuration(self):
        """Returns a dict-like representation of this loader.
        This is for storing its state in the database.
        """
        pass

    def _check_loader_methods(self, loader, methods=None):

        if type(methods) == str:
            methods = [methods]

        for method in methods:
            m = getattr(loader, method, None)
            if not callable(m):
                raise ValueError(
                    f"The dataloader {loader} does not implement"
                    "the required method {m}. Required methods are: "
                    "{methods}")


class OutputHandler(ABC):
    """Abstract base class of an output handler."""

    @abstractmethod
    def handle_result(self, result):
        """
        Handles the result of an evaluator.

        Args:
            result: passed from an evaluator.
        """
        pass
