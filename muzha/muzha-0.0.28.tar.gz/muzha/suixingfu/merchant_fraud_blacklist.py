from typing import Dict, Optional

from .base import SuixingfuBase


class MerchantFraudBlacklist(SuixingfuBase):

    def generate_biz_data(self, idcard: str = None, bankcard: str = None, regNo: str = None, verify_type: str = '07') -> \
            Dict[str, Optional[str]]:
        """
        对于风险信息校验，商户营业执照编号、身份证号码、银行卡号三选一
        :param idcard:
        :param bankcard:
        :param regNo: 商户营业执照编号
        :param verify_type:
        :return:
        """
        data = {
            'identNo': idcard, 'cardNo': bankcard, 'verifyType': verify_type, 'regNo': regNo,
        }
        copied = data.copy()
        for k, v in data.items():
            if v is None:
                copied.pop(k)
        if len(copied) == 1 and copied.get('verifyType'):
            raise ValueError(f'data {data} is invalid')
        return copied

    def set_biz_data(self, *args: str) -> 'SuixingfuBase':
        self.biz_data = self.generate_biz_data(*args)
        return self
