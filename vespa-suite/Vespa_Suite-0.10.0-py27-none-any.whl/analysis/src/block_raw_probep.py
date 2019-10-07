# Python modules
from __future__ import division

# 3rd party modules
import xml.etree.cElementTree as ElementTree

# Our modules
import vespa.analysis.src.chain_raw as chain_raw
#import vespa.analysis.src.block as block
import vespa.analysis.src.block_raw as block_raw
import vespa.common.mrs_data_raw as mrs_data_raw
import vespa.common.util.xml_ as util_xml
import vespa.common.util.misc as util_misc
from vespa.common.constants import Deflate



class BlockRawProbep(block_raw.BlockRaw):
    """ 
    This is a building block object that can be used to create a list of
    processing blocks. 
    
    This object represents the header(s) and raw data set(s) that comprise
    the first 'processing' block in the dataset.blocks list. It is sort of
    a special processing block in that it does no overt processing other 
    than the actual loading of the data into its self.data attribute.
    
    We sub-class from DataRaw base class to minimize recreation of any
    wheels.
    
    In here we also package all the functionality needed to save and recall
    these values to/from an XML node.

    We sub-class a 'Probep' version of this class so we can add an methods
    for get_/set_associated_datasets because PROBE-P Pfiles have both water
    and water suppressed data inside them.

    """
    # The XML_VERSION enables us to change the XML output format in the future 
    XML_VERSION = "1.0.0"

    
    def __init__(self, attributes=None):
        block_raw.BlockRaw.__init__(self, attributes)

        self.water_dataset = None
        self.water_dataset_id = ''


    ##### Standard Methods and Properties #####################################

    def __unicode__(self):
        lines = mrs_data_raw.DataRaw.__unicode__(self).split('\n')

        # Replace the heading line
        lines[0] = "----------- BlockRawProbep Object ------------"
        lines.append("No printable data ")

        return u'\n'.join(lines)


    def get_associated_datasets(self, is_main_dataset=True):
        """
        Returns a list of datasets associated with this object

        The 'is_main_dataset' flag allows the method to know if it is the top
        level dataset gathering associated datasets, or some dataset that is
        only associated with the top dataset. This is used to stop circular
        logic conditions where one or more datasets refer to each other.
        
        """
        # Call base class first
        datasets = block_raw.BlockRaw.get_associated_datasets(self, is_main_dataset)

        # We don't want datasets being stored in VIFF files to collide with ids
        # in memory now, should they be loaded right back in again. So, in the 
        # dataset.deflate() method, the dataset.id is changed, deflated and 
        # then restored. Here we just return the unaltered list of associated
        # datasets
        
        if self.water_dataset:
            return [self.water_dataset]
        else:
            return []


    def set_associated_datasets(self, datasets): 
        """
        In main._import_file() this only gets called for the water suppressed
        data, and the dataset passed in is the water data, so we save it and 
        all is ok. When we open a VIFF file, we get passed a list of all
        associated datasets, and again we just store it. And that too is ok
        because when the time comes to write to VIFF file again, we make sure
        that the list of associated datasets has unique elements.
        
        """
        if self.water_dataset_id == '':
            self.water_dataset = datasets[0]
        else:
            for dataset in datasets:
                if self.water_dataset_id == dataset.id:
                    self.water_dataset = dataset
                    

    def deflate(self, flavor=Deflate.ETREE):
        # Make my base class do its deflate work
        e = block_raw.BlockRaw.deflate(self, flavor)

        
        if flavor == Deflate.ETREE:
            # Alter the tag name & XML version info   
            e.tag = "block_raw_probep"
            e.set("version", self.XML_VERSION)

            # Deflate the attribs specific to this sub-class
            
            if not self.behave_as_preset:
            
                if self.water_dataset:
                    util_xml.TextSubElement(e, "water_dataset_id", self.water_dataset.id)
            
            return e

        elif flavor == Deflate.DICTIONARY:
            return e


    def inflate(self, source):
        # Make my base class do its inflate work
        block_raw.BlockRaw.inflate(self, source)
        

        # Now I inflate the attribs that are specific to this class
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element

            if not self.behave_as_preset:
                self.water_dataset_id = source.findtext("water_dataset_id")

            # Look for settings under the old name as well as the standard name.
            self.set = util_xml.find_settings(source, "block_raw_settings")
            self.set = _Settings(self.set)

        elif hasattr(source, "keys"):
            # Quacks like a dict
            for key in source.keys():
                if not self.behave_as_preset:
                    if key == "water_dataset_id":
                        self.water_dataset_id = source["water_dataset_id"]
                    
                if key == "set":
                    setattr(self, key, source[key])


        


