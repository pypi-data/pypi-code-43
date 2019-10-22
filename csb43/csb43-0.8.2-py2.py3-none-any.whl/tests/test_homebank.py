
from __future__ import unicode_literals
from __future__ import absolute_import

import unittest

from .. import homebank
from .. import utils
import datetime
import decimal


class TestHomebankTransaction(unittest.TestCase):

    def setUp(self):
        self.tDate = datetime.date(2002, 3, 4)
        self.value = [
            # date
            self.tDate.strftime("%d-%m-%y"),
            # mode
            '2',
            # info
            '3',
            # payee
            '4',
            # description
            '5',
            # amount
            '1.10'
        ]

    def test_init(self):
        try:
            homebank.Transaction()
        except utils.Csb43Exception:
            self.fail("exception not expected")

    def test_init_record(self):

        with self.assertRaises(utils.Csb43Exception):
            homebank.Transaction("1;2")

        with self.assertRaises(utils.Csb43Exception):
            homebank.Transaction(",".join(self.value))

        homebank.Transaction(";".join(self.value))

    def test_properties(self):
        t = homebank.Transaction(";".join(self.value))

        self.assertEqual(self.tDate.year, t.date.year)
        self.assertEqual(self.tDate.month, t.date.month)
        self.assertEqual(self.tDate.day, t.date.day)

        self.assertEqual(2, t.mode)
        self.assertEqual('3', t.info)
        self.assertEqual('4', t.payee)
        self.assertEqual('5', t.description)
        self.assertEqual(decimal.Decimal('1.1'), t.amount)
        self.assertIsNone(t.category)

        value = list(self.value)
        value.append('7')

        t = homebank.Transaction(";".join(value))

        self.assertEqual(self.tDate.year, t.date.year)
        self.assertEqual(self.tDate.month, t.date.month)
        self.assertEqual(self.tDate.day, t.date.day)

        self.assertEqual(2, t.mode)
        self.assertEqual('3', t.info)
        self.assertEqual('4', t.payee)
        self.assertEqual('5', t.description)
        self.assertEqual(decimal.Decimal('1.1'), t.amount)
        self.assertEqual('7', t.category)

        t.mode = '23'
        self.assertEqual(23, t.mode)
        t.mode = 23
        self.assertEqual(23, t.mode)

        t.info = '55'
        self.assertEqual('55', t.info)

        t.payee = 'payee'
        self.assertEqual('payee', t.payee)

        t.description = 'description'
        self.assertEqual('description', t.description)

        with self.assertRaises(decimal.InvalidOperation):
            t.amount = 'amount'

        with self.assertRaises(utils.Csb43Exception):
            t.date = '43'

        try:
            t.date = self.tDate
        except Exception:
            self.fail("exception not expected")

    def test_str(self):
        value = list(self.value)
        value.append('7')
        value = ";".join(value)

        t = homebank.Transaction(value)

        self.assertEqual(value, str(t))
