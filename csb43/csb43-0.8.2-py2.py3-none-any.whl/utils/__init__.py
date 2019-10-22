# -*- coding: utf-8 -*-
'''
.. note::

    license: GNU Lesser General Public License v3.0 (see LICENSE)
'''

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import re
import datetime
#import pycountry
import sys
import functools
from decimal import Decimal

from . import compat
from ..i18n import tr as _
from .currency_data import CURRENCY_DATA
import warnings


class Message(compat.BytesMixin):

    def __init__(self, message):
        self.message = message

    def __unicode__(self):
        if compat.m3_is_bytes(self.message):
            return self.message.decode("utf-8")
        return self.message

    def __bytes__(self):
        if compat.m3_is_unicode(self.message):
            return self.message.encode("utf-8")
        return self.message


class Csb43Exception(Message, Exception):
    pass


class Csb43Warning(Message, UserWarning):
    pass


def raiseCsb43Exception(value='', strict=False, silent=False, line=None, **kwargs):
    '''
    raise a :class:`Csb43Exception` or print the exception's message to \
    standard error

    :param value: message of the exception
    :param strict: print to standard error instead of raising an exception if \
    not `strict`

    :raises: :class:`Csb43Exception`
    '''
    #exc = Csb43Exception(value)
    if line is not None:
        value = "[%04d] %s" % (line, value)
    if strict:
        raise Csb43Exception(value)
    elif not silent:
        warnings.warn(Csb43Warning(value))


def check_string(pattern='', field='', strict=True, **csbexc):
    '''
    :param pattern: pattern description using regular expressions
    :type  pattern: :class:`basestring`

    :param field: variable to be checked

    :param strict: treat exceptions as warnings if `False`
    :type  strict: :class:`bool`

    :raises: :class:`Csb43Exception` if `field` doesn't match `pattern` and \
    `strict` is `True`
    '''

    if len(re.findall(pattern, field)) != 1:
        raiseCsb43Exception(
            _("Bad format: content %s mismatches the "
              "expected format r%s for this field"
              ) % (repr(field), repr(pattern)), strict=strict, **csbexc)


def check_strict(pattern):
    """
    .. note::

        decorator

    :param pattern: pattern description using regular expressions
    :type  pattern: :class:`basestring`

    :param field: variable to be checked

    :param strict: treat exceptions as warnings if `False`
    :type  strict: :class:`bool`

    :raises: :class:`Csb43Exception` if `field` doesn't match `pattern` and \
    `strict` is `True`
    """
    def _decorator(f):

        @functools.wraps(f)
        def _wrapped(self, *args, **kw):
            check_string(pattern, *args, **kw)
            return f(self, *args, **kw)

        return _wrapped

    return _decorator


DECIMAL = 2
DATEFORMAT = ["%d%m%y", "%y%m%d"]


def raw2currency(value, decimal=DECIMAL, debit='2'):
    '''
    Format the CSB composite type for amounts as a real number

    Args:
        value (long or str) -- absolute amount without decimal separator
        decimal (int)       -- number of digits reserved for decimal numbers
        debit ('1','2')     -- '1' debit, '2' credit

    Return:
        (float) the amount as a real number

    Examples:

    >>> raw2currency('123456')
    Decimal('1234.56')
    >>> raw2currency('12345',debit='1')
    Decimal('-123.45')

    '''
    val = -compat.m3_long(value) if int(debit) == 1 else compat.m3_long(value)
    return (Decimal(val) / Decimal(10 ** decimal))


def currency2raw(value, decimal=DECIMAL):
    '''
    Convert a real to the CSB amount format

    Args:
        value (float) -- quantity as a real number
        decimal (int) -- number of digits reserved for decimal numbers

    Return:
        tuple of absolute amount and debit flag

    Examples:

    >>> currency2raw(-123.456)
    (12345, '1')
    >>> currency2raw(123.45)
    (12345, '2')
    '''
    return (abs(compat.m3_long(value * (10 ** decimal))),
            '1' if value < 0 else '2')


def raw2date(value, yearFirst=True):
    '''
    Convert the CSB date format to a datetime.date object

    Args:
        value (str)      -- date using the CSB format
        yearFirst (bool) -- if *False*, consider the CSB format is DDMMYY \
            instead of YYMMDD

    Return:
        (datetime.date) the date object

    Examples:

    >>> raw2date('020301')
    datetime.date(2002, 3, 1)
    '''
    f = DATEFORMAT[1] if yearFirst else DATEFORMAT[0]
    return datetime.datetime.strptime(value, f).date()


