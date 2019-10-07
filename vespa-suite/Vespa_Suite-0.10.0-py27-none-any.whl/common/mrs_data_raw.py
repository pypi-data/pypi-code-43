# Python modules
from __future__ import division

# 3rd party modules
import numpy as np
import xml.etree.cElementTree as ElementTree

# Our modules
import vespa.common.util.xml_ as util_xml
import vespa.common.util.misc as util_misc
import vespa.common.util.math_ as util_math
import vespa.common.constants as common_constants
from vespa.common.constants import Deflate

# _BLANK_DATA_SOURCE is the replacement string we use when a DataRaw has
# nothing in data_sources.
_BLANK_DATA_SOURCE = "[No information available]"


def normalize_data_dims(data):
    """Given a numpy ndarray, ensures that the data has the number of 
    dimensions that Vespa expects of DataRaw objects. (That's currently 4, as 
    defined by DataRaw.DEFAULT_DIMS.)

    The data array is returned.

    The data itself is not changed nor is the product of its shape elements. The
    shape is padded with 1s if necessary.  For instance, an array with shape
    [1024, 25] will be given the shape [1024, 25, 1, 1].

    See also DataRaw.normalize_dims() which is just a wrapper for this function.

    This function exists and is associated with DataRaw because DataRaw is 
    the first entry point into Vespa for 3rd party formats. Authors of code to
    translate those formats into DataRaw objects can use this function to 
    make sure their data is shaped the way Vespa likes it. 
    """
    padding = len(DataRaw.DEFAULT_DIMS) - len(data.shape)

    if padding > 0:
        data.shape = ([1] * padding) + list(data.shape)
    elif padding == 0:
        # Nothing to do; data already has correct number of dims
        pass
    else:
        # padding < 0 ==> data has too many dims
        raise ValueError, "Data with shape %s has too many dimensions" % str(data.shape)

    return data



