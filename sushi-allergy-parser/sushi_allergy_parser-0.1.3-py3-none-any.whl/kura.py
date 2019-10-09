import re

import numpy
import pandas as pd
import tabula

from .base import AllergenState, BaseParser, Allergen
from .util import removeNewLine

REMOTE_URL = "http://www.kura-corpo.co.jp/common/pdf/kura_allergen.pdf"
BASE_LAYOUT = [
    ("卵", Allergen.EGG.value, True),  # header, key, required
    ("小麦", Allergen.WHEAT.value, True),
    ("乳・乳製品", Allergen.MILK.value, True),
    ("落花生ピーナッツ", Allergen.PEANUT.value, True),
    ("ソバ", Allergen.BUCKWHEAT.value, True),
    ("えび", Allergen.SHRIMP.value, True),
    ("かに", Allergen.CRAB.value, True),
    ("いか", Allergen.SQUID.value, True),
    ("いくら", Allergen.SALMON_ROE.value, True),
    ("さけ", Allergen.SALMON.value, True),
    ("さば", Allergen.MACKEREL.value, True),
    ("牛肉", Allergen.BEEF.value, True),
    ("鶏肉", Allergen.CHICKEN.value, True),
    ("豚肉", Allergen.PORK.value, True),
    ("大豆", Allergen.SOYBEAN.value, True),
    ("オレンジ", Allergen.ORANGE.value, True),
    ("りんご", Allergen.APPLE.value, True),
    ("ゼラチン", Allergen.GELATIN.value, True),
    ("クルミ", Allergen.WALNUT.value, True),
    ("バナナ", Allergen.BANANA.value, True),
    ("キウイ", Allergen.KIWI.value, True),
    ("山芋", Allergen.YAM_OR_SWEET_POTATO.value, True),
    ("モモ", Allergen.PEACH.value, True),
    ("ごま", Allergen.SESAME.value, True),
    ("あわび", Allergen.ABALONE.value, True),
    ("カシューナッツ", Allergen.CASHEW_NUT.value, True),
    ("松茸", Allergen.MATSUTAKE_MUSHROOM.value, True),
]
PAGE1_LAYOUT = [
    ("品名", "name", True),
    ("(kカ一cロ皿aリ当lーり)", "calory", False),
    ("該当なし", "none", False),
    *BASE_LAYOUT,
]
PAGE2_LAYOUT = PAGE1_LAYOUT
PAGE3_LAYOUT = [
    ("品名", "name", True),
    ("一(皿kカ・cロ一aリlー杯当)り", "calory", False),
    ("該当なし", "none", False),
    *BASE_LAYOUT,
]
PAGE4_LAYOUT = [("品名", "name", True), ("該当なし", "none", False), *BASE_LAYOUT]
PAGES = [
    ("1", "定番寿司", PAGE1_LAYOUT),
    ("2", "限定商品", PAGE2_LAYOUT),
    ("3", "サイドメニュー", PAGE3_LAYOUT),
    ("4", "その他", PAGE4_LAYOUT),
]


class KuraAllergyParser(BaseParser):
    def parse(self, filename: str = REMOTE_URL) -> pd.DataFrame:
        df_list = []
        for page, category, layout in PAGES:
            df = self._parse_table(filename, page, category, layout)
            df_list.append(df)

        df_all = pd.concat(df_list, ignore_index=True)

        for _, key, _ in BASE_LAYOUT:
            df_all[key] = df_all[key].map(self.allergen_state_of)

        return df_all

    def _parse_table(
        self, filename: str, page: int, category: str, layout: list
    ) -> pd.DataFrame:

        df = tabula.read_pdf(filename, pages=str(page), lattice=True)

        columns = [re.sub(r"\s", "", column) for column in df.columns]
        expected_columns = [column[0] for column in layout]
        assert columns == expected_columns, f"{filename} のテーブルレイアウトが変更されました。{page}ページ目"

        df.columns = [column[1] for column in layout]

        # Remove unnecessary columns
        for _, key, required in layout:
            if not required:
                del df[key]

        df_cleansed = df.applymap(removeNewLine)

        df_cleansed["category"] = category

        return df_cleansed

    def allergen_state_of(self, value: str) -> AllergenState:
        if value == "●":
            return AllergenState.CONTAIN
        elif value == "▲":
            return AllergenState.MAY_CONTAIN
        elif numpy.isnan(value):
            return AllergenState.NOT_CONTAIN
        else:
            raise ValueError(f"Unknown AllergenState {value}.")
