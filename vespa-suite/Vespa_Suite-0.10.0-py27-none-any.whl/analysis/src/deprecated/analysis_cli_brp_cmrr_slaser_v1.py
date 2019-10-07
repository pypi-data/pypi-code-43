# Python modules
from __future__ import division
import argparse
import os
import sys
import platform
import imp
import xml.etree.cElementTree as ElementTree
import collections
import multiprocessing


# 3rd party modules
import numpy as np

# Our modules
import mrs_dataset
import block_prep_fidsum
import block_raw_cmrr_slaser
import util_import

import vespa.common.configobj as configobj
import vespa.common.util.misc as util_misc
import vespa.common.util.export as util_export
import vespa.common.constants as common_constants
import vespa.common.mrs_data_raw_cmrr_slaser as mrs_data_raw_cmrr_slaser

import vespa.common.twix_parser_multi_raid as twix_multi_raid
import vespa.common.constants as constants
import vespa.common.util.misc as util_misc
import vespa.analysis.src.fileio.raw_reader as raw_reader 

from vespa.common.constants import DEGREES_TO_RADIANS, RADIANS_TO_DEGREES, DEFAULT_PROTON_CENTER_PPM, DEFAULT_XNUCLEI_CENTER_PPM

# Change to True to enable the assert() statements sprinkled through the code
ASSERTIONS_ENABLED = False

# data is complex64 per Siemens documentation for Twix
NUMPY_DATA_TYPE = np.complex64
# BYTES_PER_ELEMENT expresses how many bytes each element occupies. You
# shouldn't need to change this definition.
BYTES_PER_ELEMENT = np.zeros(1, dtype=NUMPY_DATA_TYPE).nbytes

# RAWDATA_SCALE is based on ICE_RAWDATA_SCALE in SpecRoFtFunctor.cpp
RAWDATA_SCALE = 131072.0 * 256.0


DESC =  \
"""Command line interface to process MRS data in Vespa-Analysis. 
 Data filename, preset file name, data type string and CSV output 
 file name values are all required for this command to function 
 properly.
  
 Note. You may have to enclose data/preset/output strings in double 
 quotation marks for them to process properly if they have  
 spaces or other special characters embedded in them.
"""

class CliError(Exception):
    """Basic exception for errors when applying preset object"""
    def __init__(self, msg=None):
        if msg is None:
            # set default error message
            msg = 'A general cli error occured.'
        e = sys.exc_info()
        msg =  'CliErrorMessage : '+msg
        msg += '\n'
        msg += 'BaseErrorMessage: '+e[1].message
        super(CliError, self).__init__(msg)


def clean_header(header):
    """ converts all values in ICE dict into a long string"""
    return "need to write"


def analysis_cli_gulin(datasets, preset_metab,
                                 preset_coil,
                                 preset_water,
                                 preset_ecc,
                                 out_base,
                                 out_prefix,
                                 verbose=False, debug=False, in_gui=False):
    
    
    # Sort datasets into variables ----------------------------------
    
    data_coil, data_ecc, data_water, data_metab, data_ecc2, data_water2 = datasets

    msg = ""
    
    # Load and Process - Coil Combine Dataset -----------------------

    if verbose: print "Apply Preset and Run Chain - Coil Combine"    
    try:
        msg = """applying preset - coil combine""" 
        data_coil.apply_preset(preset_coil, voxel=(0,0,0))  # update dataset object with preset blocks and chains

        msg = """running chain - coil combine""" 
        _process_all_blocks(data_coil)
    
    except:
        if not in_gui:
            print >> sys.stderr, msg+'\n'+str(sys.exc_info()[1])
            sys.exit(-1)
        else:
            raise CliError(msg)

    # Load Preset - Ecc, Water and Metab Datasets -------------------

    if verbose: print "Apply Preset - Ecc, Water and Metab Datasets"    
    try:
        # Apply presets to ecc, water and metab datasets
        
        msg = """applying preset - ecc""" 
        data_ecc.apply_preset(preset_ecc, voxel=(0,0,0))      # chain  

        msg = """applying preset - water""" 
        data_water.apply_preset(preset_water, voxel=(0,0,0))  

        msg = """applying preset - metab""" 
        data_metab.apply_preset(preset_metab, voxel=(0,0,0))  

        # Attach coil combine to ecc, water and metab datasets

        msg = """attaching coil combine to - ecc, water and metab"""
        for dset in [data_ecc, data_water, data_metab]:
            dset.blocks['prep'].attach_dataset_coil_combine(data_coil)

