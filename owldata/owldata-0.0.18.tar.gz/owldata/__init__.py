#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# =====================================================================
# Copyright (C) 2018-2019 by Owl Data
# author: Danny, Destiny

# =====================================================================

from .api import OwlData
from .__version__ import __version__

__docformat__ = 'restructuredtext'
__doc__ = '''
# OwlData 數據貓頭鷹 API

數據貓頭鷹官方網站: https://owl.cmoney.com.tw/Owl/

GitHub: https://github.com/owldb168/owldata

OwlData 提供一個穩定且快速的介面獲取數據貓頭鷹任何資料

使用注意事項:

- Python 免費版資料期間限制於2年，欄位詳見 GitHub或數據貓頭鷹官網

- 免費版試用期間為 90日，過期則需要再等 2天才能再次申請免費試用

- Python 付費版資料期間為 10年，欄位詳見 GitHub或數據貓頭鷹官網

- 若付費本出現無法擷取資料的情況，可能是因為商品清單或是交易週期對應表過期所導致，請向客服進行聯繫 (預設過期天數為999天，等待期限1日)

**有任何相關錯誤請聯繫:**

- E-mail：service@cmoney.com.tw
- 請撥打 02-8252-6620 分機241
- 星期一-星期五: 早上9:00-下午6:00, 除了國定假日以外

'''
