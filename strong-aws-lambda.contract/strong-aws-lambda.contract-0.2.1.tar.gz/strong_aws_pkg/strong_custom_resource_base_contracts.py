from dataclasses import dataclass, field
from enum import Enum
from typing import TypeVar


@dataclass(frozen=True)
class BaseResourceProperties:
    pass


TBaseRequestContract = TypeVar("TBaseRequestContract", bound=BaseResourceProperties)


class StatusResult(Enum):
    Success = 'SUCCESS'
    Failed = 'FAILED'


@dataclass(frozen=True)
class BaseResultContract:
    Status: StatusResult


@dataclass(frozen=True)
class BaseResultErrorContract:
    Status: StatusResult = field(init=False, default=StatusResult.Failed)
    Reason: str


@dataclass(frozen=True)
class AwsRequestContract:
    RequestType: str
    ResponseURL: str
    StackId: str
    ResourceType: str
    LogicalResourceId: str
