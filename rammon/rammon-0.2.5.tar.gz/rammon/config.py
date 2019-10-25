import os.path
import json
import warnings
from dataclasses import dataclass, field, asdict

__all__ = [
    "RammonConfig",
    "conf",
    "CONFIG_PATH",
    "RAMMON_PATH",
    "LAUNCHED_FROM_SYSTEMD",
]

CONFIG_PATH = os.path.expanduser("~/.rammon/conf.json")
RAMMON_PATH = os.path.dirname(CONFIG_PATH)
LAUNCHED_FROM_SYSTEMD = os.environ.get("LAUNCHED_FROM_SYSTEMD")
os.umask(0o077)
if not os.path.exists(RAMMON_PATH):
    os.makedirs(RAMMON_PATH)


@dataclass
class RammonConfig:
    WARNING_PERCENT_USED: float = field(default=80.0)
    CRITICAL_PERCENT_USED: float = field(default=95.0)
    SNOOZE_DURATION_SECONDS: int = field(default=300)
    POLL_PERIOD_SECONDS: int = field(default=10)
    NOTIFICATION_TIMEOUT_MS: int = field(default=0)  # 0 for no timeout

    def persist(self):
        with open(CONFIG_PATH, "w") as savefd:
            json.dump(asdict(self), savefd, indent=2)


conf: RammonConfig
try:
    with open(CONFIG_PATH, "r") as loadfd:
        config_dict = json.load(loadfd)
        if not isinstance(config_dict, dict):
            raise json.JSONDecodeError
        conf = RammonConfig(**config_dict)

except FileNotFoundError:
    conf = RammonConfig()

except TypeError as e:
    warnings.warn(
        "Unrecognized keys found in ~/.rammon/conf.json. Reverting to defaults."
    )
    conf = RammonConfig()

except json.JSONDecodeError:
    warnings.warn(
        "Invalid JSON Dictionary found in ~/.rammon/conf.json. Reverting to defaults."
    )
    conf = RammonConfig()
