class OnBoardingError(Exception):
    pass


class DeviceRegisterError(OnBoardingError):
    pass


class DeviceConfigureError(OnBoardingError):
    pass


class ConfigValidationError(OnBoardingError):
    pass


class GenerateKeysError(OnBoardingError):
    pass


class BoardError(OnBoardingError):
    pass


class ConnectorError(OnBoardingError):
    pass


class ConnectorExecuteError(ConnectorError):
    pass
