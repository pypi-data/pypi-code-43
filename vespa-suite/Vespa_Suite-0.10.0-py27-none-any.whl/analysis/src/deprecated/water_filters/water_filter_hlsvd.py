# Python imports
from __future__ import division
import xml.etree.cElementTree as ElementTree

# 3rd party imports
import numpy as np

# Vespa imports
# These imports take advantage of the fact that Python adds analysis/src to
# sys.path when analysis/src/main.py is run.

import water_filters.water_filter as water_filter
import functors.functor as functor
import vespa.common.util.xml_ as util_xml
import vespa.common.util.misc as util_misc

from vespa.common.constants import Deflate




#----------------------------------------------------------
# HLSVD constants

class FilterConstants(object):

    THRESH_MIN_HZ =-500
    THRESH_MAX_HZ = 500
    THRESH_DEFAULT = 11
    THRESH_APPLY = False


def _create_panel(parent, tab, filter_):
    # These imports are inline so that wx doesn't get imported unless we
    # receive an explicit request for a GUI object.
    import panel_water_filter_hlsvd

    return panel_water_filter_hlsvd.PanelWaterFilterHlsvd(parent, tab, filter_)



class WaterFilterHlsvd(water_filter.WaterFilter):
    XML_VERSION = "1.0.0"

    ID = "14023031-ad45-4662-a89c-4e35d8732244"

    DISPLAY_NAME = 'SVD Filter'

    def __init__(self, attributes=None):
        self.threshold = FilterConstants.THRESH_DEFAULT
        self.apply_as_water_filter = FilterConstants.THRESH_APPLY

        self.functor = _FunctWaterFilterHlsvd()

        self._panel = None

        if attributes is not None:
            self.inflate(attributes)


    def __str__(self):
        return self.__unicode__().encode("utf-8")


    def __unicode__(self):
        lines = [ ]
        lines.append("------  WaterFilterHlsvd  --------------")
        lines.append("threshold                  : " + unicode(self.threshold))
        lines.append("apply_as_water_filter      : " + unicode(self.apply_as_water_filter))

        # __unicode__() must return a Unicode object. In practice the code
        # above always generates Unicode, but we ensure it here.
        lines =  u'\n'.join(lines)

        return lines


    # I override my base class' implementation of this since this is the
    # HLSVD filter.
    @property
    def is_hlsvd(self):
        return True


    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            # Get my base class to deflate itself
            e = water_filter.WaterFilter.deflate(self, flavor)

            # handle the things that are specific to this class.
            util_xml.TextSubElement(e, "threshold", self.threshold)
            util_xml.TextSubElement(e, "apply_as_water_filter", self.apply_as_water_filter)

            return e

        elif flavor == Deflate.DICTIONARY:
            raise NotImplementedError


    def inflate(self, source):
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element

            # Get my base class to inflate itself
            e = water_filter.WaterFilter.inflate(self, source)

            # Now inflate the things specific to this class
            self.apply_as_water_filter = util_xml.BOOLEANS[source.findtext("apply_as_water_filter")]

            self.threshold = int(source.findtext("threshold"))

        elif hasattr(source, "keys"):
            raise NotImplementedError


    def get_panel(self, parent, tab):
        """Returns the panel (GUI) associated with this filter"""
        # self._panel is only created as needed.
#        if not self._panel:
#            self._panel = _create_panel(parent, tab, self)

        return self._panel


class _FunctWaterFilterHlsvd(functor.Functor):
    """
    This is a building block object that can be used to create a
    processing chain for time domain to frequency domain spectral MRS
    data processing.

    """

    def __init__(self):

        self.threshold = FilterConstants.THRESH_DEFAULT
        self.apply_as_water_filter = FilterConstants.THRESH_APPLY

        self.attribs = ("threshold",
                        "apply_as_water_filter",
                       )


    ##### Standard Methods and Properties #####################################


    def update(self, other):
        filter_ = other.water_handler.active
        for attr in self.attribs:
            util_misc.safe_attribute_set(filter_, self, attr)

    def algorithm(self, chain):
        """
        The chain object contains both the array of FIDs that HLSVD generates
        and the array of summed FIDs that represent only the lines selected by
        checking the boxes in the list on the HLSVD tab. These are the two
        choices that can be applied in this filter.

        If the user has checked the Apply Threshold box on the Spectral tab's
        water filter, then the array of FIDs is parsed to create a water
        filter from all lines whose frequency is >= the threshold value. The
        use of this setting does NOT affect the check boxes on the HLSVD tab.

        If the Apply Threshold box is not checked, then the array of summed
        FIDs set from the HLSVD tab is used as-is. In this case the value in
        the water threshold field is ignored.

        """
        # the HLSVD results were calculated aligned with the original raw time
        # data, no frequency shift applied. As we apply any frequency shift to
        # the raw data, we must also shift the HLSVD fids. However, if we use
        # the Spectral tab's cutoff to determine which HLSVD fids to remove,
        # then we need to apply the threshold to HLSVD frequencies that have
        # had the frequency shift added to them. And in the end, the HLSVD fids
        # need to have a phase roll applied to line them up with the raw data.

        chain.data = chain.data - chain.svd_fids_checked





