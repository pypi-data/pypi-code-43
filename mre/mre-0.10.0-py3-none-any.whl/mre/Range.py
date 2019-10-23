from .Regex import Regex


class Range(Regex):
    """Range class."""

    def __init__(self, regex: str = ""):
        super().__init__(regex)
        self.format = "{}-{}"

    def numbers(self, min: int = 0, max: int = 9):
        return Range(self.format.format(min, max))

    def letters(self, min: chr = 'A', max: chr = 'z', uppercase: bool = False, lowercase: bool = False):
        if lowercase and uppercase:
            min = min.lower()
            max = max.upper()
        elif lowercase:
            min = min.lower()
            max = max.lower()
        elif uppercase:
            min = min.upper()
            max = max.upper()

        return Range(self.format.format(min, max))
