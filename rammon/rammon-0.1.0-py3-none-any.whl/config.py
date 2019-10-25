import os.path
import json
import warnings
from dataclasses import dataclass, field, asdict

__all__ = ["RammonConfig", "config", "CONFIG_PATH", "RAMMON_PATH"]

CONFIG_PATH = os.path.expanduser("~/.rammon/config.json")
RAMMON_PATH = os.path.dirname(CONFIG_PATH)

os.umask(0o077)
if not os.path.exists(RAMMON_PATH):
    os.makedirs(RAMMON_PATH)


@dataclass
class RammonConfig:
    WARNING_PERCENT_USED: float = field(default=80)
    CRITICAL_PERCENT_USED: float = field(default=95)
    SNOOZE_DURATION_SECONDS: int = field(default=300)
    POLL_PERIOD_SECONDS: int = field(default=10)
    NOTIFICATION_TIMEOUT_MS: int = field(default=0)  # 0 for no timeout

    def persist(self):
        with open(CONFIG_PATH, "w") as savefd:
            json.dump(asdict(self), savefd, indent=2)


config: RammonConfig
try:
    with open(CONFIG_PATH, "r") as loadfd:
        config_dict = json.load(loadfd)
        if not isinstance(config_dict, dict):
            raise json.JSONDecodeError
        config = RammonConfig(**config_dict)

except FileNotFoundError:
    config = RammonConfig()

except TypeError as e:
    warnings.warn(f"Unrecognized keys found in {CONFIG_PATH!r}. Reverting to defaults.")
    config = RammonConfig()

except json.JSONDecodeError:
    warnings.warn(
        f"Invalid JSON Dictionary found in {CONFIG_PATH!r}. Reverting to defaults."
    )
    config = RammonConfig()
