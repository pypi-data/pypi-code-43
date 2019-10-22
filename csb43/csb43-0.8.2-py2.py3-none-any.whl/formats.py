# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from .i18n import tr as _
from .utils import messages as msg
from . import utils
from .utils.compat import m3_unicode

import json
import warnings


class FormatWarning(UserWarning):
    pass


_ABSTRACT_HEADER = (
    msg.T_BANK_CODE,
    msg.T_BRANCH_CODE,
    msg.T_ACCOUNT_KEY,
    msg.T_ACCOUNT_NUMBER,
    msg.T_INFORMATION_MODE,
    msg.T_SHORT_NAME,
    msg.T_CURRENCY,
    msg.T_INITIAL_DATE,
    msg.T_FINAL_DATE,
    msg.T_INITIAL_BALANCE,
    msg.T_FINAL_BALANCE,
    msg.T_INCOME,
    msg.T_EXPENSES,
    msg.T_INCOME_ENTRIES,
    msg.T_EXPENSES_ENTRIES
)


_TRANSACTION_HEADER = (
    msg.T_BRANCH_CODE,
    msg.T_DOCUMENT_NUMBER,
    msg.T_SHARED_ITEM,
    msg.T_OWN_ITEM,
    msg.T_ITEM_1,
    msg.T_ITEM_2,
    msg.T_REFERENCE_1,
    msg.T_REFERENCE_2,
    msg.T_TRANSACTION_DATE,
    msg.T_VALUE_DATE,
    msg.T_AMOUNT,
    msg.T_ORIGINAL_CURRENCY,
    msg.T_ORIGINAL_AMOUNT
)


def _abstractRow(ac):
    return (
        ac.bankCode,
        ac.branchCode,
        ac.get_account_key(),
        ac.accountNumber,
        ac.informationMode,
        ac.shortName,
        ac.currency.alpha_3,
        m3_unicode(ac.initialDate),
        m3_unicode(ac.finalDate),
        ac.initialBalance,
        ac.abstract.balance,
        ac.abstract.income,
        ac.abstract.expense,
        ac.abstract.incomeEntries,
        ac.abstract.expenseEntries
    )


def _transactionRow(t, decimal_fallback):

    name = ", ".join(x.item1.rstrip(' ') for x in t.optionalItems)

    extdname = ", ".join(x.item2.rstrip(' ') for x in t.optionalItems)

    if t.exchange:
        o_currency = utils.export_currency_code(t.exchange.sourceCurrency)
        o_amount = utils.export_decimal(t.exchange.amount, fallback=decimal_fallback)
    else:
        o_currency = None
        o_amount = None

    return (
        t.branchCode,
        t.documentNumber,
        t.sharedItem,
        t.ownItem,
        name,
        extdname,
        t.reference1,
        t.reference2,
        utils.export_date(t.transactionDate),
        utils.export_date(t.valueDate),
        t.amount,
        o_currency or '',
        o_amount or ''
    )


try:
    import tablib
    #: formats supported by :mod:`tablib`
    TABLIB_FORMATS = [f.title for f in tablib.formats.available]
except ImportError:
    TABLIB_FORMATS = []
    warnings.warn(
        _("Package 'tablib' not found. Formats provided by 'tablib' will not be available."), 
        FormatWarning
    )

#: dictionary formats
DICT_FORMATS = ['json']
try:
    import yaml
    DICT_FORMATS.append('yaml')
except ImportError:
    warnings.warn(
        _("Package 'yaml' not found. Hierarchical YAML format will not be available."), 
        FormatWarning
    )

#: available formats
FORMATS = list(set(TABLIB_FORMATS + DICT_FORMATS))


DECIMAL_SUPPORTED = [
    "ods",
    "xls",
    "xlsx",
    "csv",
    "tsv",
    "df",
    "html",
    "latex",
]


