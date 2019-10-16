from typing import Any
from typing import Dict

from nezha import udict

from .base import BoolDataBase


class PersonalCertify(BoolDataBase):
    """
    简版/详版
    """
    service = 'personal_certify'
    mode = 'mode_personal_certify'

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
                          phone: str) -> Dict[str, Any]:
        biz_data = udict.Dict.filter(locals())
        biz_data.update({
            "service": cls.service,
            "mode": cls.mode
        })
        return biz_data

    def set_biz_data(self, name: str, ident_number: str, phone: str) -> 'PersonalCertify':
        """
        support, Bankcard5Eles().set_biz_data().request()
        :param name:
        :param ident_number:
        :param phone:
        :return:
        """
        self.biz_data = self.generate_biz_data(name, ident_number, phone)
        print('self.biz_data', self.biz_data)
        return self
