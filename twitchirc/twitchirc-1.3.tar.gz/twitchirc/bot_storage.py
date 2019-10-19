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

import copy
import json
import os

import twitchirc


class AmbiguousSaveError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __repr__(self):
        return f'AmbiguousSaveError({self.msg!r})'

    def __str__(self):
        return f'AmbiguousSaveError: {self.msg}'


class CannotLoadError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __repr__(self):
        return f'CannotLoadError({self.msg!r})'

    def __str__(self):
        return f'CannotLoadError: {self.msg}'


class Storage:
    def __init__(self, auto_save=False):
        self.data = {}
        self.auto_save = auto_save

    def _load(self):
        return {}

    def _save(self):
        pass

    def load(self):
        self.data = self._load()
        return self.data

    def save(self, is_auto_save=False):
        if is_auto_save and not self.auto_save:
            return
        self._save()

    def __repr__(self):
        return f'twitchirc.Storage(auto_save={self.auto_save})'

    def __str__(self):
        return '<Storage>'

    def __getitem__(self, item):
        return self.data.__getitem__(item)

    def __setitem__(self, key, value):
        self.data.__setitem__(key, value)
        self.save(is_auto_save=True)


class JsonStorage(Storage):
    def __repr__(self):
        return f'twitchirc.JsonStorage(file={self.file}, auto_save={self.auto_save})'

    def __str__(self):
        return '<JsonStorage>'

    def __init__(self, file: str, auto_save=False, default=None):
        super().__init__(auto_save)
        if default is None:
            default = {}

        self.file = os.path.abspath(file)
        try:
            twitchirc.info(f'Reading file {self.file}')
            self.load()
        except (CannotLoadError, json.decoder.JSONDecodeError) as e:
            twitchirc.warn(f'Failed to load JsonStorage: {e}')
            self.data = default

    def _load(self):
        if not os.path.isfile(self.file):
            raise CannotLoadError(f'Target path {self.file!r} is not a file.')
        with open(self.file, 'r') as f:
            data = json.load(f)
        self._old_data = copy.deepcopy(data)
        return data

    def _save(self):
        twitchirc.log('debug', f'Saving file {self.file!r}')
        try:
            with open(self.file, 'r') as f:
                try:
                    file_data = json.load(f)
                except json.decoder.JSONDecodeError:
                    pass
                else:
                    if file_data != self._old_data:
                        raise AmbiguousSaveError('Data in file on disk has changed.')
        except FileNotFoundError:
            pass
        with open(self.file, 'w') as f:
            json.dump(self.data, f)
        self._old_data = copy.deepcopy(self.data)
        twitchirc.log('debug', f'Saved file {self.file!r}')
