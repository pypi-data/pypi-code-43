from pathlib import Path
from typing import Union, Any
from cerberus import Validator
import pandas as pd
import numpy as np


class Client:
    """
    Base class for clients.
    """
    def get(self, **kwargs: Any) -> Union[list, pd.DataFrame]:
        """
        Get data from remote resource.
        """
        raise NotImplementedError

    def save(self, path: Union[Path, str], **kwargs: Any) -> None:
        """
        Save data to disk.
        """
        raise NotImplementedError


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
            self._error(field, 'Cannot be nan')  # type: ignore
