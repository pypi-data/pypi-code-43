from typing import Dict

from nezha import udict

from .base import SuixingfuBase


class BankcardTripleElements(SuixingfuBase):
    verifyType = '03'

    def generate_biz_data(self, name: str, identNo: str, cardNo: str) -> Dict[str, str]:
        send_data = udict.Dict.filter(locals())
        send_data['verifyType'] = self.verifyType
        return send_data

    def set_biz_data(self, *args: str) -> 'SuixingfuBase':
        self.biz_data = self.generate_biz_data(*args)
        return self
