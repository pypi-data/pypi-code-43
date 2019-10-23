# coding: utf-8

from __future__ import absolute_import

from datetime import date, timedelta
import unittest
from mercury import UnbalancedButterfly, ButterflyValueException
from mercury import OptionLeg
from mercury.client.model.option_contract_type import OptionContractType


class TestUnbalancedButterfly(unittest.TestCase):
    """Butterfly unit test stubs"""

    """
    todo: note: this will be used to check both unbalanced and balanced butterfly trades
    """

    def setUp(self):
        # These legs MUST be valid for UB
        self.first_leg = OptionLeg(**{
            "expiration_date": date(2018, 5, 14),
            "type": OptionContractType.PUT,
            "quantity": 3,
            "strike": 2585,
            "opening_price": 0.1
        })
        self.mid_leg = OptionLeg(**{
            "expiration_date": date(2018, 5, 14),
            "type": OptionContractType.PUT,
            "quantity": -2,
            "strike": 2610,
            "opening_price": 0.1
        })
        self.third_leg = OptionLeg(**{
            "expiration_date": date(2018, 5, 14),
            "type": OptionContractType.PUT,
            "quantity": 1,
            "strike": 2635,
            "opening_price": 0.1
        })
        # Make sure the legs are ok
        UnbalancedButterfly(symbol='SPX',
                            quantity=1,
                            opening_date=date(2018, 5, 14),
                            first_leg=self.first_leg,
                            mid_leg=self.mid_leg,
                            third_leg=self.third_leg)

    def tearDown(self):
        pass

    def test_ub_direction_error(self):
        self.first_leg.quantity = 1  # Long
        self.mid_leg.quantity = 2  # Long
        self.third_leg.quantity = -1  # Short

        with self.assertRaises(ButterflyValueException) as ctx:
            UnbalancedButterfly(symbol='SPX',
                                quantity=1,
                                opening_date=date(2018, 5, 14),
                                first_leg=self.first_leg,
                                mid_leg=self.mid_leg,
                                third_leg=self.third_leg)

    def test_ub_direction_error2(self):
        self.first_leg.quantity = 1  # Long
        self.mid_leg.quantity = 2  # Long
        self.third_leg.quantity = 2  # Long
        with self.assertRaises(ButterflyValueException) as ctx:
            UnbalancedButterfly(symbol='SPX',
                                quantity=1,
                                opening_date=date(2018, 5, 14),
                                first_leg=self.first_leg,
                                mid_leg=self.mid_leg,
                                third_leg=self.third_leg)

    def test_ub_strike_error(self):
        self.first_leg.strike = 3
        self.mid_leg.strike = 2
        self.third_leg.strike = 1
        with self.assertRaises(ButterflyValueException) as ctx:
            UnbalancedButterfly(symbol='SPX',
                                quantity=1,
                                opening_date=date(2018, 5, 14),
                                first_leg=self.first_leg,
                                mid_leg=self.mid_leg,
                                third_leg=self.third_leg)

    def test_ub_type_error(self):
        self.first_leg.type = OptionContractType.PUT
        self.mid_leg.type = OptionContractType.CALL
        self.third_leg.type = OptionContractType.PUT
        with self.assertRaises(ButterflyValueException) as ctx:
            UnbalancedButterfly(symbol='SPX',
                                quantity=1,
                                opening_date=date(2018, 5, 14),
                                first_leg=self.first_leg,
                                mid_leg=self.mid_leg,
                                third_leg=self.third_leg)

    def test_ub_exp_date_error(self):
        self.third_leg.expiration_date = self.first_leg.expiration_date + timedelta(days=1)
        with self.assertRaises(ButterflyValueException) as ctx:
            UnbalancedButterfly(symbol='SPX',
                                quantity=1,
                                opening_date=date(2018, 5, 14),
                                first_leg=self.first_leg,
                                mid_leg=self.mid_leg,
                                third_leg=self.third_leg)

    def test_ub_quantity_error(self):
        self.first_leg.quantity = 1
        self.mid_leg.quantity = 1
        self.third_leg.quantity = 1
        with self.assertRaises(ButterflyValueException) as ctx:
            UnbalancedButterfly(symbol='SPX',
                                quantity=1,
                                opening_date=date(2018, 5, 14),
                                first_leg=self.first_leg,
                                mid_leg=self.mid_leg,
                                third_leg=self.third_leg)


if __name__ == '__main__':
    unittest.main()