#             dset.blocks['prep'].set.coil_combine_method              = 'External Dataset'
#             dset.blocks['prep'].set.coil_combine_external_filename   = 'CmrrSlaserCoilCombineDataset'
#             dset.blocks['prep'].set.coil_combine_external_dataset    = data_coil
#             dset.blocks['prep'].set.coil_combine_external_dataset_id = data_coil.id

        # Run chain - Ecc, get combined FID for next steps
        
        msg = """running chain - ecc"""
        _process_all_blocks(data_ecc)
        
        # Attach ecc to water and metab datasets

        msg = """attaching ecc to - water and metab"""
        for dset in [data_water, data_metab]:
            dset.blocks['spectral'].attach_dataset_ecc(data_ecc)

#         block    = data_ecc.blocks["prep"]
#         raw_data = block.data.copy() / block.data[0,0,0,0]   # normalize to first pt in fid
#             dset.blocks['spectral'].set.ecc_dataset    = data_ecc
#             dset.blocks['spectral'].set.ecc_dataset_id = data_ecc.id
#             dset.blocks['spectral'].set.ecc_raw        = raw_data
#             dset.blocks['spectral'].set.ecc_filename   = 'CmrrSlaserEccDataset'   # block.data_source

        # Run chain - Water
        
        msg = """running chain - water"""
        _process_all_blocks(data_water)

        # Attach water to metab dataset

        msg = """attaching water to - metab"""
        for dset in [data_metab,]:
            dset.blocks['quant'].attach_dataset_water_quant(data_water)
        
#         data_metab.blocks['quant'].set.watref_dataset    = data_water
#         data_metab.blocks['quant'].set.watref_dataset_id = data_water.id

        # Run chain - Metab
        
        msg = """running chain - metab"""
        _process_all_blocks(data_metab)


    except:
        if not in_gui:
            print >> sys.stderr, 'Error: '+msg+'\n'+sys.exc_info()[1].message
            sys.exit(-1)
        else:
            raise CliError(msg)
    
    
    # Create unique name ID for this dataset ------------------------
    
    outxml = out_base+out_prefix+'.xml'
    
    data_metab.dataset_filename = outxml

    # Save results to CSV file --------------------------------------

#     if verbose: print """Saving results to CSV file "%s". """ % csvfile
#     
#     fit = data_metab.blocks["fit"]
#     data_source = data_metab.blocks["raw"].get_data_source(voxel[0])
#     
#     val, hdr = fit.results_as_csv(voxel[0], fit.chain.fitted_lw,
#                                             fit.chain.minmaxlw[0],
#                                             fit.chain.minmaxlw[1], 
#                                             data_source, outxml)
#     nhdr = len(hdr)
#     val = ",".join(val)
#     hdr = ",".join(hdr)
#     val += "\n"
#     hdr += "\n"
#      
#     hdr_flag = True
#     if os.path.isfile(csvfile):
#         with open(csvfile, 'r+') as f:
#             data = f.readlines()
#             if len(data)>1:
#                 last = data[-1]
#                 nlast = len(last.split(','))
#                 if nlast == nhdr:
#                     hdr_flag = False
#                 
#     with open(csvfile, 'a') as f:
#         if hdr_flag:
#             f.write(hdr)
#         f.write(val)

    # Save results to XML -----------------------------------------------------
    
    if verbose: print """Saving dataset to XML file "%s". """ % outxml
    
    try:
        util_export.export(outxml, [data_metab,], None, None, False)
    except Exception as e:
        msg = """I can't write the file "%s".""" % outxml
        print >> sys.stderr, msg
        print >> sys.stderr, repr(e)
        sys.exit(-1)
        
    return None, None
            
            
            
               
def _process_all_blocks(dataset):
    """ for all voxels, run chain in all blocks to update """
    
    chain_outputs = {}
    
    voxel = dataset.all_voxels
    for key in dataset.blocks.keys():
        if key == 'spectral':
            key = 'spectral'
            block = dataset.blocks[key]
            tmp = block.chain.run(voxel, entry='all')
            chain_outputs[key] = tmp
            if 'fit' in dataset.blocks.keys():
                key = 'fit'
                block = dataset.blocks[key]
                block.chain.run(voxel, entry='initial_only')
                key = 'spectral'
                block = dataset.blocks[key]
                block.set_do_fit(True, voxel[0])
                tmp = block.chain.run(voxel, entry='all')
                chain_outputs[key] = tmp
        else:
            block = dataset.blocks[key]
            tmp = block.chain.run(voxel, entry='all')
            chain_outputs[key] = tmp

    return chain_outputs








#------------------------------------------------------------------------------