def convertFromCsb(csb, expectedFormat, decimal_fallback=None):
    '''
    Convert a File file into an :mod:`tablib` data object or a \
    dictionary-like object

    :param csb: a csb file
    :type  csb: :class:`csb43.csb43.File`
    :param decimal_fallback: decimal number fallback representation:

    - 'float': use type `float`
    - 'str': represent decimal as a string
    - `None`: use default fallback ('str')

    :rtype: :class:`tablib.Databook`, :class:`tablib.Dataset` or a object \
    with an attribute named as `expectedFormat`
    '''
    decimal_supported = expectedFormat in DECIMAL_SUPPORTED
    d_conversion = decimal_fallback or 'str'
    if decimal_supported:
        d_conversion = None

    if expectedFormat in DICT_FORMATS:
        return convertFromCsb2Dict(csb, expectedFormat, decimal_fallback=d_conversion)
    else:
        return convertFromCsb2Tabular(csb, expectedFormat, decimal_fallback=d_conversion)


class _TablibSurrogate(object):

    def __init__(self, string, expectedFormat):
        setattr(self, expectedFormat, string)


def convertFromCsb2Dict(csb, expectedFormat='json', decimal_fallback=None):
    '''
    Convert from `CSB43` to a dictionary format

    :param csb: a csb file
    :type  csb: :class:`csb43.csb43.File`
    :param decimal_fallback: decimal number fallback representation

    :rtype: a object with an attribute named as `expectedFormat`

    :raises: :class:`csb43.utils.Csb43Exception` when the format is unknown \
    or unsupported

    >>> from csb43.csb43 import File
    >>> import csb43.formats as formats
    >>> f = File()
    >>> o = formats.convertFromCsb2Dict(f, 'yaml')
    >>> print(o.yaml)
    cuentas: []
    <BLANKLINE>


    >>> o = formats.convertFromCsb2Dict(f, 'json')
    >>> print(o.json)
    {
     "cuentas": []
    }

    '''
    csb_dict = csb.as_dict(decimal_fallback=decimal_fallback)

    if expectedFormat == 'yaml':
        return _TablibSurrogate(yaml.safe_dump(csb_dict), expectedFormat)
    elif expectedFormat == 'json':
        return _TablibSurrogate(
            json.dumps(csb_dict, indent=1, sort_keys=True),
            expectedFormat
        )
    else:
        utils.raiseCsb43Exception(
            _("unexpected format %s") % expectedFormat, True)


def convertFromCsb2Tabular(csb, expectedFormat='ods', decimal_fallback=None):
    '''
    Convert a File file into an :mod:`tablib` data object

    :param csb: a csb file
    :type  csb: :class:`csb43.csb43.File`
    :param decimal_fallback: decimal number fallback representation

    :rtype: :class:`tablib.Databook` or :class:`tablib.Dataset`

    '''
    datasets = []

    accountsAbstract = tablib.Dataset()

    accountsAbstract.title = _("Accounts")
    accountsAbstract.headers = _ABSTRACT_HEADER

    datasets.append(accountsAbstract)

    for ac in csb.accounts:

        accountId = (
            ac.bankCode,
            ac.branchCode,
            ac.get_account_key(),
            ac.accountNumber
        )

        accountsAbstract.append(_abstractRow(ac))

        tList = tablib.Dataset()
        tList.title = '-'.join(accountId)

        tList.headers = _TRANSACTION_HEADER

        for t in ac.transactions:
            tList.append(_transactionRow(t, decimal_fallback))

        datasets.append(tList)

    book = tablib.Databook(datasets)

    if hasattr(book, expectedFormat):
        return book

    dataset = tablib.Dataset()

    dataset.title = _("Transactions")
    dataset.headers = _ABSTRACT_HEADER + _TRANSACTION_HEADER

    for ac in csb.accounts:

        accountAbstract = _abstractRow(ac)

        for t in ac.transactions:
            dataset.append(accountAbstract + _transactionRow(t, decimal_fallback))

    return dataset
