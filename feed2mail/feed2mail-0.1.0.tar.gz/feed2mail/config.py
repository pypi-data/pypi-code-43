import argparse
from datetime import datetime, timezone, timedelta
import json
import os

env = os.environ.get

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--print", action="store_true")
    parser.add_argument("--config-path", default=env("FEED_CONFIG"))
    parser.add_argument("--mail-user", default=env("FEED_MAIL_USER"))
    parser.add_argument("--mail-password", default=env("FEED_MAIL_PASS"))
    parser.add_argument("--mail-host", default=env("FEED_MAIL_HOST"))
    parser.add_argument("--mail-to", default=env("FEED_MAIL_TO"))

    return parser.parse_args()


def save_feeds(path, config, updated_items):
    now = datetime.now(timezone.utc).isoformat()
    for name, time in config.items():
        if name in updated_items:
            config[name] = now
        else:
            config[name] = time.isoformat()

    contents = json.dumps(config, indent=2, sort_keys=True)

    with open(path, 'w+') as f:
        f.write(json.dumps(config, indent=2, sort_keys=True))


def load_feeds(configPath):
    with open(configPath) as f:
        config = {}
        for k,v in json.load(f).items():
            try:
                # Default to old enough that it wont filter out any messages.
                config[k] = (datetime.now(timezone.utc) -
                             timedelta(days=500000))
                if v:
                    config[k] = datetime.fromisoformat(v)
            except ValueError:
                print(f"{k} has invalid date of {v}")
        return config
