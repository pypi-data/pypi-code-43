# Python modules
from __future__ import division

# 3rd party modules
import wx

# Our modules
import vespa.common.constants as constants

def is_oc(tab_or_transformation):
    """Given a tab or a transformation, returns True if the tab's
    transformation (or the transformation itself) is an optimal control
    transformation, False otherwise.

    This isn't particularly tricky, it just encapsulates a question we need
    to ask in a few different places.
    """
    type_ = None

    # All of our tabs inherit from wx.Panel
    if isinstance(tab_or_transformation, wx.Panel):
        # It's a tab
        tab = tab_or_transformation
        if hasattr(tab, "transform") and tab.transform:
            type_ = tab.transform.type
    else:
        # It's a transformation
        type_ = tab_or_transformation.type

    return (type_ == constants.TransformationType.OCN)
