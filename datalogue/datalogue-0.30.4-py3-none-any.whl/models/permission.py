from typing import Union

from datalogue.errors import DtlError, _enum_parse_error
from datalogue.utils import SerializableStringEnum


class Permission(SerializableStringEnum):
    Write = "Write"
    Use = "Use"
    Read = "Read"
    # in Yggy None is the NonPermission value for no access
    NoPermission = "None"

    @staticmethod
    def parse_error(s: str) -> str:
        return DtlError(_enum_parse_error("permission type", s))

    @staticmethod
    def permission_from_str(string: str) -> Union[DtlError, 'Permission']:
        return SerializableStringEnum.from_str(Permission)(string)