# aisolution.freeflyer.runtimeapi package

"""
    Contains a class which represents a Runtime API function result.
"""
class GetMissionPlanDiagnosticsResult(object):
    """
    Result class for the RuntimeApiEngine.getMissionPlanDiagnostics method.
    """

    def __init__(
            self
            ,
            errorsCount
            ,
            errors
            ,
            warningsCount
            ,
            warnings
    ):
        self.errorsCount = errorsCount
        self.errors = errors
        self.warningsCount = warningsCount
        self.warnings = warnings

    def getErrorsCount(self):
        """
           The number of errors retrieved.
        """

        return self.errorsCount
    def getErrors(self):
        """
           The text of the errors retrieved.
        """

        return self.errors
    def getWarningsCount(self):
        """
           The number of warnings retrieved.
        """

        return self.warningsCount
    def getWarnings(self):
        """
           The text of the warnings retrieved.
        """

        return self.warnings
