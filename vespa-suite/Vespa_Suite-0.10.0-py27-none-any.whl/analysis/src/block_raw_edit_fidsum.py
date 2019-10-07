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



class BlockRawEditFidsum(block_raw.BlockRaw):
    """ 
    This is a building block object that can be used to create a list of
    processing blocks. 
    
    This object represents the header(s) and raw data set(s) that comprise
    the first 'processing' block in the dataset.blocks list. It is sort of
    a special processing block in that it does no overt processing other 
    than the actual loading of the data into its self.data attribute.
    
    We sub-class from DataRaw base class to minimize recreation of any
    wheels, but to also leave us the flexibility of extending this class 
    in the future for any 'special children' types of data loading.
    
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

        self.data_on  = None
        self.data_off = None
        self.data_sum = None
        self.data_dif = None
        self.data_on_id  = ''
        self.data_off_id = ''
        self.data_sum_id = ''
        self.data_dif_id = ''


    ##### Standard Methods and Properties #####################################

    def __unicode__(self):
        lines = mrs_data_raw.DataRaw.__unicode__(self).split('\n')

        # Replace the heading line
        lines[0] = "----------- BlockRawEditFidsum Object ------------"
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
        if is_main_dataset:
            val = [self.data_on, self.data_off, self.data_sum, self.data_dif]
        else:
            val = []
        
        return val


    def set_associated_datasets(self, datasets): 
        """
        In main._import_file() this only gets called for the water suppressed
        data, and the dataset passed in is the water data, so we save it and 
        all is ok. When we open a VIFF file, we get passed a list of all
        associated datasets, and again we just store it. And that too is ok
        because when the time comes to write to VIFF file again, we make sure
        that the list of associated datasets has unique elements.
        
        """
        if self.data_on_id == '':
            self.data_on = datasets[0]
        else:
            for dataset in datasets:
                if self.data_on_id == dataset.id:
                    self.data_on = dataset

        if self.data_off_id == '':
            self.data_off = datasets[1]
        else:
            for dataset in datasets:
                if self.data_off_id == dataset.id:
                    self.data_off = dataset

        if self.data_sum_id == '':
            self.data_sum = datasets[2]
        else:
            for dataset in datasets:
                if self.data_sum_id == dataset.id:
                    self.data_sum = dataset

        if self.data_dif_id == '':
            self.data_dif = datasets[3]
        else:
            for dataset in datasets:
                if self.data_dif_id == dataset.id:
                    self.data_dif = dataset
                    

    def deflate(self, flavor=Deflate.ETREE):
        
        # Make my base class do its deflate work
        e = block_raw.BlockRaw.deflate(self, flavor)

        if flavor == Deflate.ETREE:
            # Alter the tag name & XML version info   
            e.tag = "block_raw_edit_fidsum"
            e.set("version", self.XML_VERSION)
            
            # Deflate the attribs specific to this sub-class
            
            if not self.behave_as_preset:
            
                # In the next few lines, we *have* to save the uuid values from 
                # the actual objects rather than from the attributes above, in 
                # order for the associated dataset uuids to reflect the new ids
                # that are given in the top level dataset. Associated datasets are
                # given new temporary uuid values so that if the main dataset is 
                # saved and immediately loaded back in, we do not get collisions
                # between the newly opened datasets and already existing ones.
                if self.data_on:
                    util_xml.TextSubElement(e, "data_on_id",  self.data_on.id)
                if self.data_off:
                    util_xml.TextSubElement(e, "data_off_id", self.data_off.id)
                if self.data_sum:
                    util_xml.TextSubElement(e, "data_sum_id", self.data_sum.id)
                if self.data_dif:
                    util_xml.TextSubElement(e, "data_dif_id", self.data_dif.id)

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
            
                self.data_on_id  = source.findtext("data_on_id")
                self.data_off_id = source.findtext("data_off_id")
                self.data_sum_id = source.findtext("data_sum_id")
                self.data_dif_id = source.findtext("data_dif_id")
            
            # Look for settings under the old name as well as the standard name.
            self.set = util_xml.find_settings(source, "block_raw_edit_fidsum_settings")
            self.set = block_raw._Settings(self.set)

        elif hasattr(source, "keys"):
            # Quacks like a dict
            for key in source.keys():
                if not self.behave_as_preset:
                    if key == "data_on_id":
                        self.data_on_id = source["data_on_id"]
                    if key == "data_off_id":
                        self.data_off_id = source["data_off_id"]
                    if key == "data_sum_id":
                        self.data_sum_id = source["data_sum_id"]
                    if key == "data_dif_id":
                        self.data_dif_id = source["data_dif_id"]

                if key == "set":
                    setattr(self, key, source[key])


        


