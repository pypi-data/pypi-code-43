from pathlib import Path
from typing import Union, Any
from abc import ABC, abstractmethod
from cerberus import Validator
import numpy as np
import pandas as pd


class Client(ABC):
    """
    Base class for clients.
    """
    @abstractmethod
    def get(self) -> Union[pd.DataFrame, dict, list]:
        pass

    @abstractmethod
    def save(self,
             path: Union[Path, str],
             recursive_concepts: bool = True,
             **kwargs: str) -> None:
        pass


class DataValidator(Validator):  # noqa
    """
    A custom Cerberus Validator. Cerberus does not support NaN values out of the box.
    """
    def _validate_nanable(self, nanable: Any, field: Any, value: Any) -> Any:
        """
        Test whether the value is nan.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if not nanable and value is np.nan:
            self._error(field, 'Cannot be nan')
