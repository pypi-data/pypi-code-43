# Python modules
from __future__ import division


# 3rd party modules
import xml.etree.cElementTree as ElementTree


# Our modules
import vespa.analysis.src.mrs_metinfo as mrs_metinfo
import vespa.analysis.src.mrs_user_prior_spectrum as mrs_user_prior_spectrum
import vespa.common.util.xml_ as util_xml


from vespa.common.constants import Deflate


class UserPrior(object):
    # FIXME PS needs a docstring

    # The XML_VERSION enables us to change the XML output format in the future 
    XML_VERSION = "1.0.0"
    
    def __init__(self, attributes=None):
        self.auto_b0_range_start      = 1.7
        self.auto_b0_range_end        = 3.4
        self.auto_phase0_range_start  = 1.85
        self.auto_phase0_range_end    = 2.25
        self.auto_phase1_range_start  = 2.75
        self.auto_phase1_range_end    = 3.60
        # Phase1 pivot ppm
        self.auto_phase1_pivot        = 2.01

        # Basic information input objects
        self.metinfo = mrs_metinfo.MetInfo()
        self.spectrum = mrs_user_prior_spectrum.UserPriorSpectrum()

        if attributes is not None:
            self.inflate(attributes)


    def __str__(self):
        return self.__unicode__().encode("utf-8")


    def __unicode__(self):
        lines = [ ]

        lines.append("-----------  User Prior  -----------")
        lines.append("auto_b0_range_start     = %f" % self.auto_b0_range_start)
        lines.append("auto_b0_range_end       = %f" % self.auto_b0_range_end)
        lines.append("auto_phase0_range_start = %f" % self.auto_phase0_range_start)
        lines.append("auto_phase0_range_end   = %f" % self.auto_phase0_range_end)
        lines.append("auto_phase1_range_start = %f" % self.auto_phase1_range_start)
        lines.append("auto_phase1_range_end   = %f" % self.auto_phase1_range_end)
        lines.append("auto_phase1_pivot       = %f" % self.auto_phase1_pivot)
        
        metinfo = unicode(self.metinfo).split('\n')
        lines += ['   ' + line for line in metinfo]

        spectrum = unicode(self.spectrum).split('\n')
        lines += ['   ' + line for line in spectrum]

        return u'\n'.join(lines)

    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            e = ElementTree.Element("user_prior", 
                                    {"version" : self.XML_VERSION})

            # These atttributes are all scalars and map directly to 
            # XML elements of the same name.
            for attribute in ("auto_b0_range_start", "auto_b0_range_end",
                    "auto_phase0_range_start", "auto_phase0_range_end",
                    "auto_phase1_range_start", "auto_phase1_range_end",
                    "auto_phase1_pivot", 
                    ):
                util_xml.TextSubElement(e, attribute, getattr(self, attribute))

            e.append(self.metinfo.deflate())
            e.append(self.spectrum.deflate())
            
            return e
            
        elif flavor == Deflate.DICTIONARY:
            return self.__dict__.copy()


    def inflate(self, source):
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element
            
            # floats
            for attribute in ("auto_b0_range_start",
                    "auto_b0_range_end", "auto_phase0_range_start",
                    "auto_phase0_range_end", "auto_phase1_range_start",
                    "auto_phase1_range_end", "auto_phase1_pivot",
                             ):
                setattr(self, attribute, float(source.findtext(attribute)))

            # subobjects
            self.metinfo = mrs_metinfo.MetInfo(source.find("metinfo"))

            e = source.find("user_prior_spectrum")
            self.spectrum = mrs_user_prior_spectrum.UserPriorSpectrum(e)
            

        elif hasattr(source, "keys"):
            # Quacks like a dict
            for key in source.keys():
                if hasattr(self, key):
                    setattr(self, key, source[key])


