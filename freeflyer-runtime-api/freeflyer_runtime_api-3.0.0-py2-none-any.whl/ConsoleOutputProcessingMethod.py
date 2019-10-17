# aisolution.freeflyer.runtimeapi package

"""
    Contains a class representing an enumeration.
"""

class ConsoleOutputProcessingMethod(object):
    """
        Determines how console output from the engine will be handled.
    """
    RedirectToRuntimeApi = 0
    """
    Console output will be captured and available to be retrieved by the GetConsoleOutput
    function.
    """
    RedirectToHost = 1
    """
    Console output will be merged into the console output of the host application.
    """
    Suppress = 2
    """
    Console output will be captured and discarded.
    """
