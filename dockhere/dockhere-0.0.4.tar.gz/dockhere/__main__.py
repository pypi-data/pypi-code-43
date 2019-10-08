"""
Run a command in docker in the current folder using a bind mount
"""
import argparse
import os
import sys

from . import docker

parser = argparse.ArgumentParser(
    prog="dockhere",
    description="Run a docker container in the current directory almost as though it was just a shell"
)
parser.add_argument("--entrypoint",
                    help="Override the container entrypoint")
parser.add_argument("-i", default=True, action="store_true", dest="interactive",
                    help="Make the container interactive (docker exec -i)")
parser.add_argument("-n", default=True, action="store_false", dest="interactive",
                    help="Make the container non-interactive (opposite of -i)")
parser.add_argument("-e", metavar="ENV", action="append", dest="ENV",
                    help="Add docker environment variables (passed to docker run)")
parser.add_argument("--priv", default=False, action="store_true",
                    help="Run docker with --privileged")
parser.add_argument("--root", default=False, action="store_true",
                    help="Run as root inside the container")
parser.add_argument("--bamboo", default=False, action="store_true",
                    help="Pass all bamboo_* environment variables to the container")
parser.add_argument("IMAGE", default="busybox:latest",
                    help="Docker image to run (default busybox)", nargs="?")

args, extra = parser.parse_known_args()

if args.bamboo:
    bamboo_vars = []
    for name in os.environ:
        if name.startswith("bamboo_"):
            bamboo_vars.append(name)
    if not args.ENV:
        args.ENV = []
    args.ENV = bamboo_vars + args.ENV


container = docker.Container(args.IMAGE, os.getcwd(), args.ENV, priv=args.priv, root=args.root)
docker_id = container.start()
assert docker_id, "could not start container!"
sys.exit(container.execute(extra, interactive=args.interactive))