def date2raw(value, yearFirst=True):
    '''
    Convert a datetime.date / datetime.datetime object to a CSB formatted date

    Args:
        value (datetime.datetime, datetime.date) -- datetime object
        yearFirst (bool) -- if *False*, consider the CSB format is DDMMYY \
            instead of YYMMDD

    Return:
        (str) the CSB date

    Examples:

    >>> a = raw2date('020301')
    >>> date2raw(a)
    '020301'
    '''
    if isinstance(value, (datetime.datetime, datetime.date)):
        f = DATEFORMAT[1] if yearFirst else DATEFORMAT[0]
        return value.strftime(f)
    else:
        raise Csb43Exception(_("instance of datetime or date expected, but "
                               "'%s' found") % type(value))


class CurrencyLite(object):

    def __init__(self, alpha_3, numeric):
        self.alpha_3 = alpha_3
        self.numeric = numeric


__CUR_LETTER = {}
__CUR_NUMERIC = {}

for el in CURRENCY_DATA:
    __tmp = CurrencyLite(el[0], el[1])
    if el[0]:
        __CUR_LETTER[el[0]] = __tmp
    if el[1]:
        __CUR_NUMERIC[el[1]] = __tmp


def currencyISO(numeric):
    '''
    :param code: a ISO 4217 numeric code
    :type  code: :class:`str`
    :rtype: :class:`pycountry.db.Currency` object from its numeric code
    '''
    if hasattr(sys, 'frozen'):
        return __CUR_NUMERIC[numeric]
    else:
        import pycountry
        return pycountry.currencies.get(numeric=numeric)


def currencyISOByLetter(alpha_3):
    '''
    :param code: a ISO 4217 numeric code
    :type  code: :class:`str`
    :rtype: :class:`pycountry.db.Currency` object from its numeric code
    '''
    if hasattr(sys, 'frozen'):
        return __CUR_LETTER[alpha_3]
    else:
        import pycountry
        return pycountry.currencies.get(alpha_3=alpha_3)


def isCurrency(obj):
    if hasattr(sys, 'frozen'):
        return isinstance(obj, CurrencyLite)
    else:
        import pycountry
        return isinstance(obj, pycountry.db.Data)


def b_left_pad(bvalue, n, fill=b' '):
    return fill * (n - len(bvalue)) + bvalue


def b_right_pad(bvalue, n, fill=b' '):
    return bvalue + fill * (n - len(bvalue))


def nullable(f):
    @functools.wraps(f)
    def wrapper(value, *args, **kwds):
        if value is None:
            return value
        return f(value, *args, **kwds)
    return wrapper


# items
CONCEPTOS = {
    '01': "TALONES - REINTEGROS",
    '02': "ABONARES - ENTREGAS - INGRESOS",
    '03': "DOMICILIADOS - RECIBOS - LETRAS - PAGOS POR SU CUENTA",
    '04': "GIROS - TRANSFERENCIAS - TRASPASOS - CHEQUES",
    '05': "AMORTIZACIONES, PRESTAMOS, CREDITOS, ETC.",
    '06': "REMESAS, EFECTOS",
    '07': "SUSCRIPCIONES - DIV. PASIVOS - CANJES",
    '08': "DIV. CUPONES - PRIMA JUNTA - AMORTIZACIONES",
    '09': "OPERACIONES DE BOLSA Y/O COMPRA/VENTA VALORES",
    '10': "CHEQUES GASOLINA",
    '11': "CAJERO AUTOMATICO",
    '12': "TARJETAS DE CREDITO - TARJETAS DE DEBITO",
    '13': "OPERACIONES EXTRANJERO",
    '14': "DEVOLUCIONES E IMPAGADOS",
    '15': "NOMINAS - SEGUROS SOCIALES",
    '16': "TIMBRES - CORRETAJE - POLIZA",
    '17': "INTERESES - COMISIONES - CUSTODIA - GASTOS E IMPUESTOS",
    '98': "ANULACIONES - CORRECCIONES ASIENTO",
    '99': "VARIOS"
}


@nullable
def export_date(value):
    return compat.m3_unicode(value)


@nullable
def export_currency_code(value):
    return compat.m3_unicode(value.alpha_3)


@nullable
def export_decimal(value, fallback=None):
    if fallback == "float":
        return float(value)
    elif fallback == "str":
        return compat.m3_unicode(value)
    elif fallback:
        raise ValueError("fallback=%r" % fallback)
    return value
