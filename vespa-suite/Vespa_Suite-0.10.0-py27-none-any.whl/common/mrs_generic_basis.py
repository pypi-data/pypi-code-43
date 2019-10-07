# Python modules
from __future__ import division

# 3rd party modules
import xml.etree.cElementTree as ElementTree

# Our modules
import vespa.common.util.xml_ as util_xml
import vespa.common.util.time_ as util_time
from vespa.common.constants import Deflate



class GenericBasis(object):
    """
    This is the fundamental object that represents the data being
    manipulated in the Analysis program.

    """
    # The XML_VERSION enables us to change the XML output format in the future
    XML_VERSION = "1.0.0"

    def __init__(self, attributes=None):
        self.source         = ''            # either 'file' or 'experiment'
        self.source_id      = ''            # filename or uuid

        self.checks            = []         # bool, shows if a line is active
        self.values_ppm        = []
        self.values_area       = []
        self.values_phase      = []
        self.values_linewidth  = []         # in Hz for Gaussian
        self.limits_ppm        = []
        self.limits_area       = []
        self.limits_phase      = []
        self.limits_linewidth  = []         # in Hz for Gaussian

        if attributes is not None:
            self.inflate(attributes)
        else:
            self.inflate(self.default_prior())


    ##### Standard Methods and Properties #####################################

    @property
    def peak_ppm(self):
        """List of max peak locations in PPM. It's read only."""
        return list(self.values_ppm)


    def __str__(self):
        return self.__unicode__().encode("utf-8")


    def __unicode__(self):
        lines = [ ]

        lines.append("=============================================")
        lines.append("Macromolecule Object")
        lines.append("=============================================")
        lines.append("Source: "+unicode(self.source))
        lines.append("Source ID: "+unicode(self.source_id))
        if self.values_ppm:
            for i in range(len(self.values_ppm)):
                line  = u"Line (+/-Limits) ="
                line += " "+unicode(self.checks[i])
                line += " "+unicode(self.values_ppm[i])
                line += " ("+unicode(self.limits_ppm[i])+"), "
                line += " "+unicode(self.limits_area[i])
                line += " ("+unicode(self.limits_phase[i])+"), "
                line += " "+unicode(self.limits_phase[i])
                line += " ("+unicode(self.limits_area[i])+"), "
                line += " "+unicode(self.values_linewidth[i])
                line += " ("+unicode(self.limits_linewidth[i])+") "
                lines.append(line)


        # __unicode__() must return a Unicode object. In practice the code
        # above always generates Unicode, but we ensure it here.
        return u'\n'.join(lines)


    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            e = ElementTree.Element("generic_basis", {"version" : self.XML_VERSION})

            util_xml.TextSubElement(e, "source",    self.source)
            util_xml.TextSubElement(e, "source_id", self.source_id)

            for check, ppm, area, phase, lw, ppm_lim, area_lim, phase_lim, lw_lim in \
                zip(self.checks, self.values_ppm, self.values_area, self.values_phase, \
                    self.values_linewidth, self.limits_ppm, self.limits_area, \
                    self.limits_phase, self.limits_linewidth):
                line_element = ElementTree.SubElement(e, "line")
                util_xml.TextSubElement(line_element, "check",     check)
                util_xml.TextSubElement(line_element, "ppm",       ppm)
                util_xml.TextSubElement(line_element, "area",      area)
                util_xml.TextSubElement(line_element, "phase",     phase)
                util_xml.TextSubElement(line_element, "lw",        lw)
                util_xml.TextSubElement(line_element, "ppm_lim",   ppm_lim)
                util_xml.TextSubElement(line_element, "area_lim",  area_lim)
                util_xml.TextSubElement(line_element, "phase_lim", phase_lim)
                util_xml.TextSubElement(line_element, "lw_lim",    lw_lim)


            return e

        elif flavor == Deflate.DICTIONARY:
            d = { }
            attributes = ("source", "source_id" )

            for attribute in attributes:
                d[attribute] = getattr(self, attribute)

            line = []
            if self.values_ppm:
                for i in range(len(self.values_ppm)):
                    l = {}
                    l["check"]     = self.checks[i]
                    l["ppm"]       = self.values_ppm[i]
                    l["area"]      = self.values_area[i]
                    l["phase"]     = self.values_phase[i]
                    l["lw"]        = self.values_linewidth[i]
                    l["ppm_lim"]   = self.limits_ppm[i]
                    l["area_lim"]  = self.limits_area[i]
                    l["phase_lim"] = self.limits_phase[i]
                    l["lw_lim"]    = self.limits_linewidth[i]
                    line.append(l)
            d["line"] = line

            return d


    def inflate(self, source):
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element

            self.source    = source.findtext("source")
            self.source_id = source.findtext("source_id")

            self.checks            = [util_xml.BOOLEANS[val.text] for val in source.getiterator("check")]
            self.values_ppm        = [float(val.text) for val in source.getiterator("ppm")]
            self.values_area       = [float(val.text) for val in source.getiterator("area")]
            self.values_phase      = [float(val.text) for val in source.getiterator("phase")]
            self.values_linewidth  = [float(val.text) for val in source.getiterator("lw")]
            self.limits_ppm        = [float(val.text) for val in source.getiterator("ppm_lim")]
            self.limits_area       = [float(val.text) for val in source.getiterator("area_lim")]
            self.limits_phase      = [float(val.text) for val in source.getiterator("phase_lim")]
            self.limits_linewidth  = [float(val.text) for val in source.getiterator("lw_lim")]


        elif hasattr(source, "keys"):
            # Quacks like a dict
            self.source     = source["source"]
            self.source_id  = source["source_id"]
            self.checks            = []
            self.values_ppm        = []
            self.values_area       = []
            self.values_phase      = []
            self.values_linewidth  = []
            self.limits_ppm        = []
            self.limits_area       = []
            self.limits_phase      = []
            self.limits_linewidth  = []
            if "line" in source:
                for line in source["line"]:
                    self.checks.append(line["check"])
                    self.values_ppm.append(line["ppm"])
                    self.values_area.append(line["area"])
                    self.values_phase.append(line["phase"])
                    self.values_linewidth.append(line["lw"])
                    self.limits_ppm.append(line["ppm_lim"])
                    self.limits_area.append(line["area_lim"])
                    self.limits_phase.append(line["phase_lim"])
                    self.limits_linewidth.append(line["lw_lim"])



    ##### Object Specific Methods and Properties #####################################

    def default_prior(self):
        """
        Set by user to pre-populate the object if no attribute keyword
        is sent in during initialization.

        """
        checks            = [True]
        values_ppm        = [1.0]
        values_area       = [1.0]
        values_phase      = [0.0]
        values_linewidth  = [5.0]
        limits_ppm        = [0.1]
        limits_area       = [1.0]
        limits_phase      = [1.0]
        limits_linewidth  = [1.0]

        # create an element tree with prior info in it

        e = ElementTree.Element("mrs_generic_basis", {"version" : self.XML_VERSION})

        util_xml.TextSubElement(e, "source",    'default')
        util_xml.TextSubElement(e, "source_id", 'default')

        for check, \
            ppm,     area,     phase,     lw, \
            ppm_lim, area_lim, phase_lim, lw_lim in zip(checks,
                                                        values_ppm,
                                                        values_area,
                                                        values_phase,
                                                        values_linewidth,
                                                        limits_ppm,
                                                        limits_area,
                                                        limits_phase,
                                                        limits_linewidth):
            line_element = ElementTree.SubElement(e, "line")
            util_xml.TextSubElement(line_element, "check",     check)
            util_xml.TextSubElement(line_element, "ppm",       ppm)
            util_xml.TextSubElement(line_element, "area",      area)
            util_xml.TextSubElement(line_element, "phase",     phase)
            util_xml.TextSubElement(line_element, "lw",        lw)
            util_xml.TextSubElement(line_element, "ppm_lim",   ppm_lim)
            util_xml.TextSubElement(line_element, "area_lim",  area_lim)
            util_xml.TextSubElement(line_element, "phase_lim", phase_lim)
            util_xml.TextSubElement(line_element, "lw_lim",    lw_lim)

        return e


    def get_rows(self):
        res = []
        for i in range(len(self.values_ppm)):

            t = (self.checks[i], \
                 self.values_ppm[i], self.values_area[i], self.values_phase[i], self.values_linewidth[i], \
                 self.limits_ppm[i], self.values_area[i], self.limits_phase[i], self.limits_linewidth[i])
            res.append(t)

        return res


    def get_row(self, indx):
        if indx >= len(self.values_ppm) or indx < 0:
            return None
        t = (self.checks[i], \
             self.values_ppm[indx], self.values_phase[indx], self.values_linewidth[indx], \
             self.limits_ppm[indx], self.limits_phase[indx], self.limits_linewidth[indx])

        return t


    def set_values(self, vals):
        # vals are a list of dicts, each dict will have a
        # value for value_ppm, value_area ... limit_lwhz

        self.checks            = []
        self.values_ppm        = []
        self.values_area       = []
        self.values_phase      = []
        self.values_linewidth  = []         # in Hz for Gaussian
        self.limits_ppm        = []
        self.limits_area       = []
        self.limits_phase      = []
        self.limits_linewidth  = []         # in Hz for Gaussian

        for line in vals:
            self.checks.append(line["check"])
            self.values_ppm.append(line["value_ppm"])
            self.values_area.append(line["value_area"])
            self.values_phase.append(line["value_phase"])
            self.values_linewidth.append(line["value_lwhz"])
            self.limits_ppm.append(line["limit_ppm"])
            self.limits_area.append(line["limit_area"])
            self.limits_phase.append(line["limit_phase"])
            self.limits_linewidth.append(line["limit_lwhz"])


#--------------------------------------------------------------------
# test code

def _test():

    test = GenericBasis()

    class_name = test.__class__.__name__
    filename = "_test_output_"+class_name+".xml"
    element = test.deflate()
    root = ElementTree.Element("_test_"+class_name, { "version" : "1.0.0" })
    util_xml.TextSubElement(root, "timestamp", util_time.now().isoformat())
    root.append(element)
    tree = ElementTree.ElementTree(root)
    tree.write(filename, "utf-8")

    tom = 10


if __name__ == '__main__':
    _test()

