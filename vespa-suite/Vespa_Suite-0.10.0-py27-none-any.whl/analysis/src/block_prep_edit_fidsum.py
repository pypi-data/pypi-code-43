# Python modules
from __future__ import division

# 3rd party modules
import xml.etree.cElementTree as ElementTree

# Our modules
import vespa.analysis.src.block_prep_fidsum as block_prep_fidsum



from vespa.common.constants import Deflate



class BlockPrepEditFidsum(block_prep_fidsum.BlockPrepFidsum):
    """ 
    This is a building block object that can be used to create a list of
    processing blocks. 
    
    This object represents pre-processing of the raw data from the first 
    block ('raw') in the dataset.blocks list. 
    
    We sub-class from BlockPrepFidsum base class to minimize recreating
    wheels.
    
    In here we also package all the functionality needed to save and recall
    these values to/from an XML node.

    """
    # The XML_VERSION enables us to change the XML output format in the future 
    XML_VERSION = "1.0.0"

    
    def __init__(self, attributes=None):
        """ Set up standard functionality of the base class """
        
        block_prep_fidsum.BlockPrepFidsum.__init__(self, attributes)
        


    ##### Standard Methods and Properties #####################################

    def __unicode__(self):

        lines = block_prep_fidsum.BlockPrepFidsum.__unicode__(self).split('\n')

        lines[0] = "----------- DataPrepEditFidsum Object ------------"
        lines.append("Data shape                    : %s" % str(self.dims))

        return u'\n'.join(lines)


    def deflate(self, flavor=Deflate.ETREE):

        e = block_prep_fidsum.BlockPrepFidsum.deflate(self, flavaor)

        if flavor == Deflate.ETREE:
            # Alter the tag name & XML version info   
            e.tag = "block_prep_edit_fidsum"
            e.set("version", self.XML_VERSION)
            return e

        elif flavor == Deflate.DICTIONARY:
            return e



    ##### Private Methods #####################################

    
