# aisolution.freeflyer.runtimeapi package

"""
    Contains a class representing an enumeration.
"""

class TimeSpanMode(object):
    """
        Determines whether the specified FreeFlyer script will be run in millisecond mode
        or nanosecond mode.
    """
    Millisecond = 0
    """
    Run the script in millisecond mode.
    """
    Nanosecond = 1
    """
    Run the script in nanosecond mode.
    """
