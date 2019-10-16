from typing import Dict

from .base import CloudWalkOCRBase
from nezha.ustring import random_key


class CloudWalkOCRBankcard(CloudWalkOCRBase):
    specified = ''
    uri = '/ai-cloud-face/ocr/bankcard'

    @property
    def cls_name(self) -> str:
        return CloudWalkOCRBankcard.__name__

    def generate_send_data(self, img: str) -> Dict[str, str]:
        send_data = {
            "img": img,
            "appKey": self.app_key,
            "nonceStr": self.specified or random_key(16),
        }
        sign = self.generate_sign(send_data)
        send_data['sign'] = sign
        return send_data
