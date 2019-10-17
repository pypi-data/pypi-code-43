# aisolution.freeflyer.runtimeapi package

"""
    Contains a class which represents a Runtime API function result.
"""
class GetLocationResult(object):
    """
    Result class for the RuntimeApiEngine.getLocation method.
    """

    def __init__(
            self
            ,
            source
            ,
            line
            ,
            statement
    ):
        self.source = source
        self.line = line
        self.statement = statement

    def getSource(self):
        """
           The source of the current statement.
        """

        return self.source
    def getLine(self):
        """
           The line of the current statement within the source.
        """

        return self.line
    def getStatement(self):
        """
           The text of the current statement.
        """

        return self.statement
