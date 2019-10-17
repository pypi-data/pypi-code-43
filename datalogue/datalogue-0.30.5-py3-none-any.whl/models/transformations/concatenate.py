from datalogue.models.transformations.commons import Transformation
from datalogue.utils import _parse_string_list, _parse_list
from datalogue.errors import DtlError, _property_not_found
from typing import List, Union


class ConcatenateAtPaths(Transformation):
    """
    Concatenates the data that reside at specified sibling nodes,
    This operation is performed[ in-place: specified nodes are collapsed to one node containing the result of the concatenation as the value,
    and the same label as in the original.
    """
    type_str = "ConcatenateAtPaths"

    def __init__(self, paths: List[List[str]]):
        """
        Paths --> List of Paths where the data to concatenate resides
        """
        Transformation.__init__(self, ConcatenateAtPaths.type_str)
        self.paths = paths

    def __eq__(self, other: 'ConcatenateAtPaths'):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"ConcatenateAtPaths({self.paths})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["paths"] = self.paths
        return base

    @staticmethod
    def _list_paths_from_payload(value: dict) -> Union[List[List[str]], DtlError]:
        def is_list_of_list():
            return isinstance(value, List) and all(isinstance(item, List) for item in value)
        if value is not None and is_list_of_list():
            return _parse_list(_parse_string_list)(value)

        return DtlError(f"Could not parse operand: {value}")

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'ConcatenateAtPaths']:
        paths = json.get("paths")
        if paths is None:
            return _property_not_found("paths", json)
        paths = ConcatenateAtPaths._list_paths_from_payload(paths)
        if isinstance(paths, DtlError):
            return paths

        return ConcatenateAtPaths(paths)
