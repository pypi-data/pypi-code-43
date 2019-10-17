class Response:

    def __init__(self, status, data):
        """
        Requester return this class as result

        :param status: http request status
        :param data: http request result - raw html
        """
        self.__status = status
        self.__data = data

    def get_data(self):
        return self.__data

    def get_status(self):
        return self.__status