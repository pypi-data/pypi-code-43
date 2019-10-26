#!/usr/bin/python3

from __future__ import print_function
from array import array
from datetime import datetime
import hashlib
import math
import sys
import re


def clean_dict(d):
    """
    Delete keys with the value ``None`` in a dictionary, recursively.
    This alters the input so you may wish to ``copy`` the dict first.
    :param d: dictionary to clean
    :type d: dict
    """
    if sys.version_info[0] < 3:
        for key, value in d.items():
            if value is None:
                del d[key]
            elif isinstance(value, dict):
                clean_dict(value)
    else:
        for key, value in list(d.items()):
            if value is None:
                del d[key]
            elif isinstance(value, dict):
                clean_dict(value)
    return d


def get_epoch_timestamp(date=None, millis=False):
    """
    Get date in epoch format
    :param date: datetime to convert. Default: utcnow():
    :type date: datetime
    :param millis: epoch with milliseconds or not
    :type millis: bool
    :return: Datetime in epoch format [Integer]
    """
    factor = 1
    if millis:
        factor *= 1000

    utc_now = date if date else datetime.utcnow()
    epoch = datetime.utcfromtimestamp(0)

    return int((utc_now - epoch).total_seconds() * factor)


class CobolDataField:
    DATA_TYPES_SEP = '-+|V+|\.+'
    DECIMAL_SEP = ','

    def __init__(self, name, pic_type, is_sensible=False, decimal_sep=None):
        """
        Constructor
        :param name: field name
        :type name: str
        :param pic_type: PIC data type
        :type pic_type: str
        :param is_sensible: indicates if the field is sensible. If yes, the value is anonymized. Default: False
        :type is_sensible: bool
        :param decimal_sep: character used as decimal separator. Default: ,
        :type decimal_sep: str
        """
        self.name = re.sub('-+|\s+|\.+', '_', name).lower()
        self.pic_type = pic_type.upper()
        self.type = 'NA'
        self.is_signed = self.pic_type.startswith('S')
        self.is_packed = 'COMP-3' in self.pic_type
        self.is_sensible = is_sensible or False
        self.decimal_sep = (decimal_sep or self.DECIMAL_SEP).encode('UTF-8')

        # implicit decimals
        self.has_implicit_decimal = 'V' in self.pic_type
        decimal_part = self.pic_type.split('V')[1] if self.has_implicit_decimal else ''

        if decimal_part:
            if re.match('^S9$|^S99+$|^9$|^99+', decimal_part):
                self.decimal_places = decimal_part.count('9')
            else:
                r = re.match('9\((\d*)\)', decimal_part)
                if r:
                    self.decimal_places = int(r.group(1) or r.group(2))
                else:
                    self.decimal_places = 0
        else:
            self.decimal_places = 0

        self.unpacked_long = self._get_long(self.pic_type if not self.is_packed else self.pic_type[:self.pic_type.find('COMP-3')].strip())
        self.long = self.unpacked_long if not self.is_packed else math.ceil((self.unpacked_long + 1) / 2)

    def convert(self, value, keep_length=True, unpack=True):
        """
        Convert value
        :param unpack: indicates if the value should be unpacked or not. Default: True
        :type unpack: bool
        :param keep_length: indicates if the value must to keep its length after conversion
        :type keep_length: bool
        :param value: value to be converted
        :type value: str
        :return: value converted
        """
        # anonymize
        if self.is_sensible:
            value = self._anonymize_value(value=value, length=self.long)

        if self.type == 'number':
            # unpack number
            if self.is_packed and unpack:
                value = self._unpack_value(value)

                # decimal places
                if self.decimal_places > 0:
                    if not keep_length:
                        if self.has_implicit_decimal:
                            if (len(value) - 1) > self.decimal_places:
                                value = value[:(len(value) - self.decimal_places)] + self.decimal_sep + value[(len(value) - self.decimal_places):]
                    else:
                        value = value.strip().zfill(self.unpacked_long + 1)

                else:
                    if keep_length:
                        value = value.strip().zfill(self.unpacked_long + 1)
        else:
            # strip value
            if not keep_length:
                value = value.strip()

        return value

    @staticmethod
    def _unpack_value(value, comp='COMP-3'):
        """
        Unpack a COMP-3 number
        :param value: valued to be unpacked
        :type value: str
        :param comp: comp type. Default: COMP-3
        :return: value unpacked
        """
        if comp.upper() == 'COMP-3':
            a = array('B', value)
            if not a:
                return ''
            v = float(0)

            # for all but last digit (half byte)
            for i in a[:-1]:
                v = (v * 100) + (((i & 0xf0) >> 4) * 10) + (i & 0xf)

            # last digit
            i = a[-1]
            v = (v * 10) + ((i & 0xf0) >> 4)

            # negative/positve check.
            if (i & 0xf) == 0xd:
                v = -v

            return (str(int(v)) if v < 0 else '+' + str(int(v))).encode('UTF-8')

    @staticmethod
    def _anonymize_value(value, length=None):
        """
        Anonymize sensible value
        :param value: value to be anonymized
        :type value: str
        :param length: length of the value
        :type length: int
        :return: value hashed with the length desired
        """
        value_hashed = hashlib.sha256(value).hexdigest()
        if length:
            if length > len(value_hashed):
                value_hashed = value_hashed.ljust(length)
            else:
                value_hashed = value_hashed[:length]

        return value_hashed.encode('UTF-8')

    def _get_long(self, pic_type):
        """
        Get data type long in bytes
        :param pic_type: PIC data type
        :type pic_type: str
        :return: long of the PIC data type
        """
        pic_type = pic_type.upper()
        types_splitted = re.split(self.DATA_TYPES_SEP, pic_type)

        if len(types_splitted) == 1:
            # empty string
            if types_splitted[0] == '':
                self.type = 'string'
                return 1

            # string by extension
            if re.match('^X$|^XX+$', types_splitted[0]):
                self.type = 'string'
                return types_splitted[0].count('X')

            # string by compression
            r = re.match('X\((\d*)\)', types_splitted[0])
            if r:
                self.type = 'string'
                return int(r.group(1))

            # number by extension
            if re.match('^S9$|^S99+$|^9$|^99+$', types_splitted[0]):
                long = types_splitted[0].count('9')
                # if types_splitted[0].startswith('S'):
                #     long += 1
                self.type = 'number'
                return types_splitted[0].count('9')

            # number by compression
            r = re.match('9\((\d*)\)|S9\((\d*)\)', types_splitted[0])
            if r:
                self.type = 'number'
                return int(r.group(1) or r.group(2))
        else:
            tail_type = pic_type[len(types_splitted[0]) + 1:]

            head_long = self._get_long(types_splitted[0])
            tail_long = self._get_long(tail_type)
            extra_long = 0 if pic_type[len(types_splitted[0])] == 'V' else 1

            return head_long + tail_long + extra_long

    def __repr__(self):
        """
        String representation
        :return: object string representation
        """
        return "DataField(name='{}', " \
               "data_type='{}', " \
               "pic_type='{}', " \
               "long={}, " \
               "unpacked_long={}, " \
               "signed={}, " \
               "is_packed={}, " \
               "is_sensible={}, " \
               "has_implicit_decimal={}, " \
               "decimal_places={})".format(self.name,
                                           self.pic_type,
                                           self.type,
                                           self.long,
                                           self.unpacked_long,
                                           self.is_signed,
                                           self.is_packed,
                                           self.is_sensible,
                                           self.has_implicit_decimal,
                                           self.decimal_places)
