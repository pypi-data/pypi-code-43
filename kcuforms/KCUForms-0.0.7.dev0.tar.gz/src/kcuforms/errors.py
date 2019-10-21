__all__ = (
    "FieldError",
)


class BaseError(ValueError):
    """
    Raised when a error occur.
    """

    SUBCODE = 10501
    STATUS = u'KCUForms Error'

    def __init__(self, message="", subcode=SUBCODE, status=STATUS, *args, **kwargs):
        self.status = status or self.STATUS
        self.subcode = subcode or self.SUBCODE
        ValueError.__init__(self, message, *args, **kwargs)


class FieldError(BaseError):
    SUBCODE = 10422
    STATUS = u'KCUForms Field Error'