class RawReaderSiemensTwixSlaserCmrrVe(raw_reader.RawReader):
    # This inherits from raw_reader.RawReader (q.v.). The only methods you
    # need to implement are __init__() and read_raw(). You *may* want to 
    # override or supplement some of raw_reader.RawReader's other methods.

    def __init__(self):
        raw_reader.RawReader.__init__(self)
        
        # The twix files all have an extension of *.dat, thus the filter below.
        self.filetype_filter = "Twix File (*.dat)|*.dat;*.DAT;"
        self.multiple = False
        
        
    def read_raw(self, filename, ignore_data=False, open_dataset=None):
        """
        Given the name of a twix file, returns a DataRawFidsum object
        populated with the parameters and data represented by the file. 
        The 'Fidsum' flavor of raw data object has individual FIDs returned in
        it rather than one summed FID.

        The ignore_data option is not implemented for this reader. 
        
        The open_dataset attribute is not used in this reader. 
        
        """
        twix = twix_multi_raid.TwixMultiRaid()
        
        twix.populate_from_file(filename)
        
        raws = []
        
        meas = twix.measurements[-1]
        
        scans, evps = meas.scans, meas.evps

        # Fill a dictionary with the minimum necessary parameters needed from
        # the twix file in order to create the DataRawFidsum objects.
        d = _extract_parameters(evps)

        if d["remove_os"]: d["sw"]   = d["sw"] / 2.0

        # Note. not filling in d["filename"] since it just gets collated with 
        #       d["data_source"] anyway, and we want only 1 string in this attrib.

        #----------------------------------------------------------------------
        # dataset1 - scan 0, water unsuppressed for coil combine
        
#        d["filename"] = filename+'.combine'

        # Parse scan data into array
        tmp = [scans[0],]           # workaround, it is a single scan but expects list of scans
        dat = _read_data(tmp, d)

        d["data"] = dat
        d["data_source"] = filename+'.combine'
        raw = mrs_data_raw_cmrr_slaser.DataRawCmrrSlaser(d)

        raws.append(raw)

        #----------------------------------------------------------------------
        # dataset2 - scan 1-2, water unsuppressed for ECC
        
#        d["filename"] = filename+'.ecc1'

        # Parse scan data into array
        tmp = scans[1:3]
        dat = _read_data(tmp, d)

        d["data"] = dat
        d["data_source"] = filename+'.ecc1'
        raw = mrs_data_raw_cmrr_slaser.DataRawCmrrSlaser(d)

        raws.append(raw)

        #----------------------------------------------------------------------
        # dataset3 - scans 3-4, water unsuppressed for water scale
        
#        d["filename"] = filename+'.water1'

        # Parse scan data into array
        tmp = scans[3:5]
        dat = _read_data(tmp, d)

        d["data"] = dat
        d["data_source"] = filename+'.water1'
        raw = mrs_data_raw_cmrr_slaser.DataRawCmrrSlaser(d)

        raws.append(raw)

        #----------------------------------------------------------------------
        # dataset4 - scans 5-68 (64 total), metabolite data with WS

#        d["filename"] = filename+'.metab64'

        # Parse scan data into array
        tmp = scans[5:69]
        dat = _read_data(tmp, d)

        d["data"] = dat
        d["data_source"] = filename+'.metab64'
        raw = mrs_data_raw_cmrr_slaser.DataRawCmrrSlaser(d)

        raws.append(raw)

        #----------------------------------------------------------------------
        # dataset5 - scans 69-70 (2 total), water unsuppressed for ecc

#        d["filename"] = filename+'.ecc2'

        # Parse scan data into array
        
        tmp = scans[69:71]
        dat = _read_data(tmp, d)

        d["data"] = dat
        d["data_source"] = filename+'.ecc2'
        raw = mrs_data_raw_cmrr_slaser.DataRawCmrrSlaser(d)

        raws.append(raw)

        #----------------------------------------------------------------------
        # dataset6 - scans 71-72 (2 total), water unsuppressed for water scale

#        d["filename"] = filename+'.water2'

        # Parse scan data into array
        
        tmp = scans[71:73]
        dat = _read_data(tmp, d)

        d["data"] = dat
        d["data_source"] = filename+'.water2'
        raw = mrs_data_raw_cmrr_slaser.DataRawCmrrSlaser(d)

        raws.append(raw)
        # TODO - bjs
        # - check scaling to get these numbers up
        # - check if ECC associate works in concert with other associations 

        return raws




####################    Internal functions start here     ###############

