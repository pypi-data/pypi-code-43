# Python modules
from __future__ import division
import xml.etree.cElementTree as ElementTree
import copy

# 3rd party modules
import numpy as np

# Our modules
import vespa.common.constants as constants
from vespa.common.rfp_machine_settings import MachineSettings
from vespa.common.rfp_master_parameters import MasterParameters
import vespa.common.rfp_transformation_factory as rfp_transformation_factory
from vespa.common.constants import Deflate
import vespa.common.util.time_ as util_time
import vespa.common.util.xml_ as util_xml
import vespa.public.minimalist_pulse as minimalist_pulse

#1234567890123456789012345678901234567890123456789012345678901234567890123456789

# _NBSP is a Unicode Non-Breaking SPace. Used in HTML output.
_NBSP = u"\xA0"

class PulseProject(object):
    """
    A container to hold the final pulse, frequency profile (and any gradients),
    as well as the provenance of the pulse, including all the prior
    transformations (and parameters) and their results.
    """
    # The XML_VERSION enables us to change the XML output format in the future 
    XML_VERSION = "1.0.0"

    def __init__(self, attributes=None):
        self.name             = ''
        self.id               = '' # uuid
        self.is_public        = False
        self.creator          = ''
        self.created          = util_time.now()
        self.comment          = ''  # User's note(s) for describing this pulse.

        self.machine_settings  = MachineSettings()
        self.master_parameters = MasterParameters()

        self.transformations  = []  # This replaces provenance,
                                    # and includes it's own results.
        # referrers is a (possibly empty) list of 2-tuples of (id, name).
        # This contains all of the pulse sequences that refer to this 
        # pulse project.
        self.referrers = [ ]

        if attributes is not None:
            self.inflate(attributes)

        if self.comment is None:
            self.comment = ""


    @property
    def create_transformation(self):
        """Returns the create transformation if one exists, None otherwise."""
        return self.transformations[0] if len(self.transformations) else None


    @property
    def has_results(self):
        return any([bool(transformation.result) for transformation 
                                                in self.transformations])

    @property
    def is_frozen(self):
        """A pulse project is frozen when it's public or when one or more
        pulse sequences refers to it."""
        return bool(self.referrers) or self.is_public


    def __str__(self):
        return self.__unicode__().encode("utf-8")


    def __unicode__(self):
        lines = [ ]
        id_ = self.id if self.id else ""
        lines.append("--- Pulse Project %s ---" % id_)
        lines.append("Name: %s" % self.name)
        lines.append("Public: %s" % ("True" if self.is_public else "False"))
        s = self.created.isoformat() if self.created else "[empty]"
        lines.append("Created: %s" % s)
        lines.append("Comment (abbr.): %s" % self.comment[:40])
        lines.append("Creator: %s" % self.creator)        
        
        # Present a summary of the machine settings
        machine_type = self.machine_settings.machine_type
        if machine_type in constants.MachineType.ALL:
            machine_type = machine_type["display"]
        machine_type += (" %.3fT" % self.machine_settings.field_strength)

        lines.append("Mach. Setngs: %s" % machine_type)
        lines.append("%d Transformations: (not listed)" % len(self.transformations))

        # __unicode__() must return a Unicode object.
        return u'\n'.join(lines)
        

    def as_html(self):
        """Returns this project rendered as a string of HTML suitable for
        display in a wx.html control."""
        # Note that this is being built for the wx.html control which has
        # no CSS support so our formatting options here are pretty limited.
        html = ElementTree.Element("html")
        body = ElementTree.SubElement(html, "body")
        
        h1 = util_xml.TextSubElement(body, "h1", "Pulse Project ")
        # Name is italicized
        util_xml.TextSubElement(h1, "i", self.name)
        
        if self.id:
            p = util_xml.TextSubElement(body, "p", "UUID: ")
            util_xml.TextSubElement(p, "tt", self.id)
            # After UUID we add an "empty" paragraph to provide some space
            # between the UUID and the next element. Since completely empty
            # paragraphs tend to get ignored by HTML renderers, we add a 
            # <p> that contains a non-breaking space.
            util_xml.TextSubElement(body, "p", _NBSP)

        # Basic project attrs go into a table.
        table = ElementTree.SubElement(body, "table", {"border" : "1px"})
        tbody = ElementTree.SubElement(table, "tbody")

        lines = [ ]
            
        lines.append( ("Public",  "%s" % ("True" if self.is_public else "False")))
        if self.created:
            timestamp = self.created.strftime(util_time.DISPLAY_TIMESTAMP_FORMAT)
            lines.append( ("Created", "%s" % timestamp))
        lines.append( ("Creator", "%s" % self.creator))
        
        for line in lines:
            description, data = line
            tr = ElementTree.SubElement(tbody, "tr")
            util_xml.TextSubElement(tr, "td", description)
            util_xml.TextSubElement(tr, "td", data, { "align" : "right" })
            
        if self.comment:
            util_xml.TextSubElement(body, "h2", "Comment")
            util_xml.TextSubElement(body, "p", self.comment)

        # The machine settings object renders itself
        util_xml.TextSubElement(body, "h2", "Machine Settings")
        body.append(self.machine_settings.as_html())

        # The master params object renders itself
        util_xml.TextSubElement(body, "h2", "Master Parameters")
        body.append(self.master_parameters.as_html())
        
        # For now, only transformation titles are listed. Maybe later we'll
        # want to add for info about each transformation, and if we do that
        # we should probably let the transformation objects render themselves.
        util_xml.TextSubElement(body, "h2", "Transformations")
        ol = ElementTree.SubElement(body, "ol")
        for transformation in self.transformations:
            util_xml.TextSubElement(ol, "li", transformation.type["display"])
            
        # The two commented-out lines below are handy for debugging, should 
        # you need that. =)
        # util_xml.indent(html)
        # print  ElementTree.tostring(html)

        return ElementTree.tostring(html)


    def clone(self):
        """
        Creates & returns a new pulse_project that looks just like this one, 
        but with a different value for created.  The id (uuid) should be modified
        externally.
        """
        pulse_project = copy.deepcopy(self)
        pulse_project.id = None
        pulse_project.created = util_time.now()
        pulse_project.is_public = False
        
        return pulse_project
    

    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            # ppe = pulse project element
            ppe = ElementTree.Element("pulse_project", 
                                      { "id" : self.id,
                                        "version" : self.XML_VERSION})

            for attribute in ("name", "created", "creator", "comment", ):
                util_xml.TextSubElement(ppe, attribute, getattr(self, attribute))

            ppe.append(self.machine_settings.deflate(flavor))

            ppe.append(self.master_parameters.deflate(flavor))

            for transformation in self.transformations:
                ppe.append(transformation.deflate(flavor))

            return ppe

        elif flavor == constants.Deflate.DICTIONARY:
            d = self.__dict__.copy()
            
            d["machine_settings"] = self.machine_settings.deflate(flavor)
            d["master_parameters"] = self.master_parameters.deflate(flavor)
            
            d["transformations"] = [transformation.deflate(flavor) for transformation
                                            in self.transformations]
            
            return d
        

    def delete_transformation(self, index):
        '''
        Deletes the transformation at the given position in the list.
        The index has to be >= 0 
        '''
        length = len(self.transformations)
        
        if index >= length or index < 0:
            return
        
        self.transformations.pop(index)
        
        length = len(self.transformations)
        
        return


    def get_pulse(self, index=-1):
        """Given an index into the list of transformations in this project,
        returns a MinimalistPulse representation of that transformation. 
        If the project has no transformations, or the indicated 
        transformation has no result, None is returned.
        
        The index defaults to -1, which refers to the last transformation.
        It's used directly in the list of transformations, so you can pass
        e.g. -2 to get the next-to-last transformation, etc. Passing an
        index >= the number of transformations raises an IndexError.

        The waveform in the object that's returned is a copy of the list 
        inside the pulse project. Changes to the list returned from here 
        won't affect the pulse project.
        """
        pulse = None
        
        if self.transformations:
            transformation = self.transformations[index]
            
            if transformation.result and transformation.result.rf:
                pulse = minimalist_pulse.MinimalistPulse()
                pulse.name = self.name
                # Note that we make a copy of the values. We don't return
                # a reference to the values in the pulse design so that 
                # changes to this minialist pulse won't be reflected in the
                # pulse design.
                pulse.dwell_time     = transformation.result.dwell_time
                pulse.rf_waveform    = transformation.result.rf.waveform[:]
                pulse.rf_xaxis       = transformation.result.rf.waveform_x_axis[:]
                # gradient and grad_xaxis default to None
                
        return pulse


    def get_bandwidth(self, index=-1):
        """Given an index into the list of transformations in this project,
        returns the bandwidth of that transformation. If there is no 
        bandwidth parameter in this transform, it searches backwards through
        the transformation list until it finds one. Otherwise it returns None.
        
        If the project has no transformations, None is returned.
        
        The index defaults to -1, which refers to the last transformation.
        It's used directly in the list of transformations, so you can pass
        e.g. -2 to get the next-to-last transformation, etc. Passing an
        index >= the number of transformations raises an IndexError.

        """
        bandwidth = None
        
        ntrans = len(self.transformations)
        
        if abs(index) > ntrans:
            return bandwidth
        
        for indx in reversed(range(ntrans + index + 1)):
            transformation = self.transformations[indx]
            if hasattr(transformation.parameters, 'bandwidth'):
                bandwidth = transformation.parameters.bandwidth
                break
        
        return bandwidth
                
                
    def get_tip_angle(self, index=-1):
        """Given an index into the list of transformations in this project,
        returns the tip angle of that transformation. If there is no 
        tip_angle parameter in this transform, it searches backwards through
        the transformation list until it finds one. Otherwise it returns None.
        
        If the project has no transformations, None is returned.
        
        The index defaults to -1, which refers to the last transformation.
        It's used directly in the list of transformations, so you can pass
        e.g. -2 to get the next-to-last transformation, etc. Passing an
        index >= the number of transformations raises an IndexError.

        """
        tip_angle = None
        
        ntrans = len(self.transformations)
        
        if abs(index) > ntrans:
            return tip_angle
        
        for indx in reversed(range(ntrans + index + 1)):
            transformation = self.transformations[indx]
            if hasattr(transformation.parameters, 'tip_angle'):
                tip_angle = transformation.parameters.tip_angle
                break
        
        return tip_angle            
            

    def get_previous_result(self, transform):
        idx = self.transformations.index(transform)
        if idx > 0:
            return self.transformations[idx-1].result
        else:
            return None


    def inflate(self, source):
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element
            self.id = source.get("id")
            self.name = source.findtext("name")
            self.creator = source.findtext("creator")
            self.created = source.findtext("created")
            self.created = util_time.datetime_from_iso(self.created)
            self.comment = source.findtext("comment")
            
            # We need an explicit test for None here; casting to bool doesn't
            # work as expected. See "caution" at the end of this section:
            # http://docs.python.org/release/2.6.6/library/xml.etree.elementtree.html#the-element-interface
            machine_settings_element = source.find("machine_settings")
            if machine_settings_element is not None:
                self.machine_settings = MachineSettings(machine_settings_element)

            # We need an explicit test for None here; casting to bool doesn't
            # work as expected. See "caution" at the end of this section:
            # http://docs.python.org/release/2.6.6/library/xml.etree.elementtree.html#the-element-interface
            master_parameters_element = source.find("master_parameters")
            if master_parameters_element is not None:
                self.master_parameters = MasterParameters(master_parameters_element)

            transformation_elements = source.findall("transformation")
            if transformation_elements:
                # This function alias just makes the list comprehension below readable.
                f = rfp_transformation_factory.transformation_from_element
                self.transformations = [f(element) for element in transformation_elements]
        elif hasattr(source, "keys"):
            # Quacks like a dict
            for key in source.keys():
                if hasattr(self, key):
                    setattr(self, key, source[key])


    def update_results(self):
        """Forces an update for the results on each transformation."""
        calc_resolution = self.master_parameters.calc_resolution

        for transformation in self.transformations:
            if transformation.result:
                transformation.result.update_profiles(calc_resolution)

    


