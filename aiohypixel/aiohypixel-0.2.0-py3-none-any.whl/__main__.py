#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © Tmpod 2019
#
# This file is part of aiohypixel.
#
# aiohypixel is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# aiohypixel is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with aiohypixel. If not, see <https://www.gnu.org/licenses/>.
"""
This is just a little *crude* interface for the wrapper.
"""

from .session import HypixelSession
import logging, asyncio, sys
from shutil import get_terminal_size

WIN_SIZE = get_terminal_size()


def fmtp(s: str) -> str:
    """Just prints the string with a little delimiter around it"""
    ndash = ("-" * (len(s) - 2)) if len(s) <= WIN_SIZE.columns else "-" * (WIN_SIZE.columns - 2)
    print(f"\n<{ndash}>\n{s}\n<{ndash}>\n")


try:
    API_KEY = sys.argv[1]
except IndexError:
    fmtp("You must provide an API key!")
else:
    try:
        REQUEST_TYPE = sys.argv[2]
    except IndexError:
        fmtp("You must provide a get method!")
    else:
        logging.basicConfig(level="DEBUG")

        try:
            QUERY = sys.argv[3]
        except IndexError:
            QUERY = None

        async def main(request_type: str, query: str = None) -> None:
            session = await HypixelSession(API_KEY)

            try:
                if query is None:
                    fmtp(str(await (getattr(session, f"get_{request_type}"))()))
                    return

                fmtp(str(await (getattr(session, f"get_{request_type}"))(query)))

            except AttributeError:
                fmtp("Invalid!")

        asyncio.get_event_loop().run_until_complete(main(REQUEST_TYPE, QUERY))
