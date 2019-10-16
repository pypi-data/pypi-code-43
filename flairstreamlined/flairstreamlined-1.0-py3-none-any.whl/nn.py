import warnings
from pathlib import Path

from torch.nn import Module
from torch import load

from typing import Union

from flair import device
from flair.file_utils import load_big_file

class Model(Module):
    """Abstract base class for all downstream task models in Flair, such as SequenceTagger and TextClassifier.
    Every new type of model must implement these methods."""


    @classmethod
    def load(cls, model: Union[str, Path]):
        """
        Loads the model from the given file.
        :param model_file: the model file
        :return: the loaded text classifier model
        """
        model_file = cls._fetch_model(str(model))

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            # load_big_file is a workaround by https://github.com/highway11git to load models on some Mac/Windows setups
            # see https://github.com/zalandoresearch/flair/issues/351
            f = load_big_file(str(model_file))
            state = load(f, map_location=device)

        model = cls._init_model_with_state_dict(state)

        model.eval()
        model.to(device)

        return model