def _extract_parameters(evps):
    """
    Given the contents of an SPAR file as a string, extracts a few specific
    parameters and returns a flat dict containing those parameters and their 
    value. 
    The returned dict is appropriate for passing to DataRaw.inflate().
    
    """
    d = { }

    header, clean_header = _parse_protocol_data(evps[3][1])

    # A copy of this goes into the dict.
    d["header"] = clean_header

    remove_oversample_flag = header.get("sSpecPara.ucRemoveOversampling", "0x0")
    remove_oversample_flag = (remove_oversample_flag.strip() == "0x1")

    d["sw"]             = 1.0 / (float(header.get("sRXSPEC.alDwellTime[0]", 1.0)) * 1e-9)
    d["remove_os"]      = remove_oversample_flag
    d["readout_os"]     = float(_get_siemens_xprotocol(evps[0][1], "ReadoutOS", 1.0))
    d["sequence_type"]  = header.get("tSequenceFileName", "wbnaa")
    d["frequency"]      = float(header["sTXSPEC.asNucleusInfo[0].lFrequency"])/1000000.0
    d["dims"]           = mrs_data_raw_cmrr_slaser.DataRawCmrrSlaser.DEFAULT_DIMS
    d["dims"][0]        = int(header["sSpecPara.lVectorSize"]) 
    d["dims"][1]        = 1 # concat will take care of header["lAverages"]
    d["dims"][2]        = 1
    d["dims"][3]        = 1 
    d["seqte"]          = float(header["alTE[0]"])*1e-6
    
    nuc = header["sTXSPEC.asNucleusInfo[0].tNucleus"].replace('"',' ').strip()
    if nuc == '1H':
        d["midppm"] = DEFAULT_PROTON_CENTER_PPM
    else:
        d["midppm"] = DEFAULT_XNUCLEI_CENTER_PPM

    d["nucleus"] = nuc

    return d  
    
    
    
def _read_data(scans, d):
    """
    This Import method was originally developed to read/process from Siemens
    IceSpectroEdit, so I leave in the documentation below describing where the
    processing code came from.
    
    Given a list of scans and the extracted parameter dictionary we process
    the data in as similar a way to Siemens ICE program IceSpectroEdit as
    we can. My way of removing oversampling seems to not match 100% but the
    other steps are in the order and perform very similarly to the ICE program.

    When we are done parsing the ON and OFF state FIDs into arrays, we create
    SUM and DIF arrays to also send back.
    
    """
    dims    = d["dims"]
    dim0    = dims[0]
    acqdim0 = dims[0] * int(d["readout_os"])
    remove_os = d["remove_os"]
        
    ncoils2  = scans[0].scan_header.used_channels
    coil_ids = sorted(set([chan[0].channel_id for scan in scans for chan in scan.channels ]))
    nscans   = len(scans)
    ncoils   = len(coil_ids)

    data = np.ndarray([ncoils,nscans,dim0],dtype=complex)

    # determine if there are any extra points at the beginning or end of FID
    start_point = scans[0].scan_header.free_parameters[0]
    end_point   = start_point + acqdim0

    # lead to typical integral values of 1 or larger which are nicely displayed
    scale = RAWDATA_SCALE / float(nscans) 

    # Parse each group of FIDs for N channels for each average as separate
    # from all other scans. Perform the following steps:
    # - scale, all channels
    # - if needed, we remove oversampling, all channels
    # - convert to complex conjugate for proper plotting
    dat = []

    for iscan, scan in enumerate(scans):
        
        # for each average, remove pre-/post- points and apply phase to  
        # correct for coil geometry
        chans = []
                
        for ichan, item in enumerate(scan.channels):
            chan = item[1]
            chan = np.array(chan[start_point:end_point])*scale

            if remove_os:
                #
                # Note that this is a simple OS removal, not the full Siemens
                # algorithm. I have not had time to implement and test that.
                #
                # There are five steps to remove oversampling:
                # 1. forward transform data at acqdim0 resolution
                # 2. shift data by dim0/2 so we have a FID centered at dim0/2 before snip
                # 3. snip out first dim0 points and roll back by -dim0/2
                # 4. inverse transform data at dim0 resolution
                # 5. (omitted) multiply by 0.5 to maintain same scale as original data
                #    (based on the results in the actual IceSpecEdit program,
                #     but still these results are a few percent off of Siemens 
                #     results, ah well) 
                chan = np.fft.fft(chan)
                chan = np.roll(chan, int(dim0/2))
                chan = np.fft.ifft(np.roll(chan[:dim0], int(-dim0/2))) 

            # apply complex conjugate to swap x-axis for proper display of data
            chan = np.conjugate(chan)

            data[ichan,iscan,:] = chan 

    return data

    
    
