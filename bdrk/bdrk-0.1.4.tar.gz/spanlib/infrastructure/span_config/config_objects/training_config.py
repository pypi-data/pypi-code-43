from dataclasses import dataclass
from typing import List, Mapping

from spanlib.infrastructure.span_config.config_objects.command import Command


@dataclass(frozen=True)
class TrainingConfig:
    image: str
    install: List[str]
    script_commands: List[Command]
    parameters: Mapping[str, str]
    secret_names: List[str]
