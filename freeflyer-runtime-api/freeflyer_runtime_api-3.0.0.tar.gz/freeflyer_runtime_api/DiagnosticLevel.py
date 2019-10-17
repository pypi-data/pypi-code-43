# aisolution.freeflyer.runtimeapi package

"""
    Contains a class representing an enumeration.
"""

class DiagnosticLevel(object):
    """
        The level of detail to use when generating diagnostic messages.
    """
    Default = 0
    """
    Use the default diagnostic level.
    """
    IncludeSourceDetails = 1
    """
    Report additional information useful when corresponding with technical support.
    """
