from typing import Any
from typing import Dict

from nezha import udict

from .base import BoolDataBase


class Bankcard3Eles(BoolDataBase):
    """
    简版/详版
    """
    service = 'bank_card_triple_elements'
    mode = 'mode_bank_card_triple_elements'
    detail_service = 'bank_card_triple_elements_detail'
    detail_mode = 'mode_bank_card_triple_elements_detail'

    default_part = [{
        "result_code": '',
        "result_code_desc": ""
    }]

    df_default_header = (
        'name', 'ident_number', 'phone', 'bank_card', 'result_code', 'result_code_desc'
    )

    @classmethod
    def generate_biz_data(cls,
                          name: str,
                          ident_number: str,
                          bank_card: str,
                          is_detail_version: bool = False) -> Dict[str, Any]:
        biz_data = udict.Dict.filter(locals())
        biz_data.update({
            "service": cls.detail_service if is_detail_version else cls.service,
            "mode": cls.detail_mode if is_detail_version else cls.mode
        })
        return biz_data

    def set_biz_data(self, name: str, ident_number: str, bankcard: str,
                     is_detail_version: bool = False) -> 'Bankcard3Eles':
        """
        support, Bankcard5Eles().set_biz_data().request()
        :param name:
        :param ident_number:
        :param bankcard:
        :param phone:
        :param account_type:
        :return:
        """
        self.biz_data = self.generate_biz_data(name, ident_number, bankcard, is_detail_version=is_detail_version)
        print('self.biz_data', self.biz_data)
        return self
