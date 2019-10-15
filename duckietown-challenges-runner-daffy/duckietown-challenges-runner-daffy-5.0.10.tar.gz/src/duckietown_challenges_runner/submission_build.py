# coding=utf-8
import subprocess
from collections import namedtuple

BuiltSub = namedtuple("BuildSub", "image_digest")


def build_image(client, path, tag, dockerfile, no_build, no_cache=False):
    if not no_build:
        cmd = ["docker", "build", "--pull", "-t", tag, "-f", dockerfile]
        if no_cache:
            cmd.append("--no-cache")
        cmd.append(path)
        subprocess.check_call(cmd)

    image = client.images.get(tag)
    return image