def _parse_protocol_data(protocol_data):
    """
    Returns a dictionary containing the name/value pairs inside the
    "ASCCONV" section of the MrProtocol or MrPhoenixProtocol elements
    of a Siemens CSA Header tag.
    """
    # Protocol_data is a large string (e.g. 32k) that lists a lot of
    # variables in a JSONish format with which I'm not familiar. Following
    # that there's another chunk of data delimited by the strings you see
    # below.
    # That chunk is a list of name=value pairs, INI file style. We
    # ignore everything outside of the ASCCONV delimiters. Everything inside
    # we parse and return as a dictionary. 
    #
    # As of the Siemens VD scanner software version the starting string is
    # no longer ### ASCCONV BEGIN ### rather it seems to have some other
    # info about what was converted inserted after the BEGIN and before 
    # the ### delimiter. To get around this for now, we search just for the  clean_header[-1] len(protocol_data)
    # beginning of the string ### ASCONV BEGIN, and then throw away the
    # first line after we split the string into lines.
    #
    start = protocol_data.find("### ASCCONV BEGIN")
    end = protocol_data.find("### ASCCONV END ###")

    _my_assert(start != -1)
    _my_assert(end != -1)

    clean_start = start
    clean_end   = end + len("### ASCCONV END ###")
    clean_header = protocol_data[clean_start:clean_end]

    start += len("### ASCCONV BEGIN ###")
    protocol_data = protocol_data[start:end]

    lines = protocol_data.split('\n')
    lines = lines[1:]

    # The two lines of code below turn the 'lines' list into a list of
    # (name, value) tuples in which name & value have been stripped and
    # all blank lines have been discarded.
    f = lambda pair: (pair[0].strip(), pair[1].strip())
    lines = [f(line.split('=')) for line in lines if line]

    return dict(lines), clean_header


def _my_assert(expression):
    if ASSERTIONS_ENABLED:
        assert(expression)
        
 
def _get_siemens_xprotocol(head_only, key, default):
    
    head = util_misc.normalize_newlines(head_only)   
    head = head.split("\n")
    
    # find substring 'key' in list even if item in list is not iterable
    items = [el for el in head if isinstance(el, collections.Iterable) and (key in el)]
    
    for item in items:
        start = item.find("{")
        end = item.find("}")
        if start != -1 and end != -1:
            temp = item[start+1:end]
            # remove duplicate white space
            temp = " ".join(temp.split())
            temp = temp.split()
            
            if len(temp) == 1:
                return temp[0]
            elif len(temp) == 3:
                return temp[2]
            else:
                return temp
    
    return default



def _remove_oversampling(scan, d):   
    """ not currently in use as incomplete """
    
    vector_size = d["vector_size"]
    remove_os   = d["remove_os"]
    left_points = scan.pre
    right_points = scan.post
    reduced_points = scan.samples_in_scan - scan.pre - scan.post
    half_vector_size = int(vector_size / 2)
    
    if (reduced_points % vector_size) != 0:
        raise ValueError('remove_oversampling: final data size not multiple of vector size.')


    if not remove_os:
        # keep oversampled points but remove extra points
        start_point = scan.pre
        scan.data = scan.data[start_point:start_point+reduced_points]
    else:
        # remove oversampled data
        shift_points = scan.post if scan.post < scan.pre else scan.pre
        
        if shift_points == 0:
            # no extra pts available, final data will show truncation artifact
            start_point = scan.pre
            data = np.array(scan.data[start_point:start_point+reduced_points])
            data = np.fft.fft(data, n=vector_size)
            data = np.fft.ifft(data) * 0.5
            scan.data = data.tolist()
            
        else:
            # Extra pts available to use for removing truncation artifact.
            # Process data twice, centering signal to the left and right of kSpaceCentreColumn (TE)
            # Retrieve half of final signal from each set.
            pass


#------------------------------------------------------------------------------

