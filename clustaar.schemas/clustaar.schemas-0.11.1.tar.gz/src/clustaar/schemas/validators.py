import re
from lupin.validators.match import Match
from lupin.validators.validator import Validator
from lupin.errors import ValidationError


_OBJECT_ID_REGEX = re.compile(r"^[a-z0-9]{24}$", re.I)


class ObjectID(Match):
    """Validate that value conforms the mongoDB objectID format"""

    def __init__(self):
        super().__init__(_OBJECT_ID_REGEX)


class IsRegexp(Validator):
    """Verify that the value is valid regexp"""

    def __call__(self, value, path):
        """Validate that value can be compiled to a regex object

        Args:
            value (str): string to validate
            path (list): error path
        """
        try:
            re.compile(value)
        except Exception:
            raise ValidationError(message="Invalid regular expression", path=path)
