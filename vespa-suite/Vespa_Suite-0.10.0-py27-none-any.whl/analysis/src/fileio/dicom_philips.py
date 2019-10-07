# Python modules
from __future__ import division
import struct
import math
import os
import collections

# 3rd party modules
import dicom
import numpy

# Our modules
import vespa.common.util.fileio as util_fileio
import vespa.analysis.src.fileio.dicom_browser.dialog_browser as dicom_browser
import vespa.analysis.src.fileio.raw_reader as raw_reader
import vespa.analysis.src.fileio.util_philips as util_philips


import vespa.common.mrs_data_raw as mrs_data_raw
import vespa.common.constants as constants
import vespa.common.configobj as configobj

from vespa.analysis.src.fileio.util_exceptions import IncompleteHeaderParametersError


# Data type is always numpy.complex64 (per Siemens doc or...?)
NUMPY_DATA_TYPE = numpy.complex64


# Change to True to enable the assert() statements sprinkled through the code
ASSERTIONS_ENABLED = False

# These are DICOM standard tags
TAG_SOP_CLASS_UID = (0x0008, 0x0016)

# These are some Siemens-specific tags
TAG_CONTENT_TYPE                          = (0x0029, 0x1008)
TAG_SPECTROSCOPY_DATA_DICOM_SOP           = (0x5600, 0x0020)
TAG_SPECTROSCOPY_DATA_PHILIPS_PROPRIETARY = (0x2005, 0x1270)

# This module is based on the dicom_siemens.py module. I (Brian) have tried
# to maintain all the comments that are relevant from the original code, but
# removed some Siemens-specific yabbering for brevity
#
# ------------------------------------------------------------------------
#
# CSA header parsing is a port of C++ code in GDCM (Grassroots DICOM) project.

class RawReaderDicomPhilips(raw_reader.RawReader):
    """
    Reads a Philips DICOM file into an DataRaw object.

    It implements the interface defined by raw_reader.RawReader (q.v.).
    """
    def __init__(self):
        raw_reader.RawReader.__init__(self)


    def pickfile(self, default_path=""):
        """ 
        The default here is to allow multiple filenames. Each will be treated as
        a separate MRS file and 'loaded into the screen'.
        
        """
        dialog = dicom_browser.PhilipsSpectroscopyBrowserDialog(multi_select=self.multiple)
        dialog.ShowModal()
        self.filenames = dialog.filenames

        return bool(self.filenames)


    def read_raw(self, filename, ignore_data=False, *args, **kwargs):
        """
        Given the name of a Siemens DICOM file, returns an DataRaw object
        populated with the parameters and data.

        When ignore_data is True, this function ignores the data in the DICOM
        file which can help performance.
        
        """
        # Since a DICOM file is params + data together, it's not so simple to
        # ignore the data part. The best we can do is tell PyDicom to apply
        # lazy evaluation which might not save a lot of time or disk IO.
        defer_size = 4096 if ignore_data else None

        dataset = dicom.read_file(filename, defer_size)

        # dataset is a pydicom dataset which is a custom object that's
        # dictionary-ish but still very DICOM-y. We want a dictionary that's
        # friendly to DataRaw and it takes a couple of steps to get there.
        #
        # Philips still uses a proprietary DICOM hack to store MRS data, rather
        # than the more elegant (and official)  MR Spectroscopy Storage object 
        # that is somewhat available on Siemens. That is all that we accomodate 
        # within this module.

        # get parameters stored in proprietary tags - direct to something palatable to DataRaw
        d = _extract_parameters_from_dataset_proprietary(dataset)

        # Header is a string representation of the params we read in. 
        # Since we already have a dict, it's easy to generate the key=value pairs
        # for an INI file format. We need a section name, though, so I use the
        # filename for lack of a better idea.
        header = ["%s=%s" % (key, d[key]) for key in sorted(d.keys())]
        header = "\n".join(header)
        header = ("[%s]\n" % os.path.basename(filename)) + header

        d["header"]      = header
        d["data_source"] = filename

        shape = d["dims"][::-1]
        del d["dims"]

        if ignore_data:
            # create zero data
            data = numpy.zeros(shape, NUMPY_DATA_TYPE)
        else:
            data = _read_data_from_dataset_proprietary(dataset)
            data = numpy.fromiter(data, NUMPY_DATA_TYPE)

            data.shape = shape

        d["data"] = data

        return mrs_data_raw.DataRaw(d)


