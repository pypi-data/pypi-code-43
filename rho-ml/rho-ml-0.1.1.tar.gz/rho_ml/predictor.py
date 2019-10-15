from typing import Any

import attr
import marshmallow

from rho_ml.utils import Version

# todo: consider alternate name for Predictor
@attr.s(auto_attribs=True)
class Predictor(object):
    """ The most basic wrapper for an ML or other model.  Specific models should
    be a subclass of Predictor, and implement whatever appropriate subset of
    abstract methods defined here """
    input_schema: marshmallow.Schema
    output_schema: marshmallow.Schema

    @property
    def name(self) -> str:
        return str(self.__name__)

    @property
    def version(self) -> Version:
        raise NotImplementedError

    def train(self, *args, **kwargs) -> Any:
        """ This method should be overridden with the appropriate logic to
        pull in training data, evaluation data, run training, and return
        relevant data (e.g. training and validation metrics for each epoch)."""
        raise NotImplementedError

    def predict(self, *args, **kwargs) -> Any:
        """ This method should take a batch of items with appropriate types
        for the model, and generate a batch of outputs with appropriate
        types."""
        raise NotImplementedError

    def serialize(self) -> bytes:
        """ Serialize the predictor object to a byte string"""
        # todo: consider a default implementation
        raise NotImplementedError

    @classmethod
    def deserialize(cls, serialized: bytes):
        """ Instantiate a Predictor object from a serialized byte string """
        raise NotImplementedError

    def save_to_disk(self, path_to_output: str):
        """ Logic to save a single Predictor object to disk."""
        serialized = self.serialize()
        with open(path_to_output, 'wb') as f:
            f.write(serialized)

    @classmethod
    def load_from_disk(cls, path_to_file: str):
        """ Logic to load the Predictor subclass from disk. """
        with open(path_to_file, 'rb') as f:
            loaded = cls.deserialize(f.read())
        return loaded


