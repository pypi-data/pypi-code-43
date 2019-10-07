# Python modules
from __future__ import division
import xml.etree.cElementTree as ElementTree

# Our Modules
import vespa.common.constants as constants
import vespa.common.util.xml_ as util_xml
import vespa.common.rfp_result as rfp_result

from vespa.common.constants import Deflate


class Transformation(object):
    """
    Transformation: Abstract class. Subclasses of this class will be used in the
    provenance, which consists of two lists: Transformations and Results.  
    
    """
    # The XML_VERSION enables us to change the XML output format in the future 
    XML_VERSION = "1.0.0"

    def __init__(self, type_):
        
        self.type = type_
        self.transform_name = ''
        self.parameters = None
        self.result = None      # result is an rfp_result.Result object


    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            # e = transformation_element
            e = ElementTree.Element("transformation", 
                                      {"version" : self.XML_VERSION})
            
            type_ = self.type["db"] if self.type else ""
            util_xml.TextSubElement(e, "type", type_)
            
            e.append(self.parameters.deflate(flavor))
            
            if self.result:
                e.append(self.result.deflate(flavor))
            
            return e
        elif flavor == Deflate.DICTIONARY:
            return self.__dict__.copy()
            

    def inflate(self, source):
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element
            
            self.type = source.findtext("type")
            # I import this here rather than at the top of the file in 
            # order to avoid circular imports.
            import rfp_transformation_factory
            
            _, parameters_ctor = rfp_transformation_factory.CONSTRUCTORS[self.type]

            self.type = constants.TransformationType.get_type_for_value(self.type, "db")
                
            parameters_element = source.find("parameters")
            
            self.parameters = parameters_ctor(parameters_element)
            
            # We need an explicit test for None here; casting to bool doesn't
            # work as expected. See "caution" at the end of this section:
            # http://docs.python.org/release/2.6.6/library/xml.etree.elementtree.html#the-element-interface
            result = source.find("result")
            if result is not None:
                self.result = rfp_result.Result(result)
        elif hasattr(source, "keys"):
            # Quacks like a dict
            raise NotImplementedError
