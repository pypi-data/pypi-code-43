
class CoachCareExceptions(Exception):
    """
    Base exception class for CoachCare project
    """

class NoDataRecieved(CoachCareExceptions):
    """
    No Data is Recieved
    """
class AuthenticationError(CoachCareExceptions):
    def __init__(self, error):
        CoachCareExceptions.__init__(self)
        self.error = error

    def __str__(self):
        return "Authenication Error: {}".format(self.error)

class BadResponse(CoachCareExceptions):
    def __init__(self, response_code):
        CoachCareExceptions.__init__(self)
        self.response_code = response_code

    def __str__(self):
        return "Bad response code: {}".format(self.response_code)

class InvalidRouteData(CoachCareExceptions):
    def __init__(self, diff):
        CoachCareExceptions.__init__(self)
        self.diff = diff
    
    def __str__(self):
        return "Data does not contain the minimum required fields\nMissing: {}".format(self.diff)

class InvalidHL7(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.msg = message

    def __str__(self):
        return "InvalidHL7 {}".format(self.msg)



