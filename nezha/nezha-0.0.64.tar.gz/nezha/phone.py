# -*- coding: utf-8 -*-

from typing import Dict
from typing import Tuple


class Phone:
    f_yidong = 'yidong'
    f_liantong = 'liantong'
    f_dianxin = 'dianxin'
    valid_length = 11

    @classmethod
    def get_operator_segment(cls) -> Dict[str, Tuple]:
        return {
            cls.f_yidong: ('134', '135', '136', '137', '138', '139', '150', '151', '152', '157',
                           '158', '159', '182', '183', '184', '187', '188', '147', '178', '1703', '1705', '1706'),
            cls.f_liantong: ('130', '131', '132', '145', '155', '156', '175', '176', '185', '186', '171', '1704',
                             '1707', '1708', '1709'),
            cls.f_dianxin: ('133', '149', '153', '173', '177', '180', '181', '189', '1700', '1701', '1702')
        }

    @classmethod
    def all_operators(cls) -> Tuple[str, str, str]:
        return (cls.f_yidong, cls.f_liantong, cls.f_dianxin)

    @classmethod
    def get_operator(cls, phone: str) -> str:
        if not isinstance(phone, str):
            raise ValueError(f"phone {phone} is expected str and got {type(phone)}")
        if len(phone) != cls.valid_length:
            raise ValueError(f"phone {phone} length is expected {cls.valid_length} and got {len(phone)}")
        top_three = phone[0:3]
        top_four = phone[0:4]
        for operator, segment in cls.get_operator_segment().items():
            if top_three in segment or top_four in segment:
                return operator
        return ''
