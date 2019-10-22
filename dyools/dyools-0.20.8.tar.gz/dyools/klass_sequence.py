from __future__ import (absolute_import, division, print_function, unicode_literals)

from datetime import datetime


class Sequence(object):

    def __init__(self,
                 start=1,
                 fill='0',
                 prefix='',
                 prefix_padding=0,
                 prefix_fill='0',
                 suffix='',
                 suffix_padding=0,
                 suffix_fill='0',
                 padding=0,
                 stop=None,
                 step=1
                 ):
        self.prefix = prefix
        self.suffix = suffix
        self.padding = padding
        self.prefix_padding = prefix_padding
        self.suffix_padding = suffix_padding
        self.step = step
        self.stop = stop
        self.fill = fill
        self.prefix_fill = prefix_fill
        self.suffix_fill = suffix_fill
        self.__is_int = isinstance(start, int) and not suffix and not prefix
        self.char_start = False
        self.char_stop = False
        self.__first_loop = True
        if not self.__is_int:
            start = str(start)
            if len(start) != 1:
                raise ValueError('The start should be one character')
            elif 97 <= ord(start) <= 122:
                self.char_start = 97
                self.char_stop = 122
            elif 65 <= ord(start) <= 90:
                self.char_start = 65
                self.char_stop = 90
            elif 48 <= ord(start) <= 57:
                self.char_start = 48
                self.char_stop = 57
            else:
                raise ValueError('The character should be in [a-z] or [A-Z] or [0-9]')
        self.__value = start

    def next(self):
        if self.__is_int:
            if not self.__first_loop:
                self.__value += self.step
            if not self.stop is None:
                if self.__value > self.stop:
                    self.__value = self.stop
        else:
            i = 0
            v = list(self.__value[::-1])
            if not self.__first_loop:
                while True:
                    if ord(v[i]) + self.step <= self.char_stop:
                        v[i] = chr(ord(v[i]) + self.step)
                        break
                    else:
                        v[i] = chr(self.char_start)
                    i += 1
                    if len(v) == i:
                        v.append(chr(self.char_start))
                        break
            self.__value = ''.join(v[::-1])
            if not self.stop is None:
                if len(self.__value) == len(self.stop) and self.__value > self.stop:
                    self.__value = self.stop
        self.__first_loop = False
        return self._get_value()

    @property
    def value(self):
        if self.__first_loop:
            self.__first_loop = False
        return self._get_value()

    def _get_value(self):
        class Params(dict):
            def __init__(self):
                self.date = datetime.now()

            def __getitem__(self, item):
                return str(getattr(self.date, item))

        params = Params()
        if self.__is_int:
            return self.__value
        else:
            if self.prefix and isinstance(self.prefix, (str, bytes)) and '%' in self.prefix:
                self.prefix = self.prefix % params
            if self.suffix and isinstance(self.suffix, (str, bytes)) and '%' in self.suffix:
                self.suffix = self.suffix % params
            fmt = '{prefix:{prefix_fill}>{prefix_padding}}{value:{fill}>{padding}}{suffix:{suffix_fill}>{suffix_padding}}'
            return fmt.format(
                prefix=self.prefix,
                padding=self.padding,
                value=self.__value,
                suffix=self.suffix,
                fill=self.fill,
                prefix_fill=self.prefix_fill,
                suffix_fill=self.suffix_fill,
                prefix_padding=self.prefix_padding,
                suffix_padding=self.suffix_padding,
            )
