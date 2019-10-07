"""
Routines for reading a Varian file pair (procpar & fid) and returning an
DataRaw object populated with the files' data.
"""

# Python modules
from __future__ import division
import os.path

# 3rd party modules
import numpy
import vespa.analysis.src.fileio.nmrglue.varian as nmrglue_varian

# Our modules
import vespa.common.constants as constants
import vespa.common.util.misc as util_misc
import vespa.common.mrs_data_raw as mrs_data_raw
import vespa.analysis.src.fileio.raw_reader as raw_reader 

import vespa.analysis.src.fileio.util_exceptions as util_exceptions


# Documentation concerning the decisions in code below is scattered across a 
# few different manuals. We found relevant doc in both VNMR and VNMRJ manuals.
# (The latter is a successor to the former and/or a Java-based version.)
# We looked at docs with the following titles:
#   User Guide: Imaging
#   Vnmr  Command and Parameter Reference
#   VnmrJ Command and Parameter Reference
#   VnmrJ User Programming
#
# All of these docs are available at Agilent.com.
#
# Most of the work for reading Varian files is done by modules we swiped from
# the NMRGlue project (J. J. Helmus and C.P. Jaroniec, nmrglue, 
# http://code.google.com/p/nmrglue, The Ohio State University.)


class RawReaderVarian(raw_reader.RawReader):
    def __init__(self):
        raw_reader.RawReader.__init__(self)
        
        self.filetype_filter = "Spectra (procpar,fid)|procpar;fid"
        self.multiple = False
        

    def read_raw(self, path, ignore_data=False, *args, **kwargs):
        """
        Given the fully qualified path to a directory of Varian files, returns
        an DataRaw object populated with the parameters and data
        represented by the files therein. One can also pass the fully
        qualified path to a procpar or fid file. For instance, all of the
        following are valid and will result in the same output:
        read_raw("/home/philip/data/csi2d_03.fid")
        read_raw("/home/philip/data/csi2d_03.fid/procpar")
        read_raw("/home/philip/data/csi2d_03.fid/fid")
    
        When ignore_data is True, this function only reads the parameters file
        which can be much faster than reading both params & data.
        """
        if not os.path.isdir(path):
            # Caller passed a directory name + file name. Strip the file name.
            path, _ = os.path.split(path)
        #else: 
            # Caller passed a directory name so I don't need to do anything

        # Create the name of the two files I want to read
        parameters_filename = os.path.join(path, "procpar")
        data_filename = os.path.join(path, "fid")

        if not os.path.isfile(parameters_filename):
            raise util_exceptions.FileNotFoundError, \
                  "I can't find the parameters file '%s'" % parameters_filename

        if not ignore_data and not os.path.isfile(data_filename):
            raise util_exceptions.FileNotFoundError, \
                  "I can't find the data file '%s'" % data_filename

        # Read the params file and extract the stuff I need.
        procpar = nmrglue_varian.read_procpar(parameters_filename)

        d = _extract_parameters(procpar)

        # The entire procpar file gets stuffed into the "headers" 
        d["headers"]  = [open(parameters_filename, "rb").read()]
        d["data_source"] = path

        # Read data, too, if the caller wants me to do so.
        if not ignore_data:
            shape = nmrglue_varian.find_shape(procpar)

            _, data = nmrglue_varian.read_fid(data_filename, shape)

            # Ensure the data is the right shape
            data = mrs_data_raw.normalize_data_dims(data)
        
            d["data"] = data

        return mrs_data_raw.DataRaw(d)



####################    Internal functions start here     ###############

def _extract_parameters(procpar):
    """Given the procpar file as a dict, extracts a few specific parameters 
    and returns a flat dict containing those parameters and their value.

    The returned dict is appropriate for passing to DataRaw.inflate().
    """
    d = { }

    # A procpar dict contains many, many keys. We're only interested in 
    # a few.
    # Sweep width
    d["sw"] = float(procpar["sw"]["values"][0])
    # Scanner frequency (in MHz; e.g. sfrq=400.335 is a 9.4T).
    d["frequency"] = float(procpar["sfrq"]["values"][0])
    d["seqte"] = float(procpar["te"]["values"][0])
    if "flip1" in procpar.keys():
        d["flip_angle"] = float(procpar["flip1"]["values"][0])
    else:
        d["flip_angle"] = 0.0
        
    # The observed isotope is given as H1, P31, etc. We prefer it in
    # the reverse order so we fix it here.
    nucleus = util_misc.normalize_isotope_name(procpar["tn"]["values"][0])

    if nucleus is None:
        nucleus = ""

    if nucleus == "1H":
        d["resppm"] = constants.DEFAULT_PROTON_CENTER_PPM
        d["midppm"] = constants.DEFAULT_PROTON_CENTER_PPM
    else:
        d["resppm"] = constants.DEFAULT_XNUCLEI_CENTER_PPM
        d["midppm"] = constants.DEFAULT_XNUCLEI_CENTER_PPM

    d["nucleus"] = nucleus

    return d

