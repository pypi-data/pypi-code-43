import os
import random
import json

from dotenv import load_dotenv

load_dotenv()


def random_ua():
    base_dir = os.getenv("BASE_DIR", "/opt/crawlers-monitoramento/bots/")
    lines = open("{}user-agents.txt".format(base_dir), "r").read().splitlines()
    return random.choice(lines)


def dumps(to_dump):
    def dump(obj):
        # try:
        #     return obj.toJSON()
        # except Exception as _:
        return obj.__dict__

    return json.dumps(to_dump, indent=4, default=dump, ensure_ascii=False)


class AtomicCounter:
    def __init__(self):
        self.counter = 0

    def count(self):
        self.counter += 1
        return self.counter
