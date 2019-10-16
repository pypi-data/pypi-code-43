from typing import Dict

from .base import ShenxinBase


class BankcardFiveElements(ShenxinBase):

    def generate_send_data(self, name: str, phone: str, idcard: str, account_type: str, bankcard: str) -> Dict[
        str, str]:
        raw_biz_data = {
            "phone": phone,
            "identNumber": idcard,
            "accountType": account_type,
            "name": name,
            "bankcard": bankcard
        }
        send_data = {"bankCode": self.company_uuid,
                     "requestBody": self.generate_request_body(raw_biz_data),
                     "sign": self.generate_sign(raw_biz_data)}
        return send_data
