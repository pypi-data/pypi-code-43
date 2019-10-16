class GeofilesError(Exception):
    def __init__(self, *args, **kwargs):
        """
        Custom Exception for the cpc.geofiles package

        ### Parameters

        - message (string): Exception message
        - file (string): File being loading when the Exception was raised
        """
        self.__dict__.update(kwargs)
        Exception.__init__(self, *args, **kwargs)


class LoadingError(Exception):
    def __init__(self, message, file=None, *args, **kwargs):
        """
        Custom Exception for the loading module

        ### Parameters

        - message (string): Exception message
        - file (string): File being loading when the Exception was raised
        """
        self.__dict__.update(kwargs)
        self.file = file
        Exception.__init__(self, message, file, *args, **kwargs)


class ReadingError(Exception):
    def __init__(self, message, file=None, *args, **kwargs):
        """
        Custom Exception for the loading module

        ### Parameters

        - message (string): Exception message
        - file (string): File being loading when the Exception was raised
        """
        self.__dict__.update(kwargs)
        self.file = file
        Exception.__init__(self, message, file, *args, **kwargs)