def process_ice(scans, sw, freq, dim0, seqte, ncoils, nscans, npts, preset_string):
    """
    Assume that data is a list of FID data arrays in (scan, chan, npts) order.
    I need to process each FID to remove oversampling and then store into 
    a numpy array.
    
    
    """
    d = []
    
    filename = "Siemens_VB19_ICE_Transfer_semi-LASER"
    
    d["filename"]       = filename
    d["data_source"]    = filename
    d["sw"]             = 1.0 / float(sw * 1e-9)
    d["readout_os"]     = 2
    d["remove_os"]      = True
    d["sequence_type"]  = 'slaser'
    d["frequency"]      = float(freq)/1000000.0
    d["dims"]           = mrs_data_raw_cmrr_slaser.DataRawCmrrSlaser.DEFAULT_DIMS
    d["dims"][0]        = int(dim0) * int(d["readout_os"])
    d["dims"][1]        = 1 # this updates as raw.concatenate is applied
    d["dims"][2]        = 1
    d["dims"][3]        = 1 
    d["seqte"]          = float(seqte)*1e-6
    d["nucleus"]        = '1H'
    d["preset_string"]  = preset_string

    # load DATA into DATASETS ---------------------------------------
    
    data = np.ndarray([ncoils,nscans,dim0],dtype=complex)

    # determine if there are any extra points at the beginning or end of FID
    start_point = 0
    end_point   = start_point + (dim0 * 2)

    # lead to typical integral values of 1 or larger which are nicely displayed
    scale = RAWDATA_SCALE / float(nscans) 
    
    for iscan in range(nscans):
        
        # for each average, remove pre-/post- points and apply phase to  
        # correct for coil geometry
        chans = []
                
        for ichan in range(nchan):
            
            indx = ichan + iscan * nchan
            
            chan = scans[indx]
            chan = np.array(chan[start_point:end_point])*scale

            if remove_os:
                chan = np.fft.fft(chan)
                chan = np.roll(chan, int(dim0/2))
                chan = np.fft.ifft(np.roll(chan[:dim0], int(-dim0/2))) 

            # apply complex conjugate to swap x-axis for proper display of data
            chan = np.conjugate(chan)

            data[ichan,iscan,:] = chan 

        if d["remove_os"]: d["sw"]   = d["sw"] / 2.0

        datasets = []

        #----------------------------------------------------------------------
        # dataset1 - scans 1-4, water unsuppressed
        
        d["filename"]    = filename+'.water1'
        d["data"]        = data[:,1:5,:]
        raw = mrs_data_raw_cmrr_slaser.DataRawCmrrSlaser(d)

        datasets.append(raw)

        #----------------------------------------------------------------------
        # dataset2 - scans 5-68 (64 total), metabolite data with WS

        d["filename"]    = filename+'.metab64'
        d["data"]        = data[:,5:69,:]
        raw = mrs_data_raw_cmrr_slaser.DataRawCmrrSlaser(d)

        datasets.append(raw)

        #----------------------------------------------------------------------
        # dataset3 - scans 69-72 (4 total), water unsuppressed

        d["filename"]    = filename+'.water2'
        d["data"]        = data[:,69:73,:]
        raw = mrs_data_raw_cmrr_slaser.DataRawCmrrSlaser(d)

        datasets.append(raw)
        

    # Load PRESET data ----------------------------------------------
    
    if verbose: print "Load Preset into the Dataset object"    
    try:
        msg = ""
        
        preset_string  = header["preset_string"]
        preset_element = ElementTree.fromstring(preset_string)
        
        try:
            importer = util_import.DatasetImporter(preset_string)
        except IOError:
            msg = """I can't read the preset string "%s".""" % preset_string
        except SyntaxError:
            msg = """The preset string "%s" isn't valid Vespa Interchange File Format.""" % preset_string

        if msg:
            pass
            # TODO need to exit gracefully from this
        else:
            # Time to rock and roll!
            presets = importer.go()
            preset  = presets[0]
    except:
        msg = """Unknown exception reading Preset string "%s".""" % preset_string 
        # TODO need to exit gracefully from this


    img, outxml = analysis_cli_gulin(datasets, 
                                     preset, 
                                     verbose=args.verbose, 
                                     debug=args.debug)

    
    


def process_twix2dataset(datafile, verbose=False, debug=False):
    
    # Load DATASET object ----------------------------------------------
    
    if verbose: print """process_twix2dataset - Datafile = "%s"."""  % datafile  
    if debug: return
      
    try:
        data_parser = RawReaderSiemensTwixSlaserCmrrVe()
        raws = data_parser.read_raw(datafile)
    except:
        msg = """process_twix2dataset - Unknown exception parsing/reading Dataset file "%s".""" % datafile 
        print >> sys.stderr, msg
        sys.exit(-1)

    # Convert these raw objects into fully-fledged dataset objects.

    zero_fill_multiplier = 0

    # See if any data types need special classes. We usually only
    # look for raw fidsum classes which trigger a prep fidsum block.

    block_class_specs = [ ]
    for raw in raws:
        d = { }
        
        if isinstance(raw, mrs_data_raw_cmrr_slaser.DataRawCmrrSlaser):
            d["raw"]  = block_raw_cmrr_slaser.BlockRawCmrrSlaser
            d["prep"] = block_prep_fidsum.BlockPrepFidsum
        
        block_class_specs.append(d)

    f = lambda raw, block_classes: mrs_dataset.dataset_from_raw(raw,
                                                      block_classes,
                                               zero_fill_multiplier)
    datasets = map(f, raws, block_class_specs)

    for i,dataset in enumerate(datasets):
        # Here the cmrr slaser data reader should return 6 datasets, coil_combine 
        # (1 FID), ecc1 (2 FIDs), water1 (2 FIDs), metab64 (64 FIDs), ecc2 (2 FIDs) 
        # and water2 (2 FIDs). This will save provenance for all states. Note that 
        # when we go to save the dataset the copy of self that is in the associated 
        # raw datasets will be filtered out.
        dataset.blocks['raw'].set_associated_datasets([datasets[0], datasets[1], datasets[2], datasets[3], datasets[4], datasets[5]])


    return datasets


