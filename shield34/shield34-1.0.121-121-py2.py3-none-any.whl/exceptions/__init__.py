
class Shield34PropertiesFileNotFoundException(Exception):
    DEFAULT_MESSAGE = "shield34 properties file was not found, please check if shield34.ini file exists in your project home directory"

    def __init__(self, message=DEFAULT_MESSAGE):
        super(Shield34PropertiesFileNotFoundException, self).__init__(message)

class Shield34PropertiesSyntaxIncorrect(Exception):
    DEFAULT_MESSAGE = "shield34 properties syntax is incorrect, please check your shield34.ini file"

    def __init__(self, message=DEFAULT_MESSAGE):
        super(Shield34PropertiesSyntaxIncorrect, self).__init__(message)

class Shield34LoginFailedException(Exception):
    DEFAULT_MESSAGE = "login to shield34 account failed, please check your project's credentials in shield34.ini file"
    def __init__(self, message=DEFAULT_MESSAGE):
        super(Shield34LoginFailedException, self).__init__(message)