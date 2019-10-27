

class JsonException(Exception):
    pass


class HmacException(Exception):
    def __init__(self, calculated, desired):
        self.calculated = calculated
        self.desired = desired


class DecryptNotFound(Exception):
    pass


class NoDecodersDefined(Exception):
    pass
