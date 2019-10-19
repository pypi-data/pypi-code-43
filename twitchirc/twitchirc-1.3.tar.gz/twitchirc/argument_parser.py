#  Library to make crating bots for Twitch chat easier.
#  Copyright (c) 2019 Maciej Marciniak
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import typing


class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, *a, message_handler=lambda *a: None, **kw):
        super().__init__(*a, **kw)
        self.message_handler = message_handler

    def parse_args(self, args: typing.Optional[typing.Sequence[str]] = None,
                   namespace: typing.Optional[argparse.Namespace] = None) -> typing.Optional[argparse.Namespace]:
        try:
            return super().parse_args(args, namespace)
        except SystemExit:
            return

    def _print_message(self, message: str, file: typing.Optional[typing.IO[str]] = None) -> None:
        self.message_handler(message.rstrip('\n'))