class DataRaw(object):
    """ 
    A container for magnetic resonance spectroscopy data. 
    
    This is a building block object that can be used to create a  
    fundamental MRS data object. 
    
    This object contains the parameters that describe a raw MRS data set 
    (aka. k-space data). 
    
    In here we also package all the functionality needed to save and recall
    Preset values to/from an XML node.
    """
    # This is the version of this object's XML output format. 
    XML_VERSION = "1.0.0"
    
    # Some default attributes follow. Creating them as static properties of
    # the class ensures that every time someone accesses one of these 
    # constants, they get a fresh (unique) copy of the list.
    
    DEFAULT_DIMS = \
        util_misc.StaticProperty(lambda: [common_constants.DEFAULT_SPECTRAL_POINTS, 1, 1, 1])
    DEFAULT_IMAGE_POSITION = \
        util_misc.StaticProperty(lambda: [0.0, 0.0, 0.0])
    DEFAULT_IMAGE_DIMENSION = \
        util_misc.StaticProperty(lambda: [20.0, 20.0, 20.0])
    DEFAULT_IMAGE_ORIENTATION_ROW = \
        util_misc.StaticProperty(lambda: [1.0, 0.0, 0.0])
    DEFAULT_IMAGE_ORIENTATION_COLUMN = \
        util_misc.StaticProperty(lambda: [1.0, 0.0, 0.0])
    DEFAULT_ECHOPEAK = 0.0

    def __init__(self, attributes=None):
        # FIXME PS - docstring is incomplete/not up to date
        """
        General Parameters
        -----------------------------------------

        id          A permanent, unique identifying string for this 
                    object. Typically serves as a "source_id" for 
                    some other object. It is part of the provenance
                    for this processing functor chain
                   
        source_id   The unique identifier used to find the input data
                    for this object. It may refer to one whole object
                    that has only one result, OR it could refer to s
                    single results inside an object that has multiple
                    results.
        
        MRS Data Parameters
        -----------------------------------------
        
        header      String, header (metadata) from the input file
                   
        data        numpy array, The raw mr spectroscopy data.
        data_type   string [numpy data type], the type of the data. Read only.
                   
        data_sources  A list of strings explaining where the data came from. 
                      These are typically filenames but can be "scanner",
                      "database", etc. There should be 0, 1, or N entries in 
                      this list (where N == dims[1]) although this is not 
                      enforced. See the property .data_source and the method
                      get_data_source() for access to this list.

        frequency   float, MR scanner field strength in MHz
        
        dims        list [int], current data points in spatial/spectral 
                    dimensions. Read only.
                  
        sw          Data sweep width in Hz. Note that there's currently no way 
                    to change this when the application is running, but it can
                    differ from the acqsw. Quoting Brian, "Some saved data has
                    been 'snipped' from its original size to save space once
                    it was in the frequency domain. For instance, 4096 points
                    would be snipped to the 1024 that contained all the useful
                    peaks. In this circumstance, the sweep width would be set
                    to however many Hz were represented across that snip. E.g.
                    4096 pts and ACQSW=2000 snipped to 1024 pts would result
                    in SW=1000.
                   
        resppm      float, acquisition on-resonance value in PPM
        midppm      float, current data middle point (dim0/2) in PPM
        echopeak    float [0.0-1.0], acquisition spectral echo peak in % 
                    acqdim0 length
        nucleus     string, nucleus name, e.g. 1H, 31P, 13C etc.
        seqte       float, sequence echo time (TE) in [ms]
        hpp         float, current data Hertz per point (sw/dims[0]). Read only.
        
        """
        self.id               = util_misc.uuid()
        self.source_id        = ''
        self.behave_as_preset = False
        
        self.data_sources  = []
        self.sw            = common_constants.DEFAULT_SWEEP_WIDTH
        self.frequency     = common_constants.DEFAULT_PROTON_CENTER_FREQUENCY
        self.resppm        = common_constants.DEFAULT_PROTON_CENTER_PPM
        self.midppm        = common_constants.DEFAULT_PROTON_CENTER_PPM
        self.echopeak      = self.DEFAULT_ECHOPEAK
        self.nucleus       = common_constants.DEFAULT_ISOTOPE
        self.seqte         = 30.0
        self.flip_angle    = 90.0

        # voxel and/or slice location parameters
        self.image_position          = self.DEFAULT_IMAGE_POSITION
        self.image_dimension         = self.DEFAULT_IMAGE_DIMENSION
        self.image_orient_row        = self.DEFAULT_IMAGE_ORIENTATION_ROW
        self.image_orient_col        = self.DEFAULT_IMAGE_ORIENTATION_COLUMN
        self.slice_thickness         = 15.0
        self.slice_orientation_pitch = 'Tra'
        self.slice_orientation_roll  = ''

        self.measure_time = []

        self.headers = []
        self.data   = np.ndarray(self.DEFAULT_DIMS[::-1], dtype=np.complex64)

        # Explicit test for None necessary here. See:
        # http://scion.duhs.duke.edu/vespa/project/ticket/35
        if attributes is not None:
            self.inflate(attributes)
            

    ##### Standard Methods and Properties ##################################
    @property
    def data_source(self):
        """Returns the first data source in the list of data sources, or
        a placeholder string if no data source information is available. 

        See also get_data_source().
        """
        return (self.data_sources[0] if self.data_sources else _BLANK_DATA_SOURCE)
    
    @property
    def data_type(self):
        """Returns the data type as a numpy string, e.g. "complex64". 
        Read only."""
        return str(self.data.dtype)
    
    @property
    def dims(self):
        """Data dimensions in a list, e.g. [1024, 5, 1, 1]. It's read only."""
        # Note that self.data.shape is a tuple. Dims must be a list.
        return list(self.data.shape[::-1])

    @property
    def hpp(self):
        """Current hertz per point. It's read only."""
        return (self.sw / self.dims[0]) if self.dims[0] else 0.0
    
    @property
    def is_fid(self): 
        """Boolean; True if data is Free Induction Decay data.
        Inferred from echo peak. It's read only."""
        return not bool(self.echopeak)
    
    def __str__(self):
        return self.__unicode__().encode("utf-8")


    def __unicode__(self):
        lines = [ ]
        # The header to this text contains the class name. Generating it 
        # dynamically here ensures that this reports the correct object type
        # even for subclass instances of this class.
        header = "----------- {0} Object ------------"
        lines.append(header.format(self.__class__.__name__))
        lines.append("Data sources                  : %s" % self.data_sources)
        lines.append("Data dimensions               : "+str(self.dims))
        lines.append("Spectral sweep width (Hz)     : %f" % self.sw)
        lines.append("Spectrometer frequency (MHz)  : %f" % self.frequency)
        lines.append("Data type                     : %s" % self.data_type)
        lines.append("Acq resonance PPM             : %f" % self.resppm)
        lines.append("Data midpoint PPM             : %f" % self.midppm)
        lines.append("Acq echo peak                 : %f" % self.echopeak)
        lines.append("Nucleus                       : %s" % self.nucleus)
        lines.append("Sequence TE                   : %f" % self.seqte)
        lines.append("Flip angle                    : %f" % self.flip_angle)
        lines.append("Image position                : "+str(self.image_position))
        lines.append("Image dimension               : "+str(self.image_dimension))
        lines.append("Image orient row              : "+str(self.image_orient_row))
        lines.append("Image orient col              : "+str(self.image_orient_col))
        lines.append("Slice thickness               : %f" % self.slice_thickness)
        lines.append("Slice pitch                   : %s" % self.slice_orientation_pitch)
        lines.append("Slice roll                    : %s" % self.slice_orientation_roll)
        lines.append("Data length                   : %d" % self.data.size)
        if self.measure_time:
            items = [unicode(item) for item in self.measure_time]
            lines.append("Measurement Times             : %s" % " ".join(items))
        
        # __unicode__() must return a Unicode object. In practice the code
        # above always generates Unicode, but we ensure it here.
        return u'\n'.join(lines)


    def concatenate(self, new):
        """Given an DataRaw instance, concatenates that instance's data
        (and some metadata) onto this object. This object's second dimension 
        will increase by one. For instance, if self.dims was [4096, 1, 1, 1] 
        before concatenation, it will be [4096, 2, 1, 1] after.

        There are several conditions that must be met, otherwise this will
        raise a ValueError.
        
        1) This data must be single voxel or a stack of single voxels.
           (i.e. 3rd and 4th dimension == 1)
        2) The data to be concatenated must be single voxel or a stack of 
           single voxels. (i.e. 3rd and 4th dimension == 1)
        3) The spectral dimension (dims[0]) must match.
        4) The attributes data_type, sw, resppm, midppm, echopeak, and
           nucleus must be the same on both DataRaw instances. 
        """
        if max(self.dims[2:]) > 1:
            raise ValueError, "Current data is not single voxel "          \
                              "or a stack of single voxels"
    
        if max(new.dims[1:]) > 1:
            raise ValueError, "Data to be concatented is not single voxel" \
                              "or a stack of single voxels"
            
        if new.dims[0] != self.dims[0]:
            raise ValueError, "Spectral dimension mismatch"

        attribs = ("data_type", "sw", "resppm", "midppm", 
                   "echopeak", "nucleus")
        for attr in attribs:
            if getattr(self, attr) != getattr(new, attr):
                raise ValueError, """Attribute "%s" not equal""" % attr
                
        # Frequencies must be within +/-1 of one another.
        if not util_math.eq(self.frequency, new.frequency, 0, 1):
            raise ValueError, """Frequencies not equal""" % attr
                
        # All is well, we can concatenate.
        if new.data_sources:
            self.data_sources.append(new.data_sources[0])
        if new.headers:
            self.headers.append(new.headers[0])
        if new.measure_time:
            self.measure_time.append(new.measure_time[0])
        self.data = np.concatenate((self.data, new.data),axis=2)


    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            e = ElementTree.Element("data_raw", { "id" : self.id,
                                                  "version" : self.XML_VERSION})

            util_xml.TextSubElement(e, "behave_as_preset", self.behave_as_preset)

            if not self.behave_as_preset:
            
                for data_source in self.data_sources:
                    # Vespa <= 0.6.0 thought of data sources exclusively as 
                    # files, so we're stuck with "filename" in the XML
                    # rather than "data_source".
                    util_xml.TextSubElement(e, "filename", data_source)

                # Vespa <= 0.4.2 relied on reading the data type from XML. 
                # That's no longer the case, but we still write it so that 
                # newer versions of Vespa don't write files that look broken 
                # to versions <= 0.4.2.
                util_xml.TextSubElement(e, "data_type", self.data_type)

                # Vespa <= 0.5.0 relied on reading the dims from XML. 
                # That's no longer the case, but we still write it so that 
                # newer versions of Vespa don't write files that look broken 
                # to versions <= 0.5.0.
                for dim in self.dims:
                    util_xml.TextSubElement(e, "dim", dim)

                util_xml.TextSubElement(e, "sweep_width", self.sw)
                util_xml.TextSubElement(e, "frequency",   self.frequency)
                util_xml.TextSubElement(e, "resppm",      self.resppm)
                util_xml.TextSubElement(e, "midppm",      self.midppm)
                util_xml.TextSubElement(e, "echopeak",    self.echopeak)
                util_xml.TextSubElement(e, "nucleus",     self.nucleus)
                util_xml.TextSubElement(e, "seqte",       self.seqte)
                util_xml.TextSubElement(e, "flip_angle",  self.flip_angle)
                util_xml.TextSubElement(e, "slice_thickness",         
                                           self.slice_thickness)
                util_xml.TextSubElement(e, "slice_orientation_pitch", 
                                           self.slice_orientation_pitch)
                util_xml.TextSubElement(e, "slice_orientation_roll",  
                                           self.slice_orientation_roll)            

                for val in self.image_position:
                    util_xml.TextSubElement(e, "image_position", val)
                for val in self.image_dimension:
                    util_xml.TextSubElement(e, "image_dimension", val)
                for val in self.image_orient_row:
                    util_xml.TextSubElement(e, "image_orientation_row", val)
                for val in self.image_orient_col:
                    util_xml.TextSubElement(e, "image_orientation_col", val)

                e.append(util_xml.numpy_array_to_element(self.data, "data"))

                for item in self.measure_time:
                    util_xml.TextSubElement(e, "measure_time", item)

                for header in self.headers:
                    util_xml.TextSubElement(e, "header", header)

            return e
            
        elif flavor == Deflate.DICTIONARY:
            return self.__dict__.copy()


    def inflate(self, source):
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element  

            self.id = source.get("id")

            val = source.findtext("behave_as_preset")   # default is False
            if val is not None:
                self.behave_as_preset = util_xml.BOOLEANS[val]
            
            if not self.behave_as_preset:
                # Vespa <= 0.6.0 thought of data sources exclusively as 
                # files, so we're stuck with "filename" in the XML
                # rather than "data_source".
                self.data_sources = [filename.text for filename
                                                   in source.findall("filename")
                                                   if filename.text]

                self.sw        = float(source.findtext("sweep_width"))
                self.frequency = float(source.findtext("frequency"))
                self.resppm    = float(source.findtext("resppm"))
                self.midppm    = float(source.findtext("midppm"))
                self.echopeak  = float(source.findtext("echopeak"))
                self.nucleus   =       source.findtext("nucleus")
                self.seqte     = float(source.findtext("seqte"))
                self.flip_angle              = float(source.findtext("flip_angle"))
                self.slice_thickness         = float(source.findtext("slice_thickness"))
                self.slice_orientation_pitch = source.findtext("slice_orientation_pitch")
                self.slice_orientation_roll  = source.findtext("slice_orientation_roll")

                self.image_position = [float(val.text) for val
                                        in source.findall("image_position")]
                self.image_dimension = [float(val.text) for val
                                        in source.findall("image_dimension")]
                self.image_orient_row = [float(val.text) for val
                                        in source.findall("image_orientation_row")]
                self.image_orient_col = [float(val.text) for val
                                        in source.findall("image_orientation_col")]
                self.data = util_xml.element_to_numpy_array(source.find("data"))

                self.image_position = [float(val.text) for val
                                        in source.findall("image_position")]
                
                self.measure_time = [float(item.text) for item in source.findall("measure_time")]

                self.headers = [header.text for header in source.findall("header")]

        elif hasattr(source, "keys"):
            # Quacks like a dict
            for key in source.keys():
                if key == "header":
                    # This gets special treatment because it's passed
                    # as a singular item but is stored in a list.
                    self.headers.append(source["header"])
                elif key in ("data_source", "filename"):
                    # Like 'header', these attrs are single items in the dict
                    # but a list on the raw object. Also note that we accept
                    # two terms which both map back to "data_sources".
                    self.data_sources.append(source[key])
                elif key in ("data_type", "dims"):
                    # We ignore these since they're implied by the data. This
                    # has not always been the case; data type and dims (data
                    # shape) were once stored in separate attributes in addition
                    # to being properties of the .data attribute. It's not an
                    # error to pass data_type and dims to inflate(), but its
                    # best practice not to since they're ignored.
                    pass
                elif key == 'measure_time':
                    # This gets special treatment because it's passed
                    # as a singular item but is stored in a list.
                    self.measure_time = [float(val) for val in source[key]]
                else:
                    if hasattr(self, key):
                        setattr(self, key, source[key])

        if self.nucleus != "1H":
            self.midppm = common_constants.DEFAULT_XNUCLEI_CENTER_PPM
            self.resppm = common_constants.DEFAULT_XNUCLEI_CENTER_PPM

        # Now that inflating is complete, we ensure that the data is shaped
        # correctly. When inflating from VIFF this is never a problem. It's 
        # here as a CYA for 3rd party formats that might call inflate.
        self.normalize_dims()


    def get_data_source(self, index):
        """Given a 0-based index into the list of data_sources, attempts to 
        return the data source at that index. 

        This function is 'safe' in that if the index goes off the end of the
        list it won't fail but will instead return an alternate data source. 
        The sources that this function attempts to return in order of 
        preference are:
           1. data_sources[index]
           2. data_sources[0]
           3. A placeholder string (_BLANK_DATA_SOURCE)

        This function sacrifices guaranteed accuracy for guaranteed convenience.
        Callers who absolutely need to know which data source is at a given
        index will need to examine the list themselves.
        """
        nsources = len(self.data_sources)
        if nsources == 0:
            source = _BLANK_DATA_SOURCE
        else:
            if index >= nsources:
                # Ooops, we're off the end of the list. Just return the first 
                # one.
                index = 0
            source = self.data_sources[index]

        return source


    def normalize_dims(self):
        """Calls normalize_data_dims() (q.v.) in this module. 

        In addition, this method also ensures that the dims attribute reflects
        the data's shape.
        """
        self.data = normalize_data_dims(self.data)
