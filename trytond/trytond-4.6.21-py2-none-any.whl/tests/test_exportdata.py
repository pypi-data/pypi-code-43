# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import sys
try:
    import cdecimal
    if 'decimal' not in sys.modules:
        sys.modules['decimal'] = cdecimal
except ImportError:
    import decimal
    sys.modules['cdecimal'] = decimal
import unittest
from decimal import Decimal
import datetime
from trytond.tests.test_tryton import activate_module, with_transaction
from trytond.pool import Pool


class ExportDataTestCase(unittest.TestCase):
    'Test export_data'

    @classmethod
    def setUpClass(cls):
        activate_module('tests')

    @with_transaction()
    def test_boolean(self):
        'Test export_data boolean'
        pool = Pool()
        ExportData = pool.get('test.export_data')

        export1, = ExportData.create([{
                    'boolean': True,
                    }])
        self.assertEqual(
            ExportData.export_data([export1], ['boolean']), [[True]])

        export2, = ExportData.create([{
                    'boolean': False,
                    }])
        self.assertEqual(
            ExportData.export_data([export2], ['boolean']),
            [[False]])

        self.assertEqual(
            ExportData.export_data([export1, export2],
                ['boolean']),
            [[True], [False]])

    @with_transaction()
    def test_integer(self):
        'Test export_data integer'
        pool = Pool()
        ExportData = pool.get('test.export_data')

        export1, = ExportData.create([{
                    'integer': 2,
                    }])
        self.assertEqual(
            ExportData.export_data([export1], ['integer']), [[2]])

        export2, = ExportData.create([{
                    'integer': 0,
                    }])
        self.assertEqual(
            ExportData.export_data([export2], ['integer']), [[0]])

        self.assertEqual(
            ExportData.export_data([export1, export2], ['integer']),
            [[2], [0]])

    @with_transaction()
    def test_float(self):
        'Test export_data float'
        pool = Pool()
        ExportData = pool.get('test.export_data')

        export1, = ExportData.create([{
                    'float': 1.1,
                    }])
        self.assertEqual(
            ExportData.export_data([export1], ['float']), [[1.1]])

        export2, = ExportData.create([{
                    'float': 0,
                    }])
        self.assertEqual(
            ExportData.export_data([export2], ['float']), [[0]])

        self.assertEqual(
            ExportData.export_data([export1, export2], ['float']),
            [[1.1], [0]])

    @with_transaction()
    def test_numeric(self):
        'Test export_data numeric'
        pool = Pool()
        ExportData = pool.get('test.export_data')

        export1, = ExportData.create([{
                    'numeric': Decimal('1.1'),
                    }])
        self.assertEqual(
            ExportData.export_data([export1], ['numeric']),
            [[Decimal('1.1')]])

        export2, = ExportData.create([{
                    'numeric': Decimal('0'),
                    }])
        self.assertEqual(
            ExportData.export_data([export2], ['numeric']),
            [[Decimal('0')]])

        self.assertEqual(
            ExportData.export_data([export1, export2], ['numeric']),
            [[Decimal('1.1')], [Decimal('0')]])

    @with_transaction()
    def test_char(self):
        'Test export_data char'
        pool = Pool()
        ExportData = pool.get('test.export_data')

        export1, = ExportData.create([{
                    'char': 'test',
                    }])
        self.assertEqual(
            ExportData.export_data([export1], ['char']), [['test']])

        export2, = ExportData.create([{
                    'char': None,
                    }])
        self.assertEqual(
            ExportData.export_data([export2], ['char']), [['']])

        self.assertEqual(
            ExportData.export_data([export1, export2], ['char']),
            [['test'], ['']])

    @with_transaction()
    def test_text(self):
        'Test export_data text'
        pool = Pool()
        ExportData = pool.get('test.export_data')

        export1, = ExportData.create([{
                    'text': 'test',
                    }])
        self.assertEqual(
            ExportData.export_data([export1], ['text']), [['test']])

        export2, = ExportData.create([{
                    'text': None,
                    }])
        self.assertEqual(
            ExportData.export_data([export2], ['text']), [['']])

        self.assertEqual(
            ExportData.export_data([export1, export2], ['text']),
            [['test'], ['']])

    @with_transaction()
    def test_date(self):
        'Test export_data date'
        pool = Pool()
        ExportData = pool.get('test.export_data')

        export1, = ExportData.create([{
                    'date': datetime.date(2010, 1, 1),
                    }])
        self.assert_(ExportData.export_data([export1],
            ['date']) == [[datetime.date(2010, 1, 1)]])

        export2, = ExportData.create([{
                    'date': None,
                    }])
        self.assertEqual(
            ExportData.export_data([export2], ['date']), [['']])

        self.assertEqual(
            ExportData.export_data([export1, export2], ['date']),
            [[datetime.date(2010, 1, 1)], ['']])

    @with_transaction()
    def test_datetime(self):
        'Test export_data datetime'
        pool = Pool()
        ExportData = pool.get('test.export_data')

        export1, = ExportData.create([{
                    'datetime': datetime.datetime(2010, 1, 1, 12, 0, 0),
                    }])
        self.assertEqual(
            ExportData.export_data([export1], ['datetime']),
            [[datetime.datetime(2010, 1, 1, 12, 0, 0)]])

        export2, = ExportData.create([{
                    'datetime': None,
                    }])
        self.assertEqual(
            ExportData.export_data([export2], ['datetime']),
            [['']])

        self.assertEqual(
            ExportData.export_data([export1, export2], ['datetime']),
            [[datetime.datetime(2010, 1, 1, 12, 0, 0)], ['']])

    @with_transaction()
    def test_selection(self):
        'Test export_data selection'
        pool = Pool()
        ExportData = pool.get('test.export_data')

        export1, = ExportData.create([{
                    'selection': 'select1',
                    }])
        self.assertEqual(
            ExportData.export_data([export1], ['selection',
                    'selection.translated']),
            [['select1', 'Select 1']])

        export2, = ExportData.create([{
                    'selection': None,
                    }])
        self.assertEqual(
            ExportData.export_data([export2], ['selection']), [['']])

        self.assertEqual(
            ExportData.export_data([export1, export2],
                ['selection']),
            [['select1'], ['']])

    @with_transaction()
    def test_many2one(self):
        'Test export_data many2one'
        pool = Pool()
        ExportData = pool.get('test.export_data')
        ExportDataTarget = pool.get('test.export_data.target')

        target, = ExportDataTarget.create([{
                    'name': 'Target Test',
                    }])
        export1, = ExportData.create([{
                    'many2one': target.id,
                    }])
        self.assertEqual(
            ExportData.export_data([export1], ['many2one/name']),
            [['Target Test']])

        export2, = ExportData.create([{
                'many2one': None,
                }])
        self.assertEqual(
            ExportData.export_data([export2], ['many2one/name']),
            [['']])

        self.assertEqual(
            ExportData.export_data([export1, export2],
                ['many2one/name']),
            [['Target Test'], ['']])

    @with_transaction()
    def test_many2many(self):
        'Test export_data many2many'
        pool = Pool()
        ExportData = pool.get('test.export_data')
        ExportDataTarget = pool.get('test.export_data.target')

        target1, = ExportDataTarget.create([{
                    'name': 'Target 1',
                    }])
        export1, = ExportData.create([{
                    'many2many': [('add', [target1])],
                    }])
        self.assertEqual(
            ExportData.export_data([export1], ['many2many/name']),
            [['Target 1']])

        target2, = ExportDataTarget.create([{
                    'name': 'Target 2',
                    }])
        ExportData.write([export1], {
                'many2many': [('add', [target1.id, target2.id])],
                })
        self.assertEqual(
            ExportData.export_data([export1], ['id',
                    'many2many/name']),
            [[export1.id, 'Target 1'], ['', 'Target 2']])

        export2, = ExportData.create([{
                    'many2many': None,
                    }])
        self.assertEqual(
            ExportData.export_data([export2], ['many2many/name']),
            [['']])

        self.assertEqual(
            ExportData.export_data([export1, export2],
                ['id', 'many2many/name']),
            [[export1.id, 'Target 1'], ['', 'Target 2'], [export2.id, '']])

    @with_transaction()
    def test_one2many(self):
        'Test export_data one2many'
        pool = Pool()
        ExportData = pool.get('test.export_data')
        ExportDataTarget = pool.get('test.export_data.target')

        export1, = ExportData.create([{}])
        ExportDataTarget.create([{
                    'name': 'Target 1',
                    'one2many': export1.id,
                    }])
        self.assertEqual(
            ExportData.export_data([export1], ['one2many/name']),
            [['Target 1']])

        ExportDataTarget.create([{
                    'name': 'Target 2',
                    'one2many': export1.id,
                    }])
        self.assertEqual(
            ExportData.export_data([export1],
                ['id', 'one2many/name']),
            [[export1.id, 'Target 1'], ['', 'Target 2']])

        export2, = ExportData.create([{}])
        self.assertEqual(
            ExportData.export_data([export2], ['one2many/name']),
            [['']])

        self.assertEqual(
            ExportData.export_data([export1, export2], ['id',
                    'one2many/name']),
            [[export1.id, 'Target 1'], ['', 'Target 2'], [export2.id, '']])

    @with_transaction()
    def test_reference(self):
        'Test export_data reference'
        pool = Pool()
        ExportData = pool.get('test.export_data')
        ExportDataTarget = pool.get('test.export_data.target')

        target1, = ExportDataTarget.create([{'name': "Target test"}])
        export1, = ExportData.create([{
                    'reference': str(target1),
                    }])
        self.assertEqual(
            ExportData.export_data([export1], ['reference']),
            [[str(target1)]])

        export2, = ExportData.create([{
                    'reference': None,
                    }])
        self.assertEqual(
            ExportData.export_data([export2], ['reference']), [['']])

        self.assertEqual(
            ExportData.export_data([export1, export2],
                ['reference']),
            [[str(target1)], ['']])

        self.assertEqual(
            ExportData.export_data([export1], ['reference/rec_name']),
            [[target1.rec_name]])

        self.assertEqual(
            ExportData.export_data([export1], ['reference.translated']),
            [["Target"]])


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ExportDataTestCase)
