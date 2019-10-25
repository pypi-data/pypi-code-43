from pangeamt_nlp.locale.locale import Locale
from pangeamt_nlp.multilingual_ressource import Tmx

class TmxReaderBilingualText:
    def __init__(self, src_lang, tgt_lang):
        self._src_lang = src_lang
        self._tgt_lang = tgt_lang

        self._tmx_src_locale = None
        self._tmx_tgt_locale = None

    def read(self, segs_by_locale):
        if self._tmx_src_locale is None:
            src_locales = [locale for locale in segs_by_locale if Locale.to_lang(locale) in self._src_lang]
            if len(src_locales) != 1:
                raise ValueError(f"TmxExtractorBilingualText. More than one language for {self._src_lang}: {''.join(src_locales)}")
            self._tmx_src_locale = src_locales[0]

            tgt_locales = [locale for locale in segs_by_locale if Locale.to_lang(locale) in self._tgt_lang]
            if len(tgt_locales) != 1:
                raise ValueError(f"TmxExtractorBilingualText. More than one language for {self._tgt_lang}: {''.join(tgt_locales)}")
            self._tmx_tgt_locale = tgt_locales[0]

        try:
            src = segs_by_locale[self._tmx_src_locale]
        except KeyError:
            raise ValueError(f"TmxExtractorBilingualText. {self._src_lang} is mapped to {self._tmx_src_locale} and no segment was find for that locale")
        try:
            tgt = segs_by_locale[self._tmx_tgt_locale]
        except KeyError:
            raise ValueError(f"TmxExtractorBilingualText. {self._tgt_lang} is mapped to {self._tmx_tgt_locale} and no segment was find for that locale")

        return Tmx.seg_to_text(src), Tmx.seg_to_text(tgt)
