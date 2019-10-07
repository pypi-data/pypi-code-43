# Python modules
from __future__ import division
import xml.etree.cElementTree as ElementTree

# 3rd party modules
import numpy as np

# Our modules
import vespa.common.util.xml_ as util_xml

from vespa.common.constants import Deflate



class PriorMetabolite(object):
    """
    A prior metabolite consisting of ppm, area and phase values in correlated
    numpy arrays and additional identifying information. The length of each 
    array is the same and the Nth element of any array is associated with 
    the Nth element of the other two arrays.
    
    """
    
    # The XML_VERSION enables us to change the XML output format in the future 
    XML_VERSION = "1.0.0"

    def __init__(self, attributes=None):
        self.spins     = 0
        # dims are in the Simulation-Experiment sense
        self.dims      = ['',0,0,0]
        # group is currently unused but we're treating it as text
        self.group     = []
        self.ppms      = []
        self.areas     = []
        self.phases    = []
    
        if attributes is not None:
            self.inflate(attributes)


    ##### Standard Methods and Properties #####################################

    @property
    def name(self):
        return self.dims[0]
        

    def __str__(self):
        return self.__unicode__().encode("utf-8")


    def __unicode__(self):
        lines = [ ]
        lines.append("=============================================")
        lines.append("PriorMetabolite Object (%d lines)" % len(self.ppms))
        lines.append("=============================================")
        
        lines.append("Name: %s" % self.name)
        lines.append("Spins: %s" % unicode(self.spins))
        
        if self.ppms:
            for i in range(len(self.ppms)):
                line  = u"Line " +unicode(i)+" : "
                line += " PPM="  +unicode(self.ppms[i])
                line += " Area=" +unicode(self.areas[i])
                line += " Phase="+unicode(self.phases[i])
                line += " Loop1="+unicode(self.dims[1])
                line += " Loop2="+unicode(self.dims[2])
                line += " Loop3="+unicode(self.dims[3])
                lines.append(line)
        
        # __unicode__() must return a Unicode object. In practice the code
        # above always generates Unicode, but we ensure it here.
        return u'\n'.join(lines)


    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            e = ElementTree.Element("prior_metabolite", {"version" : self.XML_VERSION})
            
            util_xml.TextSubElement(e, "name", self.name)
            for dim in self.dims[1:]:
                util_xml.TextSubElement(e, "dim", dim)
            util_xml.TextSubElement(e, "spins", self.spins)
            
            groups = self.group
            ppms   = self.ppms
            areas  = self.areas
            phases = self.phases
            
            # We're currently not using groups, so it never changes from 
            # its default value of [ ]. If we don't change that, the call to 
            # zip() below will return an empty list so here we hack groups 
            # to be a bunch of blanks.
            if len(groups) != len(ppms):
                groups = [''] * len(ppms)
                 
            for group, ppm, area, phase in zip(groups, ppms, areas, phases):
                line_element = ElementTree.SubElement(e, "line")
                util_xml.TextSubElement(line_element, "group", group)
                util_xml.TextSubElement(line_element, "ppm",   ppm)
                util_xml.TextSubElement(line_element, "area",  area)
                util_xml.TextSubElement(line_element, "phase", phase)

            return e
            
        elif flavor == Deflate.DICTIONARY:
            d = { }
            
            for attribute in ("spins", "group", "ppms", "areas", "phases", ):
                d[attribute] = getattr(self, attribute)
            
            d["name"] = self.name
            d["dims"] = self.dims[1:]
            
            return d
            

            
    def inflate(self, source):
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element
            dims = [float(dim.text) for dim in source.findall("dim")]
            self.dims   = [source.findtext("name")] + dims
            self.spins  = int(source.findtext("spins"))
            self.group  = [group.text        for group in source.getiterator("group")]
            self.ppms   = [float(ppm.text)   for ppm   in source.getiterator("ppm")]
            self.areas  = [float(area.text)  for area  in source.getiterator("area")]
            self.phases = [float(phase.text) for phase in source.getiterator("phase")]
        
        elif hasattr(source, "keys"):
            # Quacks like a dict
            for key in source.keys():
                # the "name" key gets a little special handling
                if hasattr(self, key) and (key != "name"):
                    setattr(self, key, source[key])
            
            self.dims = [source["name"]] + source["dims"]


    def sim_display(self, dims):
        lines = [ ]
        for i in range(len(self.ppms)):
            line = "%s\t%s\t%s\t%s\t" % tuple(dims)
            line += (str(i)+'\t'+str(self.ppms[i])+'\t'+str(self.areas[i])+'\t'+str(self.phases[i]))
            lines.append(line)
        
        return '\n'.join(lines)                


    def get_rows(self):
        lines = []
        for ppm, area, phase in zip(self.ppms,self.areas,self.phases):
            lines.append([ppm,area,phase])
        
        return lines                


#--------------------------------------------------------------------
# test code

def _test():

    bob = PriorMetabolite()
    
    tom = 10  


if __name__ == '__main__':
    _test()