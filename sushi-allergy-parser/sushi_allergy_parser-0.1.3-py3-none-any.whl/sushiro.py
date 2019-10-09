import re

import numpy
import pandas as pd
import tabula

from .base import AllergenState, BaseParser, Allergen
from .util import removeNewLine

REMOTE_URL = "http://www3.akindo-sushiro.co.jp/pdf/menu/allergy.pdf"
BASE_LAYOUT = [
    ("卵", Allergen.EGG.value, True),  # header, key, required
    ("乳", Allergen.MILK.value, True),
    ("小麦", Allergen.WHEAT.value, True),
    ("えび", Allergen.SHRIMP.value, True),
    ("かに", Allergen.CRAB.value, True),
    ("そば", Allergen.BUCKWHEAT.value, True),
    ("落花生", Allergen.PEANUT.value, True),
    ("あわび", Allergen.ABALONE.value, True),
    ("いか", Allergen.SQUID.value, True),
    ("いくら", Allergen.SALMON_ROE.value, True),
    ("オレンジ", Allergen.ORANGE.value, True),
    ("キウイ", Allergen.KIWI.value, True),
    ("牛肉", Allergen.BEEF.value, True),
    ("クルミ", Allergen.WALNUT.value, True),
    ("鮭", Allergen.SALMON.value, True),
    ("さば", Allergen.MACKEREL.value, True),
    ("大豆", Allergen.SOYBEAN.value, True),
    ("鶏肉", Allergen.CHICKEN.value, True),
    ("バナナ", Allergen.BANANA.value, True),
    ("豚肉", Allergen.PORK.value, True),
    ("松茸", Allergen.MATSUTAKE_MUSHROOM.value, True),
    ("桃", Allergen.PEACH.value, True),
    ("山芋", Allergen.YAM_OR_SWEET_POTATO.value, True),
    ("りんご", Allergen.APPLE.value, True),
    ("ゼラチン", Allergen.GELATIN.value, True),
    ("ごま", Allergen.SESAME.value, True),
    ("カシューナッツ", Allergen.CASHEW_NUT.value, True),
]
TABLE_LAYOUT = [
    ("分類", "category", True),
    ("商品名", "name", True),
    *BASE_LAYOUT,
    ("なし", "none", False),
]


class SushiroAllergyParser(BaseParser):
    def parse(self, filename: str = REMOTE_URL) -> pd.DataFrame:
        df = self._parse_table(filename, TABLE_LAYOUT)

        for _, key, _ in BASE_LAYOUT:
            df[key] = df[key].map(self.allergen_state_of)

        return df

    def _parse_table(self, filename, layout) -> pd.DataFrame:

        df = tabula.read_pdf(filename, pages="all", lattice=True)

        columns = [re.sub(r"\s", "", column) for column in df.columns]
        expected_columns = [column[0] for column in layout]
        assert columns == expected_columns, f"{filename} のテーブルレイアウトが変更されました。"

        df.columns = [column[1] for column in layout]

        # Remove unnecessary columns
        for _, key, required in layout:
            if not required:
                del df[key]

        df_filterd = df.query('category != "分類"')

        df_cleansed = df_filterd.applymap(removeNewLine)

        return df_cleansed

    def allergen_state_of(self, value: str) -> AllergenState:
        if value == "●":
            return AllergenState.CONTAIN
        elif value == "○":
            return AllergenState.MAY_CONTAIN
        elif numpy.isnan(value):
            return AllergenState.NOT_CONTAIN
        else:
            raise ValueError(f"Unknown AllergenState {value}.")

