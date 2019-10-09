from dataclasses import dataclass
from typing import List, Mapping, Optional

from spanlib.infrastructure.span_config.config_objects.command import Command


@dataclass(frozen=True)
class FeatureDefinition:
    name: str
    key: str
    description: Optional[str]


@dataclass(frozen=True)
class FeatureConfig:
    image: str
    install: List[str]
    script_commands: List[Command]
    parameters: Mapping[str, str]
    secret_names: List[str]
    feature_definitions: List[FeatureDefinition]
