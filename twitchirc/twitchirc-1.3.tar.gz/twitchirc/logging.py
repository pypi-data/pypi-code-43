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

import datetime
import os
import re
import time

quiet = False
log_file = None
log_file_name = ''
log_file_counter = 0
log_start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
log_rotate_delay = 1 * 24 * 60 * 60
# 1 day
# * 24 hours
# * 60 minutes
# * 60 seconds
log_rotate_timestamp = time.time() + log_rotate_delay
DISPLAY_LOG_LEVELS = {
    'info': 'info',
    'warn': 'warn',
    'err': 'err',
    'debug': 'debug'
}
LOG_FORMAT = '[{time}] [{level}] {message}\n'


def remove_other_logs():
    n = log_file_name.replace(".", "\\.")
    pat = re.compile(rf'{n}\.[0-9]+')
    p = os.path.dirname(log_file_name)
    for i in os.listdir('.' if p == '' else p):
        m = re.match(pat, i)
        if m:
            os.unlink(os.path.join(p, i))
            continue


def enable_file_logging(filename: str, delay=1 * 24 * 60 * 60):
    global log_file, log_file_name, log_rotate_timestamp, log_rotate_delay
    log_file_name = filename
    remove_other_logs()
    log_file = open(filename, 'w')
    log_rotate_delay = delay
    log_rotate_timestamp = time.time() + log_rotate_delay
    write_log_message()


def write_log_message():
    log_file.write(f'/*\n')
    log_file.write(f' * {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
    log_file.write(f' * Log file {log_file_name!r} (will be moved to {f"{log_file_name}.{log_file_counter}"!r})\n')
    log_file.write(f' * Program started on {log_start_time}\n')
    log_file.write(' */\n')
    log_file.flush()


def rotate_logs():
    global log_rotate_timestamp, log_file, log_file_counter
    log_rotate_timestamp = time.time() + log_rotate_delay
    if log_file is not None:
        log_file.close()
        new_name = log_file_name + '.' + str(log_file_counter)

        os.rename(log_file_name, new_name)
        log_file_counter += 1
        log_file = open(log_file_name, 'w')
        write_log_message()


def log(level: str, *message: str, sep: str = ' '):
    if log_rotate_timestamp <= time.time():
        rotate_logs()
    msg = LOG_FORMAT.format(time=datetime.datetime.now().strftime("%H:%M:%S"),
                            level=DISPLAY_LOG_LEVELS[level],
                            message=sep.join(message))
    if log_file:
        log_file.write(msg)
        log_file.flush()
    if not quiet:
        print(msg, end='', flush=True)


def info(*message: str):
    log('info', *message)


def warn(*message: str):
    log('warn', *message)