####################    Internal functions start here     ###############

def _read_data_from_dataset_proprietary(dataset):
    """
    Given a PyDicom dataset, returns the data in the Philips DICOM
    spectroscopy data tag (0x2005,0x1270) as a list of complex numbers.
    
    """
    data = []

    # TODO bjs - may not need all this error checking here?
    if not isinstance(dataset, dicom.dataset.Dataset):
        raise ValueError("Object passed in not a pydicom Dataset.") 
    
    if not util_philips.is_mrs_dicom(dataset):
        raise ValueError("Dataset does not have MRS data.")
    
    data = dataset[0x2005,0x1270].value         
    data = util_fileio.collapse_complexes(data, conjugate_flag=True)  # empirical, so far

    return data


def _extract_parameters_from_dataset_proprietary(dataset):
    """
    Given a PyDicom dataset, returns a fairly extensive subset of the
    parameters therein as a dictionary. 

    """
    d = { }

    # some calculations before making a dict

    institution_id = _get(dataset, (0x0008, 0x0080), "")
    
    if (0x0028,0x9001) in dataset:
        averages = dataset[0x0028,0x9001].value 
    elif (0x2005,0x140f) in dataset:
        if "DataPointRows" in dataset[0x2005,0x140f].value[0]:
            averages = dataset[0x2005,0x140f].value[0].DataPointRows
    elif (0x2001,0x1081) in dataset:
        averages = dataset[0x2001,0x1081].value     # maybe?  number of dynamic scans
    else:
        averages = 1

    if (0x2005,0x1315) in dataset:
        spectral_points = dataset[0x2005,0x1315].value 
    elif (0x2005,0x140f) in dataset:
        if "DataPointColumns" in dataset[0x2005,0x140f].value[0]:
            spectral_points = dataset[0x2005,0x140f].value[0].DataPointColumns
    elif (0x0028,0x9002) in dataset:
        spectral_points = dataset[0x0028,0x9002].value
    else:
        raise IncompleteHeaderParametersError, "spectral_points"

    if (0x2005,0x140f) in dataset:
        if "ChemicalShiftReference" in dataset[0x2005,0x140f].value[0]:
            ppm_ref = dataset[0x2005,0x140f].value[0].ChemicalShiftReference[0]
    elif (0x0018,0x9053) in dataset:
        ppm_ref = dataset[0x0018,0x9053].value
    else:
        ppm_ref = 0.0

    if (0x2005,0x140f) in dataset:
        if "SpectrallySelectedSuppression" in dataset[0x2005,0x140f].value[0]:
            water_suppression = dataset[0x2005,0x140f].value[0].SpectrallySelectedSuppression
        elif (0x0018,0x9025) in dataset[0x2005,0x140f].value[0]:
            water_suppression = dataset[0x2005,0x140f].value[0][0x0018,0x9025].value
        else:
            water_suppression = ''
        


    # here are the essential paramters for Analysis

    d["dims"]              = mrs_data_raw.DataRaw.DEFAULT_DIMS
    d["dims"][0]           = int(spectral_points)
    d["dims"][1]           = int(averages)
    d["dims"][2]           = 1
    d["dims"][3]           = 1
    d["frequency"]         = float(_get(dataset, (0x2001,0x1083), "")) 
    d["sw"]                = float(_get(dataset, (0x2005,0x1357), ""))
    d["nucleus"]           = "1H"
    d["seqte"]             = float(_get(dataset, (0x2001,0x1025), "")) * 0.001


    # added this parameter when Siemens started using DICOM MRS compliant
    # SOP object rather than a proprietarty hack. Some storage rules are
    # slightly different between the two, this flag allow us to test for them.
    d["is_dicom_sop"] = False

    # Patient Info
    d["patient_name"]      = _get(dataset, (0x0010, 0x0010), "")
    d["patient_id"]        = _get(dataset, (0x0010, 0x0020), "")
    d["patient_birthdate"] = _get(dataset, (0x0010, 0x0030))
    d["patient_sex"]       = _get(dataset, (0x0010, 0x0040), "")
    d["patient_age"]       = int(_get(dataset, (0x0010, 0x1010), "000Y")[:3])  # [PS] Siemens stores the age as nnnY where 'n' is a digit, e.g. 042Y
    d["patient_weight"]    = round(_get(dataset, (0x0010, 0x1030), 0))

    # Identification info
    d["institution_id"]    = institution_id
    d["bed_move_date"]     = _get(dataset, (0x0008, 0x0020), "")
    d["measure_date"]      = d["bed_move_date"]
    d["bed_move_time"]     = _get(dataset, (0x0008, 0x0030), "")
    d["measure_time"]      = _get(dataset, (0x0008, 0x0032), "")
    if d["measure_time"] == "":
        d["measure_time"]  = _get(dataset, (0x0008, 0x0033), "")
    d["data_type"]         = "complex64"     # default
    
    if "VolumeLocalizationTechnique" in dataset:
        d["sequence_type"]     = dataset.VolumeLocalizationTechnique   # tells PRESS (PRIME) or STEAM or sLASER

    if "RepetitionTime" in dataset:
        d["repetition_time"]   = float(dataset.RepetitionTime) * 0.001
    else:
        d["repetition_time"]   = float(_get(dataset, (0x2005,0x1030), "")[0]) * 0.001
        
    d["echopeak"]          = 0.0
    d["resppm"]            = constants.DEFAULT_PROTON_CENTER_PPM       # default is 4.7
    d["midppm"]            = d["resppm"]
    
    d["image_normal_sagittal"]   = 1.0
    d["image_normal_coronal"]    = 0.0
    d["image_normal_transverse"] = 0.0
    d["image_column_sagittal"]   = 0.0
    d["image_column_coronal"]    = 0.0
    d["image_column_transverse"] = 1.0

    if "ProtocolName" in dataset:
        d["protocol_name"] = dataset.ProtocolName
    else:
        d["protocol_name"]  = _get(dataset, (0x0018,0x1030), "")

    if "Manufacturer" in dataset:
        d["manufacturer"] = dataset.Manufacturer

    if "SeriesDescription" in dataset:
        d["series_description"] = dataset.SeriesDescription 

    if "ManufacturerModelName" in dataset:
        d["manufacturer_model_name"] = dataset.ManufacturerModelName 
        
    if "ReceiveCoilName" in dataset:
        d["receive_coil_name"] = dataset.ReceiveCoilName
    else:
        d["receive_coil_name"]  = _get(dataset, (0x0018,0x1250), "")
        
    if "SoftwareVersions" in dataset:
        d["software_versions"] = str(dataset.SoftwareVersions)
    else:
        d["software_versions"]  = str(_get(dataset, (0x0018,0x1020), ""))


    if "SliceThickness" in dataset:
        d["slice_thickness"] = dataset.SliceThickness
        
    if "FlipAngle" in dataset:
        d["flip_angle"] = dataset.FlipAngle

    if "PixelSpacing" in dataset:
        temp = dataset.PixelSpacing
        d["pixel_spacing"] = [float(item) for item in temp]
        
    d["water_suppression"] = water_suppression

    

    return d


