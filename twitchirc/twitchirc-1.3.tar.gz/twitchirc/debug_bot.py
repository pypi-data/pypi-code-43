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
import fcntl
import os
import socket
import sys
import typing
from typing import Any

import mmw
import twitchirc


def _get_all_chars_from_stdin():
    flags = fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL)
    fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, flags | os.O_NONBLOCK)
    chars = ''
    try:
        chars = sys.stdin.read(10)
    except TypeError:  # Happens in some weird cases
        pass
    finally:
        fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, flags)
        return chars


def input_getch(prompt='>>>', max_bytes=-1):
    data = ''
    screen = mmw.Screen()
    print(prompt, end='', flush=True)

    while 1:
        key = screen.get_char()
        if key == '\033':
            key += _get_all_chars_from_stdin()
        key = mmw.decode(key)
        if key == mmw.BACKSPACE:
            data = data[:-1]
            print(f'\n\033[A\033[2K{prompt}{data}', end='', flush=True)
        elif key == mmw.END:
            exit()
        elif key == mmw.RETURN:
            print(f'\n\033[A\033[2K(sent) {data}')
            return data
        elif len(key) == 1:
            data += key
            print(f'\n\033[A\033[2K{prompt}{data}', end='', flush=True)
        else:
            print(f'Unbound key: {key!r}')
        if max_bytes != -1:
            current_bytes = len(bytes(data, 'utf-8'))
            if current_bytes >= max_bytes:
                return data


class EmulatedConnection(socket.socket):

    # noinspection PyMissingConstructor
    def __init__(self, input_func, output_func=print) -> None:
        self.output_func = output_func
        self.input_func = input_func

    def close(self) -> None:
        self.output_func('**EMULATED CONNECTION CLOSED**')

    def getpeername(self) -> Any:
        return 'localhost', -1

    def getsockname(self) -> Any:
        return 'localhost', -1

    def recv(self, bufsize: int, flags: int = ...) -> bytes:
        return bytes(self.input_func(f'[{bufsize} bytes]>>>', bufsize), 'utf-8')

    def send(self, data: bytes, flags: int = ...) -> int:
        print('(emucon)', repr(str(data, 'utf-8', errors='ignore')))
        return len(data)
        # return super().send(data, flags)


# return super().recv(bufsize, flags)


class DebugBot(twitchirc.Bot):
    def _select_socket(self):
        return True
    def __init__(self, address, username: str, password: typing.Union[str, None] = None, port: int = 6667,
                 no_connect=True, storage=None, no_atexit=False):
        super().__init__(address, username, password, port, no_connect, storage, no_atexit)
        self.socket = EmulatedConnection(input_getch)
