class GenericError(Exception):
    default_message = None

    def __init__(self, *args, **kwargs):
        if not args and not kwargs and self.default_message is not None:
            super().__init__(self.default_message)
        else:
            super().__init__(*args, **kwargs)


class ConfigurationError(GenericError):
    pass


class ConfigNotFoundError(ConfigurationError):
    default_message = 'config file not found'


class NoDistFilesFoundError(GenericError):
    pass


class UploaderError(GenericError):
    pass


class UploadError(UploaderError):
    pass


class InvalidUploadDestination(UploadError):
    pass


class FileAlreadyUploaded(UploadError):
    pass
