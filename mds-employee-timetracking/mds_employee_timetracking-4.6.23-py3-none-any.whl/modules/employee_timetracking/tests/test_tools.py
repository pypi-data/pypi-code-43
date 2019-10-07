# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from datetime import timedelta
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from datetime import timedelta


class ToolsTestCase(ModuleTestCase):
    'Test tools module'
    module = 'employee_timetracking'

    @with_transaction()
    def test_tools_round_timedelta(self):
        """ test: rounding of timedelta-value
        """
        from ..tools import round_timedelta
        
        self.assertRaisesRegex(ValueError,
            "wrong parameter in'rndmode': '123' \(up/down\)",
            round_timedelta,
            timedelta(seconds=23*60 + 42), rndmode='123')

        # 23 min 42 sec - up
        self.assertEqual(
                round_timedelta(timedelta(seconds=23*60 + 42), rndmode='up'), 
                timedelta(seconds=24*60)
            )
        # 23 min 42 sec - down
        self.assertEqual(
                round_timedelta(timedelta(seconds=23*60 + 42), rndmode='down'), 
                timedelta(seconds=23*60)
            )
        # 18 h 23 min 42 sec - up
        self.assertEqual(
                round_timedelta(timedelta(seconds=18*60*60 + 23*60 + 42), rndmode='up'), 
                timedelta(seconds=18*60*60 + 24*60)
            )
        # 18 h 23 min 42 sec - down
        self.assertEqual(
                round_timedelta(timedelta(seconds=18*60*60 + 23*60 + 42), rndmode='down'), 
                timedelta(seconds=18*60*60 + 23*60)
            )
        # 2 days 18 h 23 min 42 sec - up
        self.assertEqual(
                round_timedelta(timedelta(days=2, seconds=18*60*60 + 23*60 + 42), rndmode='up'), 
                timedelta(days=2, seconds=18*60*60 + 24*60)
            )
        # 2 days 18 h 23 min 42 sec - down
        self.assertEqual(
                round_timedelta(timedelta(days=2, seconds=18*60*60 + 23*60 + 42), rndmode='down'), 
                timedelta(days=2, seconds=18*60*60 + 23*60)
            )

        # 0 +
        self.assertEqual(
                round_timedelta(timedelta(seconds=0), rndmode='up'), 
                timedelta(seconds=0)
            )
        # 0 -
        self.assertEqual(
                round_timedelta(timedelta(seconds=0), rndmode='down'), 
                timedelta(seconds=0)
            )

        # - 23 min 42 sec - up
        self.assertEqual(
                round_timedelta(-timedelta(seconds=23*60 + 42), rndmode='up'), 
                -timedelta(seconds=23*60)
            )
        # - 23 min 42 sec - down
        self.assertEqual(
                round_timedelta(-timedelta(seconds=23*60 + 42), rndmode='down'), 
                -timedelta(seconds=24*60)
            )
        # 18 h 23 min 42 sec - up
        self.assertEqual(
                round_timedelta(-timedelta(seconds=18*60*60 + 23*60 + 42), rndmode='up'), 
                -timedelta(seconds=18*60*60 + 23*60)
            )
        # 18 h 23 min 42 sec - down
        self.assertEqual(
                round_timedelta(-timedelta(seconds=18*60*60 + 23*60 + 42), rndmode='down'), 
                -timedelta(seconds=18*60*60 + 24*60)
            )
        # 2 days 18 h 23 min 42 sec - up
        self.assertEqual(
                round_timedelta(-timedelta(days=2, seconds=18*60*60 + 23*60 + 42), rndmode='up'), 
                -timedelta(days=2, seconds=18*60*60 + 23*60)
            )
        # 2 days 18 h 23 min 42 sec - down
        self.assertEqual(
                round_timedelta(-timedelta(days=2, seconds=18*60*60 + 23*60 + 42), rndmode='down'), 
                -timedelta(days=2, seconds=18*60*60 + 24*60)
            )

# end ToolsTestCase

