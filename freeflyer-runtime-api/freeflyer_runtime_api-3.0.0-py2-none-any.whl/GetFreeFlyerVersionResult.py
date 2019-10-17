# aisolution.freeflyer.runtimeapi package

"""
    Contains a class which represents a Runtime API function result.
"""
class GetFreeFlyerVersionResult(object):
    """
    Result class for the RuntimeApiEngine.getFreeFlyerVersion method.
    """

    def __init__(
            self
            ,
            major
            ,
            minor
            ,
            build
            ,
            revision
    ):
        self.major = major
        self.minor = minor
        self.build = build
        self.revision = revision

    def getMajor(self):
        """
           The major version of FreeFlyer.
        """

        return self.major
    def getMinor(self):
        """
           The minor version of FreeFlyer.
        """

        return self.minor
    def getBuild(self):
        """
           The build version of FreeFlyer.
        """

        return self.build
    def getRevision(self):
        """
           The revision version of FreeFlyer.
        """

        return self.revision
