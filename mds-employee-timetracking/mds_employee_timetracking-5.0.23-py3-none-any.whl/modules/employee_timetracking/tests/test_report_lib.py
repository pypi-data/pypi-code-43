# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from datetime import timedelta, time
from trytond.pool import Pool


class ReportLibTestCase(ModuleTestCase):
    'Test reort lib module'
    module = 'employee_timetracking'

    @with_transaction()
    def test_reportlib_cleanfilename(self):
        """ test: cleanup filename from invalid chars
        """
        ReportMonth = Pool().get('employee_timetracking.report_evaluation_month', type='report')
        self.assertEqual(ReportMonth.clean_filename('abDFä(öo)ôá^|[]1234.txt'), 'abDFa(oo)oa1234.txt')

    @with_transaction()
    def test_reportlib_formattime(self):
        """ test: format time values
        """
        ReportMonth = Pool().get('employee_timetracking.report_evaluation_month', type='report')
        self.assertEqual(ReportMonth.formattime(time(0, 23)), '00:23')
        self.assertEqual(ReportMonth.formattime(time(1, 23)), '01:23')
        self.assertEqual(ReportMonth.formattime(time(10, 53)), '10:53')
        self.assertEqual(ReportMonth.formattime(time(22, 42)), '22:42')

    @with_transaction()
    def test_reportlib_formattimedelta(self):
        """ test: format positive and negative timedelta values
        """
        ReportMonth = Pool().get('employee_timetracking.report_evaluation_month', type='report')
        
        # invalid values
        self.assertEqual(ReportMonth.formattimedelta('123'), '')
        self.assertEqual(ReportMonth.formattimedelta(None), '')
        
        # zero
        self.assertEqual(ReportMonth.formattimedelta(timedelta(seconds=0)), '+00:00')
        self.assertEqual(ReportMonth.formattimedelta(timedelta(seconds=0), noplussign=True), '00:00')
        
        # positive timedelta
        self.assertEqual(ReportMonth.formattimedelta(timedelta(seconds=60*60)), '+01:00')
        self.assertEqual(ReportMonth.formattimedelta(timedelta(seconds=60*60), noplussign=True), '01:00')
        self.assertEqual(ReportMonth.formattimedelta(timedelta(seconds=60*60 + 23*60 + 42)), '+01:23')
        self.assertEqual(ReportMonth.formattimedelta(timedelta(seconds=60*60*5 + 23*60)), '+05:23')
        self.assertEqual(ReportMonth.formattimedelta(timedelta(seconds=60*60*15 + 23*60)), '+15:23')
        self.assertEqual(ReportMonth.formattimedelta(timedelta(seconds=60*60*25 + 23*60)), '+25:23')
        self.assertEqual(ReportMonth.formattimedelta(timedelta(days=1, seconds=60*60 + 23*60)), '+25:23')
        self.assertEqual(ReportMonth.formattimedelta(timedelta(days=5, seconds=60*60*5 + 23*60)), '+125:23')

        # negative timedelta
        self.assertEqual(ReportMonth.formattimedelta(-timedelta(seconds=60*60)), '-01:00')
        self.assertEqual(ReportMonth.formattimedelta(-timedelta(seconds=60*60), noplussign=True), '-01:00')
        self.assertEqual(ReportMonth.formattimedelta(-timedelta(seconds=60*60 + 23*60 + 42)), '-01:23')
        self.assertEqual(ReportMonth.formattimedelta(-timedelta(seconds=60*60*5 + 23*60)), '-05:23')
        self.assertEqual(ReportMonth.formattimedelta(-timedelta(seconds=60*60*15 + 23*60)), '-15:23')
        self.assertEqual(ReportMonth.formattimedelta(-timedelta(seconds=60*60*25 + 23*60)), '-25:23')
        self.assertEqual(ReportMonth.formattimedelta(-timedelta(days=1, seconds=60*60 + 23*60)), '-25:23')
        self.assertEqual(ReportMonth.formattimedelta(-timedelta(days=5, seconds=60*60*5 + 23*60)), '-125:23')

# end ReportLibTestCase
