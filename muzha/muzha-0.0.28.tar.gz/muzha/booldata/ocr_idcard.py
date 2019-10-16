import os
from typing import Dict, Any

from .base import BoolDataBase

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class OCRIdcard(BoolDataBase):
    service = 'ocr_idcard_service'
    mode = 'ocr_idcard_mode'

    @classmethod
    def generate_biz_data(cls, img: str) -> Dict[str, Any]:
        return {
            'service': cls.service,
            'mode': cls.mode,
            'img': img
        }
