from typing import Tuple, List
from collections import namedtuple

ClientExceptionResult = namedtuple("ClientExceptionResult", "client exception")
OperationResult = namedtuple("OperationResult", "client result")
BulkOperationResult = Tuple[List[OperationResult], List[ClientExceptionResult]]
