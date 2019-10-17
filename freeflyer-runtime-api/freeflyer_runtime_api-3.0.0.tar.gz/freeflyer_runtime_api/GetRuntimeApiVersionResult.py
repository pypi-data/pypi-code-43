# aisolution.freeflyer.runtimeapi package

"""
    Contains a class which represents a Runtime API function result.
"""
class GetRuntimeApiVersionResult(object):
    """
    Result class for the RuntimeApiEngine.getRuntimeApiVersion method.
    """

    def __init__(
            self
            ,
            major
            ,
            minor
    ):
        self.major = major
        self.minor = minor

    def getMajor(self):
        """
           The major version of the Runtime API.
        """

        return self.major
    def getMinor(self):
        """
           The minor version of the Runtime API.
        """

        return self.minor
