class ViiError(Exception):
    def __init__(self, msg):
        super(ViiError, self).__init__(msg)


class BadSignatureError(ViiError):
    pass


class AssetCodeInvalidError(ViiError):
    pass


class ViiAddressInvalidError(ViiError):
    pass


class ViiSecretInvalidError(ViiError):
    pass


class NoViiSecretOrAddressError(ViiError):
    pass


class SequenceError(ViiError):
    pass


class ConfigurationError(ViiError):
    pass


class NoApproximationError(ViiError):
    pass


class HorizonError(ViiError):
    """A :exc:`HorizonError` that represents an issue stemming from
    Vii Horizon.

    """

    def __init__(self, msg, status_code):
        super(HorizonError, self).__init__(msg)
        self.message = msg
        self.status_code = status_code


class HorizonRequestError(ViiError):
    """A :exc:`HorizonRequestError` that represents we cannot connect
    to Vii Horizon.

    """
    pass


class SignatureExistError(ViiError):
    pass


class DecodeError(ViiError):
    pass


class NotValidParamError(ViiError):
    pass


class MnemonicError(ViiError):
    pass


class MissingSigningKeyError(ViiError):
    pass


class FederationError(Exception):
    """A :exc:`FederationError` that represents an issue stemming from
    Vii Federation.

    """


class InvalidSep10ChallengeError(ViiError):
    pass
