# coding:utf-8
from typing import Dict

from nezha.ustring import random_key

from .base import CloudWalkOCRBase


class IdCard(CloudWalkOCRBase):
    not_get_face = '0'
    get_face = '1'
    specified = ''
    uri = '/ai-cloud-face/ocr/idcard'

    @property
    def cls_name(self) -> str:
        return IdCard.__name__

    def generate_send_data(self, img: str) -> Dict[str, str]:
        send_data = {
            "img": img,
            "appKey": self.app_key,
            "nonceStr": self.specified or random_key(16),
            "getFace": self.get_face,
        }
        sign = self.generate_sign(send_data)
        send_data['sign'] = sign
        return send_data