def load_preset(presetfile, verbose=False, debug=False):

    # Load PRESET object ----------------------------------------------
    
    if verbose: print """load_preset - Presetfile = "%s"."""  % presetfile 
    if debug: return 
     
    try:
        msg = ""
        try:
            importer = util_import.DatasetImporter(presetfile)
        except IOError:
            msg = """load_preset - I can't read the preset file "%s".""" % presetfile
        except SyntaxError:
            msg = """load_preset - The preset file "%s" isn't valid Vespa Interchange File Format.""" % presetfile

        if msg:
            print >> sys.stderr, msg
            sys.exit(-1)
        else:
            # Time to rock and roll!
            presets = importer.go()
            preset  = presets[0]
    except:
        msg = """load_preset - Unknown exception reading Preset file "%s".""" % presetfile 
        print >> sys.stderr, msg
        sys.exit(-1)

    
    return preset




def analysis_kernel(param):
    
    datafile, fbase, out_base0, out_base1, fpreset_coil, fpreset_ecc, fpreset_water, fpreset_metab = param
    
    # ---------------------------------
    # Copied section - begin

    debug   = False
    verbose = True
    
    # Copied section - end
    # ---------------------------------
        

    preset_metab = [load_preset(item, verbose=True, debug=debug) for item in fpreset_metab] 
    preset_coil  =  load_preset(fpreset_coil, verbose=True, debug=debug)
    preset_water =  load_preset(fpreset_water,   verbose=True, debug=debug)
    preset_ecc   =  load_preset(fpreset_ecc,     verbose=True, debug=debug)

    if verbose: 
        print "Unique Output Base   = "+out_base1

    # Use subdir names to create unique prefix for output files
    parts = os.path.normpath(datafile).split(os.sep)
    out_prefix = parts[-3]+'_'+parts[-2]    # Ex. 'S4_V1'

    datasets = process_twix2dataset( datafile, verbose=True, debug=debug )

    if verbose: 
        print "Unique Output Prefix = "+out_prefix

    if not debug:
        img0, outxml0 = analysis_cli_gulin( datasets, 
                                            preset_metab[0],
                                            preset_coil,
                                            preset_water,
                                            preset_ecc,
                                            out_base0,
                                            'mixed_'+out_prefix,
                                            verbose=True)

        bob = 10
        bob += 1

    if verbose: 
        print "Finished - " + str(os.path.basename(datafile))
    
#     for datafile in datafiles:
#         
#         # Use subdir names to create unique prefix for output files
#         parts = os.path.normpath(datafile).split(os.sep)
#         out_prefix = parts[-3]+'_'+parts[-2]    # Ex. 'S4_V1'
#     
#         datasets = process_twix2dataset( datafile, verbose=True, debug=debug )
#     
#         if verbose: 
#             print "Unique Output Prefix = "+out_prefix
#     
#         if not debug:
#             img0, outxml0 = analysis_cli_gulin( datasets, 
#                                                 preset_metab[0],
#                                                 preset_coil,
#                                                 preset_water,
#                                                 preset_ecc,
#                                                 out_base0,
#                                                 'mixed_'+out_prefix,
#                                                 verbose=True)
# 
#             bob = 10
#             bob += 1
#  
# #         datasets = process_twix2dataset( datafile, verbose=True, debug=debug)
# #     
# #         img1, outxml1 = analysis_cli_gulin(datasets, 
# #                                          preset_metab[1],
# #                                          preset_combine,
# #                                          preset_water,
# #                                          preset_ecc,
# #                                          out_base1,
# #                                          'indiv_'+out_prefix,
# #                                          verbose=true)
    
    

#def main():
if __name__ == '__main__':

    debug          = False
    verbose        = True
    single_process = False
    nprocess       = 12

    fbase     = 'D:\\Users\\bsoher\\projects\\2015_gulin_BRP\\data_sharing\\BRP_twix_v2\\'
    out_base0 = 'D:\\Users\\bsoher\\projects\\2015_gulin_BRP\\data_sharing\\BRP_twix_v2\\results_basis_mixed_v2\\'
    out_base1 = 'D:\\Users\\bsoher\\projects\\2015_gulin_BRP\\data_sharing\\BRP_twix_v2\\results_basis_indiv\\'

    fpreset_coil  =  fbase+'preset_analysis_brp_slaser_coil_v1.xml'
    fpreset_ecc   =  fbase+'preset_analysis_brp_slaser_ecc_v1.xml'
    fpreset_water =  fbase+'preset_analysis_brp_slaser_water_v1.xml'
    fpreset_metab = [fbase+'preset_analysis_brp_slaser_metab_mixed_v2_increasedInitval.xml',]
