import re

PATTERN = re.compile("\d+\.\d+\.\d+")


def read_setup(file: str) -> str:
    with open(file, encoding='utf-8', mode='r') as f:
        return f.read()


def update_version(file: str, version: str):
    subbed = PATTERN.sub(version, read_setup(file))
    with open(file, encoding='utf-8', mode='w') as fl:
        fl.write(subbed)


def current_version(file: str):
    return PATTERN.findall(read_setup(file))
