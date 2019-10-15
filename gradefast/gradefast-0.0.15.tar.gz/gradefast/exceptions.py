class TestConventionError(Exception):
    def __init__(self, message, convention_mistakes):
        super().__init__(message)
        self.mistakes = convention_mistakes

class EmptySubmissionsException(Exception):
    def __init__(self):
        super().__init__('Empty or uninitialized submissions object. Use LoadSubmissions class to get submissions')

class ServerOrScraperException(Exception):
    def __init__(self):
        super().__init__("Server returned a non-2XX HTTP status code. Either the cookie provided is invalid or expired. Or there is an issue with the scraper or server.")

class RangeError(Exception):
    def __init__(self):
        super().__init__('Left argument of range should be less than or equal to the right')

class FilterException(Exception):
    def __init__(self):
        super().__init__('Atleast one valid filter should be supplied. Please recheck filter configurations.')

class ParseError(Exception):
    def __init__(self, message):
        return super().__init__(message)

class ResultToMarksConversionFailed(Exception):
    def __init__(self):
        exception_message = "Result to final marks conversion failed. Please rechek your Result values and marking scheme. The arrays should have similar dimensions and values need to be float or int"
        return super().__init__(exception_message)

class CannotMakeSubmissionsFS(Exception):
    def __init__(self):
        exception_message = "Cannot make submissions from file system because no submission.json was found or the folders don't exist on proper format on the disk. Use an alternative approach like 'from_url' to build submissions."
        return super().__init__(exception_message)

class InvalidParameterException(Exception):
    def __init__(self, message):
        super().__init__(message)

class PackagePathException(Exception):
    def __init__(self, message='Package path should not be empty if test type is package'):
        super().__init__(message)