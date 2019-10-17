class RequesterException(Exception):
    def __init__(self, message, url):
        super(Exception, self).__init__(message)
        self.__url = url

    def get_url(self):
        return self.__url