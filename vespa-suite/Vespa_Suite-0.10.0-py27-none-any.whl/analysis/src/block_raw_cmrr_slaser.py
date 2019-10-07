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



class BlockRawCmrrSlaser(block_raw.BlockRaw):
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

        self.data_coil_combine      = None
        self.data_ecc1              = None
        self.data_water1            = None
        self.data_metab64           = None
        self.data_ecc2              = None
        self.data_water2            = None
        self.data_coil_combine_id   = ''
        self.data_ecc1_id           = ''
        self.data_water1_id         = ''
        self.data_metab64_id        = ''
        self.data_ecc2_id           = ''
        self.data_water2_id         = ''


    ##### Standard Methods and Properties #####################################

    def __unicode__(self):
        lines = mrs_data_raw.DataRaw.__unicode__(self).split('\n')

        # Replace the heading line
        lines[0] = "----------- BlockRawCmrrSlaser Object ------------"
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
            assoc = []
            for item in [self.data_coil_combine, self.data_ecc1, self.data_water1, self.data_metab64, self.data_ecc2, self.data_water2]:
                if item is not None:
                    assoc.append(item)
            return assoc
        else:
            return []


    def set_associated_datasets(self, datasets): 
        """
        In main._import_file() this gets called with a list of datasets with
        known positions, so we can just set them by list order.
        
        If the IDs are set in here already, as they may be if we are inflating
        this object with a list of associated datasets, we want to be sure that
        the ID set for a given attribute matches one of the dataset.id values
        for an associated dataset in the 'datasets' list before we assign it
        to an attribute.
        
        """
        if self.data_coil_combine_id == '':
            self.data_coil_combine = datasets[0]
        else:
            for dataset in datasets:
                if self.data_coil_combine_id == dataset.id:
                    self.data_coil_combine = dataset

        if self.data_ecc1_id == '':
            self.data_ecc1 = datasets[1]
        else:
            for dataset in datasets:
                if self.data_ecc1_id == dataset.id:
                    self.data_ecc1 = dataset

        if self.data_water1_id == '':
            self.data_water1 = datasets[2]
        else:
            for dataset in datasets:
                if self.data_water1_id == dataset.id:
                    self.data_water1 = dataset

        if self.data_metab64_id == '':
            self.data_metab64 = datasets[3]
        else:
            for dataset in datasets:
                if self.data_metab64_id == dataset.id:
                    self.data_metab64 = dataset
                    
        if self.data_ecc2_id == '':
            self.data_ecc2 = datasets[4]
        else:
            for dataset in datasets:
                if self.data_ecc2_id == dataset.id:
                    self.data_ecc2 = dataset

        if self.data_water2_id == '':
            self.data_water2 = datasets[5]
        else:
            for dataset in datasets:
                if self.data_water2_id == dataset.id:
                    self.data_water2 = dataset


    def deflate(self, flavor=Deflate.ETREE):
        
        # Make my base class do its deflate work
        e = block_raw.BlockRaw.deflate(self, flavor)

        if flavor == Deflate.ETREE:
            # Alter the tag name & XML version info   
            e.tag = "block_raw_cmrr_slaser"
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
                if self.data_coil_combine:
                    util_xml.TextSubElement(e, "data_coil_combine_id",  self.data_coil_combine.id)
                if self.data_ecc1:
                    util_xml.TextSubElement(e, "data_ecc1_id", self.data_ecc1.id)
                if self.data_water1:
                    util_xml.TextSubElement(e, "data_water1_id", self.data_water1.id)
                if self.data_metab64:
                    util_xml.TextSubElement(e, "data_metab64_id", self.data_metab64.id)
                if self.data_ecc2:
                    util_xml.TextSubElement(e, "data_ecc2_id", self.data_ecc2.id)
                if self.data_water2:
                    util_xml.TextSubElement(e, "data_water2_id", self.data_water2.id)

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
            
                self.data_coil_combine_id   = source.findtext("data_coil_combine_id")
                self.data_ecc1_id           = source.findtext("data_ecc1_id")
                self.data_water1_id         = source.findtext("data_water1_id")
                self.data_metab64_id        = source.findtext("data_metab64_id")
                self.data_ecc2_id           = source.findtext("data_ecc2_id")
                self.data_water2_id         = source.findtext("data_water2_id")
            
            self.set = block_raw._Settings(self.set)

        elif hasattr(source, "keys"):
            # Quacks like a dict
            for key in source.keys():
                if not self.behave_as_preset:
                    if key == "data_coil_combine_id":
                        self.data_coil_combine_id = source["data_coil_combine_id"]
                    if key == "data_ecc1_id":
                        self.data_ecc1_id = source["data_ecc1_id"]
                    if key == "data_water1_id":
                        self.data_water1_id = source["data_water1_id"]
                    if key == "data_metab64_id":
                        self.data_metab64_id = source["data_metab64_id"]
                    if key == "data_ecc2_id":
                        self.data_ecc2_id = source["data_ecc2_id"]
                    if key == "data_water2_id":
                        self.data_water2_id = source["data_water2_id"]

                if key == "set":
                    setattr(self, key, source[key])


        


