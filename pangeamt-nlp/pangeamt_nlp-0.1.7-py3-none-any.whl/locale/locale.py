class Locale:
    def __init__(self, locale: str):
        self._locale = locale

    @staticmethod
    def to_lang(locale: str) -> str:
        return locale.lower()[0:2]
