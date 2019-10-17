# aisolution.freeflyer.runtimeapi package

"""
    Contains a class representing an enumeration.
"""

class WindowedOutputMode(object):
    """
        Determines whether output windows will be generated and whether or not they are
        used for image generation only.
    """
    NoOutputWindowSupport = 0
    """
    Output windows are not generated at runtime.
    """
    GenerateOutputWindows = 1
    """
    Output windows are generated and shown to the user.
    """
    HideMainOutputWorkspace = 2
    """
    Hides the main output workspace, but shows any unconstrained windows.
    """
    GenerateImagesOnly = 3
    """
    Output windows are generated and can be used to capture images, but not shown to
    the user.
    """
