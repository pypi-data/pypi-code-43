#
# Copyright (c) 2019-present, wobe-systems GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# found in the LICENSE file in the root directory of this source tree.
#

""" Brick Runner (application)
"""

import argparse
import asyncio
import signal
import sys

from titanfe.apps.brick_runner.runner import BrickRunner


if "win" in sys.platform:
    # Windows specific event-loop policy
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
else:
    import uvloop  # pylint: disable=import-error

    uvloop.install()


async def run_app(args):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    br = await BrickRunner.create(  # pylint: disable=invalid-name
        args.id, args.controlpeer, args.kafka
    )
    await br.run()


def main():
    """parse args and run the application"""
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-id", type=str, help="Brick Runner ID")  # uuid.UUID,
    arg_parser.add_argument(
        "-controlpeer", type=str, help="ControlPeer input_address as <host>:<port>"
    )
    arg_parser.add_argument("-kafka", type=str, help="Kafka bootstrap servers")

    args = arg_parser.parse_args()

    asyncio.run(run_app(args))


if __name__ == "__main__":
    main()