def _my_assert(expression):
    if ASSERTIONS_ENABLED:
        assert(expression)





def _float(value):
    """Attempts to return value as a float. No different from Python's
    built-in float(), except that it accepts None and "" (for which it
    returns 0.0).
    """
    return float(value) if value else 0.0


def _extract_from_quotes(s):
    """Given a string, returns the portion between the first and last
    double quote (ASCII 34). If there aren't at least two quote characters,
    the original string is returned."""
    start = s.find('"')
    end = s.rfind('"')

    if (start != -1) and (end != -1):
        s = s[start + 1 : end]

    return s



def _get(dataset, tag, default=None):
    """Returns the value of a dataset tag, or the default if the tag isn't
    in the dataset.
    PyDicom datasets already have a .get() method, but it returns a
    dicom.DataElement object. In practice it's awkward to call dataset.get()
    and then figure out if the result is the default or a DataElement,
    and if it is the latter _get the .value attribute. This function allows
    me to avoid all that mess.
    It is also a workaround for this bug (which I submitted) which should be
    fixed in PyDicom > 0.9.3:
    http://code.google.com/p/pydicom/issues/detail?id=72
    Also for this bug (which I submitted) which should be
    fixed in PyDicom > 0.9.4-1:
    http://code.google.com/p/pydicom/issues/detail?id=88

    bjs - added the option that the tag may exist, but be blank. In this case
          we will return the default value. This is especially important if
          the data has been run through an anonymizer as many of these leave
          the tag but set it to a blank string.

    """
    if tag not in dataset:
        return default

    if dataset[tag].value == '':
        return default

    return dataset[tag].value


def _empty_string(value, default):
    if value == '':
        return default
    else:
        return value