#    fpreset_metab = [fbase+'preset_analysis_brp_slaser_metab_mixed_v1.xml',]

#     fpreset_metab = [fbase+'preset_slaser_metab_basis_mixed.xml', 
#                      fbase+'preset_slaser_metab_basis_indiv.xml']
#     fpreset_coil  =  fbase+'preset_slaser_combine.xml'
#     fpreset_water =  fbase+'preset_slaser_water.xml'
#     fpreset_ecc   =  fbase+'preset_slaser_ecc.xml'

    
    fdata = ['S1\\V1\\meas_MID00347_FID24051_CBWM_WS64.dat',
            'S1\\V2\\meas_MID00040_FID25206_CBWM_WS64_manTRA.dat',
            'S2\\V1\\meas_MID00148_FID24553_CBWM_WS64_man_wROT.dat',
            'S2\\V2\\meas_MID00520_FID26915_CBWM_WS64.dat',
            'S3\\V1\\meas_MID00329_FID25911_CBWM_WS64.dat',
            'S3\\V2\\meas_MID00613_FID28758_CBWM_WS64.dat',
            'S4\\V1\\meas_MID00257_FID29236_CBWM_WS64.dat',
            'S4\\V2\\meas_MID00146_FID30165_CBWM_WS64.dat',
            'S5\\V1\\meas_MID00062_FID30294_CBWM_WS64.dat',
            'S5\\V2\\meas_MID00259_FID30493_CBWM_WS64.dat',
            'S6\\V1\\meas_MID00393_FID39482_CBWM_WS64.dat',
            'S6\\V2\\meas_MID00148_FID39689_CBWM_WS64.dat',
            'S7\\V1\\meas_MID00090_FID22649_CBWM_WS64_Tra.dat',
            'S7\\V2\\meas_MID00257_FID22816_CBWM_WS64_traMan.dat',
            'S7\\V2_B\\meas_MID00250_FID22809_CBWM_WS64.dat',
            'S8\\V1\\meas_MID00106_FID27202_CBWM_WS64_TRA.dat',
            'S8\\V1_B\\meas_MID00105_FID27201_CBWM_WS64.dat',
            'S8\\V2\\meas_MID00536_FID28681_CBWM_WS64.dat',
            'S9\\V1\\meas_MID00218_FID38117_CBWM_WS64.dat',
            'S9\\V2\\meas_MID00541_FID41901_CBWM_WS64.dat',
             ]

    _datafiles = [fbase+item for item in fdata]
    
#    datafiles = _datafiles 
    datafiles = [_datafiles[8],]
#    datafiles = _datafiles[0:5]
    # Basic file checking for existence

    msg = ''
    for datafile in datafiles:

        if not os.path.isfile(datafile):
            msg = """Main DATAFILE does not exist "%s".""" % datafile 

        if msg:        
            print >> sys.stderr, msg
            print >> sys.stdout, msg
            sys.exit(-1)
    
    if not os.path.isfile(fpreset_metab[0]):
        msg = """PRESETFILE_Metab does not exist "%s".""" % fpreset_metab[0] 
#     if not os.path.isfile(fpreset_metab[1]):
#         msg = """PRESETFILE_Metab does not exist "%s".""" % fpreset_metab[1] 
    if not os.path.isfile(fpreset_coil):
        msg = """PRESETFILE_Combine does not exist "%s".""" % fpreset_coil
    if not os.path.isfile(fpreset_water):
        msg = """PRESETFILE_Water does not exist "%s".""" % fpreset_water
    if not os.path.isfile(fpreset_ecc):
        msg = """PRESETFILE_Ecc does not exist "%s".""" % fpreset_ecc
    

    if len(datafiles) == 1 or single_process:

        for datafile in datafiles:
            params = [datafile, fbase, out_base0, out_base1, fpreset_coil, fpreset_ecc, fpreset_water, fpreset_metab]
            analysis_kernel(params)
    else:
        params = []
        for datafile in datafiles:
            params.append([datafile, fbase, out_base0, out_base1, fpreset_coil, fpreset_ecc, fpreset_water, fpreset_metab])
            
        pool = multiprocessing.Pool(processes=nprocess)
        results = pool.map(analysis_kernel, params)



        
#if __name__ == '__main__':
#    main()        
        