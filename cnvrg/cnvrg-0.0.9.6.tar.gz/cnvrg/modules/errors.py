class CnvrgError(Exception):
    pass

class UserError(CnvrgError):
    pass

class NotImplementedError(CnvrgError):
    pass

class UnknownStsError(CnvrgError):
    pass