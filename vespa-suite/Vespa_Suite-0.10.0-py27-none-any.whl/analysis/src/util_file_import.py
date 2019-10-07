# Python modules
from __future__ import division
import os
import imp
import abc

# 3rd party modules
import numpy as np

# Our modules
import vespa.analysis.src.mrs_dataset as mrs_dataset
import vespa.analysis.src.block_raw_probep as block_raw_probep
import vespa.analysis.src.block_raw_cmrr_slaser as block_raw_cmrr_slaser
import vespa.analysis.src.block_raw_edit_fidsum as block_raw_edit_fidsum
import vespa.analysis.src.block_prep_fidsum as block_prep_fidsum
import vespa.analysis.src.block_prep_wbnaa as block_prep_wbnaa
import vespa.analysis.src.block as block_prep_megalaser
import vespa.analysis.src.block_prep_timeseries as block_prep_timeseries
import vespa.analysis.src.util_import as util_import

import vespa.analysis.src.fileio.bruker as fileio_bruker
import vespa.analysis.src.fileio.ge_probe as fileio_ge_probe
import vespa.analysis.src.fileio.dicom_siemens as fileio_dicom_siemens
import vespa.analysis.src.fileio.dicom_siemens_fidsum as fileio_dicom_siemens_fidsum
import vespa.analysis.src.fileio.dicom_siemens_timeseries as fileio_dicom_siemens_timeseries
import vespa.analysis.src.fileio.siemens_rda as fileio_siemens_rda
import vespa.analysis.src.fileio.dicom_philips as fileio_dicom_philips
import vespa.analysis.src.fileio.dicom_philips_fidsum as fileio_dicom_philips_fidsum
import vespa.analysis.src.fileio.philips_spar as fileio_philips_spar
import vespa.analysis.src.fileio.philips_fidsum as fileio_philips_fidsum
import vespa.analysis.src.fileio.varian as fileio_varian
import vespa.analysis.src.fileio.vasf as fileio_vasf
import vespa.analysis.src.fileio.vasf_fidsum as fileio_vasf_fidsum
import vespa.analysis.src.fileio.util_exceptions as util_exceptions

import vespa.common.mrs_data_raw as mrs_data_raw
import vespa.common.mrs_data_raw_probep as mrs_data_raw_probep
import vespa.common.mrs_data_raw_cmrr_slaser as mrs_data_raw_cmrr_slaser
import vespa.common.mrs_data_raw_fidsum as mrs_data_raw_fidsum
import vespa.common.mrs_data_raw_timeseries as mrs_data_raw_timeseries
import vespa.common.mrs_data_raw_uncomb as mrs_data_raw_uncomb
import vespa.common.mrs_data_raw_fidsum_uncomb as mrs_data_raw_fidsum_uncomb
import vespa.common.mrs_data_raw_wbnaa as mrs_data_raw_wbnaa
import vespa.common.mrs_data_raw_edit_fidsum as mrs_data_raw_edit_fidsum
import vespa.common.util.misc as util_misc

import vespa.common.configobj as configobj


_MSG_MULTIFILE_ATTRIBUTE_MISMATCH = """
The dimensions and/or sweep widths in the selected data files differ.
 
Multifile selection is only available for single voxel data files.
 
Please select single voxel data files with same dimensions and sweep width."""
 
_MSG_MULTIFILE_TYPE_MISMATCH = """
More that one set of raw data was read from the file(s) selected, however, not all were of the same format type (summed FIDs or not).
 
Where multifile selection is allowed, or multiple datasets are being read out of one file, all files must return the same types of data."""
 

_MSG_OPEN_ATTRIBUTE_MISMATCH = """
The dimensions and/or sweep width of the currently open datasets differ from those of the file(s) you asked to open.
  
You can open these files, but first you have to close all currently open datasets.
"""
  
_MSG_OPEN_TYPE_MISMATCH = """
The currently open datasets differ from those of the file(s) you asked to open in that they are not all of the same format type (summed FIDs or not).
 
You can open these files, but first you have to close all currently open datasets.
"""
 
_MSG_UNSUPPORTED_DIMENSIONALITY = """
The file(s) you opened contains SI datasets. Vespa doesn't support SI at this time.
"""

_MSG_INCORRECT_DIMENSIONALITY = """
The file you selected is likely an SVS file but has a dimension that is not supported by this Import class. One possibility is that this is a Fidsum format.

Please try opening this file with a different Import format.
"""
 
_MSG_PRESET_MISMATCH = """
One or more of the selected VIFF files is an Analysis Preset file. These can not be opened as datasets.
"""
 
_MSG_OPEN_ATTRIBUTE_MISMATCH = """
The dimensions and/or sweep width of the currently open datasets differ from those of the file(s) you asked to open.
 
You can open these files, but first you have to close all currently open datasets.
"""
 
_MSG_OPEN_ZEROFILL_MISMATCH = """
The zerofill factor of the currently open datasets differ from those of the file you asked to open.
 
You can open this file, but the zero fill factor of the open datasets needs to be changed.
"""
 
_MSG_NO_DATASETS_FOUND = """The file "%s" doesn't contain any datasets."""

_MSG_INCOMPLETE_HEADER_PARAMETERS = """Import header missing a necessary parameter -> """




########################################################################
# This is a non-GUI based module that sets up a dictionay that maps 
# import data types to Python modules with parser classes/objects. Vespa
# Analysis used to have a few hard coded 'standard' formats (eg. siemens
# dicom, siemens rds, GE probe, etc.) but we have switched over to have
# all formats being mapped through this helper module. We did this so 
# it would be available for the CLI (command line interface) usages.
#
# NB. If no filename is provided to the program, eg in CLI mode, then 
#     only the default data classes are returned.
#
########################################################################


# these are the default import data classes - used to be hard coded in main()

STANDARD_CLASSES_LOFL = [
'[separator100]',
'[import_bruker]',
'path=vespa.analysis.src.fileio.bruker',
'class_name=RawReaderBruker',
'menu_item_text=Bruker',
'ini_file_name=import_bruker',
'[import_ge_probe]',
'path=vespa.analysis.src.fileio.ge_probe',
'class_name=RawReaderGeProbe',
'menu_item_text=GE PROBE (*.7)',
'ini_file_name=import_ge_probe',
'[import_philips_dicom]',
'path=vespa.analysis.src.fileio.dicom_philips',
'class_name=RawReaderDicomPhilips',
'menu_item_text=Philips DICOM',
'ini_file_name=import_philips_dicom',
'[import_philips_dicom_fidsum]',
'path=vespa.analysis.src.fileio.dicom_philips_fidsum',
'class_name=RawReaderDicomPhilipsFidsum',
'menu_item_text=Philips DICOM Sum FIDs',
'ini_file_name=import_philips_dicom_fidsum',
'[import_philips_spar]',
'path=vespa.analysis.src.fileio.philips_spar',
'class_name=RawReaderPhilipsSpar',
'menu_item_text=Philips (*.spar/sdat)',
'ini_file_name=import_philips_spar',
'[import_philips_fidsum]',
'path=vespa.analysis.src.fileio.philips_fidsum',
'class_name=RawReaderPhilipsFidsum',
'menu_item_text=Philips Sum FIDs',
'ini_file_name=import_philips_fidsum',
'[import_siemens_dicom]',
'path=vespa.analysis.src.fileio.dicom_siemens',
'class_name=RawReaderDicomSiemens',
'menu_item_text=Siemens DICOM',
'ini_file_name=import_siemens_dicom',
'[import_siemens_dicom_fidsum]',
'path=vespa.analysis.src.fileio.dicom_siemens_fidsum',
'class_name=RawReaderDicomSiemensFidsum',
'menu_item_text=Siemens DICOM Sum FIDs',
'ini_file_name=import_siemens_dicom_fidsum',
'[import_siemens_dicom_timeseries]',
'path=vespa.analysis.src.fileio.dicom_siemens_timeseries',
'class_name=RawReaderDicomSiemensTimeseries',
'menu_item_text=Siemens DICOM Timeseries',
'ini_file_name=import_siemens_dicom_timeseries',
'[import_siemens_rda]',
'path=vespa.analysis.src.fileio.siemens_rda',
'class_name=RawReaderSiemensRda',
'menu_item_text=Siemens Export (*.rda)',
'ini_file_name=import_siemens_rda',
'[import_varian]',
'path=vespa.analysis.src.fileio.varian',
'class_name=RawReaderVarian',
'menu_item_text=Varian',
'ini_file_name=import_varian',
'[import_vasf]',
'path=vespa.analysis.src.fileio.vasf',
'class_name=RawReaderVasf',
'menu_item_text=VASF (*.rsd/rsp)',
'ini_file_name=import_vasf',
'[import_vasf_fidsum]',
'path=vespa.analysis.src.fileio.vasf_fidsum',
'class_name=RawReaderVasfFidsum',
'menu_item_text=VASF Sum FIDs (*.rsd/rsp)',
'ini_file_name=import_vasf_fidsum',
'[separator101]',
]







def set_import_data_classes(filename=''):

    # -----------------------------------------------------------------
    # these are the standard data classes we guarantee are provided
    
    full_cfg = configobj.ConfigObj(STANDARD_CLASSES_LOFL, encoding="utf-8")

    if filename:
       
        # these are any additional user defined files
        user_cfg = configobj.ConfigObj(filename, encoding="utf-8")

        # merge default and user config 'file' settings. Note that as written the
        # user config settings will overwrite any duplicates in the default values
        full_cfg.merge(user_cfg)
    
    # now we fill a dict with the reader object and default path name for each
    # import data class type and send it bact to theuser.
    
    items = { }
    msg   = ''
    
    for module_name in full_cfg.keys():
        if not'separator' in module_name.lower():

            section = full_cfg[module_name]
            path    = section["path"]

            if 'vespa.analysis.src.fileio' in path:

                items[module_name] = standard_data_module(path)
                
            else:
                
                # to be polite we check to be sure that the path and file exists,
                # but there are so many ways this could go wrong ...
                
                if os.path.exists(path):
                    module = imp.load_source(module_name, path)
                else:
                    msg1 = """\nI couldn't find the file "{0}" referenced in {1}.""".format(path,filename)
                    msg += msg1.format(path)
                    continue

                # Save the reader class & INI file name associated with this menu item.
                
                klass = getattr(module, section["class_name"])
                items[module_name] = (klass, section["ini_file_name"])
            
    return items, full_cfg, msg


def standard_data_module(path):
    """
    These are the data format classes that used to be included in Analysis 
    automatically. More recently, all data format classes are listed in the
    file analysis_import_menu_additions.ini file. So we need to be able to 
    add these formats if they don't exist in the INI file
    
    """
    if path == 'vespa.analysis.src.fileio.bruker':
        item = (fileio_bruker.RawReaderBruker, "import_bruker")
    elif path == 'vespa.analysis.src.fileio.ge_probe':
        item = (fileio_ge_probe.RawReaderGeProbe, "import_ge_probe")
    elif path == 'vespa.analysis.src.fileio.dicom_philips':
        item = (fileio_dicom_philips.RawReaderDicomPhilips, "import_dicom_philips")
    elif path == 'vespa.analysis.src.fileio.dicom_philips_fidsum':
        item = (fileio_dicom_philips_fidsum.RawReaderDicomPhilipsFidsum, "import_dicom_philips_fidsum")
    elif path == 'vespa.analysis.src.fileio.philips_spar':
        item = (fileio_philips_spar.RawReaderPhilipsSpar, "import_philips_spar")
    elif path == 'vespa.analysis.src.fileio.philips_fidsum':
        item = (fileio_philips_fidsum.RawReaderPhilipsFidsum, "import_philips_fidsum")
    elif path == 'vespa.analysis.src.fileio.dicom_siemens':
        item = (fileio_dicom_siemens.RawReaderDicomSiemens, "import_dicom_siemens")
    elif path == 'vespa.analysis.src.fileio.dicom_siemens_fidsum':
        item = (fileio_dicom_siemens_fidsum.RawReaderDicomSiemensFidsum, "import_dicom_siemens_fidsum")
    elif path == 'vespa.analysis.src.fileio.dicom_siemens_timeseries':
        item = (fileio_dicom_siemens_timeseries.RawReaderDicomSiemensTimeseries, "import_dicom_siemens_timeseries")
    elif path == 'vespa.analysis.src.fileio.siemens_rda':
        item = (fileio_siemens_rda.RawReaderSiemensRda, "import_siemens_rda")
    elif path == 'vespa.analysis.src.fileio.varian':
        item = (fileio_varian.RawReaderVarian, "import_varian")
    elif path == 'vespa.analysis.src.fileio.vasf':
        item = (fileio_vasf.RawReaderVasf, "import_vasf")
    elif path == 'vespa.analysis.src.fileio.vasf_fidsum':
        item = (fileio_vasf_fidsum.RawReaderVasfFidsum, "import_vasf_fidsum")
    else:
        item = None
        
    return item


def get_datasets_cli(datafile, section_name, open_dataset=None):
    """
    This is only called by command line scripts. It shortcuts all the GUI 
    complexity. It does assume that Vespa is installed and has INI files in 
    their normal locations.
    
    """
    fname = os.path.join(util_misc.get_data_dir(), "analysis_import_menu_additions.ini")
    classes, _, _ = set_import_data_classes(filename=fname)
    if section_name not in classes.keys():
        raise ValueError('Could not find section named %s in FileImportClasses dict' % (section_name,)) 
    reader, _ = classes[section_name]
    reader = reader()
    reader.filenames = [datafile,]
    datasets, msg = get_datasets(reader, open_dataset)
    return datasets
    

def get_datasets(reader, open_dataset=None):
    
    msg = ''
    datasets = []
    
    # as this point, we assume reader has had picfile() method, or some other
    # file selection method, already called and is ready to go.
    
    try:
        # Step 1
        #
        # Return one or more DataRawXxxx objects that indicate what
        # sort of data was read in by the reader
        raws = reader.read_raws(open_dataset=open_dataset)
    except IOError:
        msg = "One or more of the files couldn't be read due to a disk error."

    except util_exceptions.MultifileAttributeMismatchError:
        msg = _MSG_MULTIFILE_ATTRIBUTE_MISMATCH

    except util_exceptions.MultifileTypeMismatchError:
        msg = _MSG_MULTIFILE_TYPE_MISMATCH

    except util_exceptions.UnsupportedDimensionalityError:
        # Note that this also catches SIDataError which is a
        # subclass of UnsupportedDimensionalityError
        msg = _MSG_UNSUPPORTED_DIMENSIONALITY

    except util_exceptions.IncorrectDimensionalityError:
        # Note that this also catches SIDataError which is a
        # subclass of UnsupportedDimensionalityError
        msg = _MSG_INCORRECT_DIMENSIONALITY

    except util_exceptions.OpenFileAttributeMismatchError:
        msg = _MSG_OPEN_ATTRIBUTE_MISMATCH

    except util_exceptions.OpenFileTypeMismatchError:
        msg = _MSG_OPEN_TYPE_MISMATCH

    except util_exceptions.FileNotFoundError, error_instance:
        msg = unicode(error_instance)

    except util_exceptions.OpenFileUserReadRawError, error_instance:
        if not error_instance:
            error_instance = "User read_raw raised OpenFileUserReadRawError"
        msg = unicode(error_instance)
        
    except util_exceptions.IncompleteHeaderParametersError, e:
        if not e:
            e = 'None'
        msg = unicode(_MSG_INCOMPLETE_HEADER_PARAMETERS) + unicode(e)


    if not msg:

        # All is well. Convert these raw objects into fully-fledged
        # dataset objects.
        if open_dataset:
            zero_fill_multiplier = open_dataset.zero_fill_multiplier
        else:
            zero_fill_multiplier = 0

        # Step 2
        #
        # See if any data types need special classes. We usually only
        # look for raw fidsum classes which trigger a prep fidsum block.
        block_class_specs = [ ]
        for raw in raws:
            d = { }
            if isinstance(raw, mrs_data_raw_probep.DataRawProbep):
                d["raw"] = block_raw_probep.BlockRawProbep
            if isinstance(raw, mrs_data_raw_edit_fidsum.DataRawEditFidsum):
                d["raw"] = block_raw_edit_fidsum.BlockRawEditFidsum
            if isinstance(raw, mrs_data_raw_cmrr_slaser.DataRawCmrrSlaser):
                d["raw"] = block_raw_cmrr_slaser.BlockRawCmrrSlaser
                d["prep"] = block_prep_fidsum.BlockPrepFidsum
            if isinstance(raw, mrs_data_raw_fidsum.DataRawFidsum):
                d["prep"] = block_prep_fidsum.BlockPrepFidsum
            if isinstance(raw, mrs_data_raw_timeseries.DataRawTimeseries):
                d["prep"] = block_prep_timeseries.BlockPrepTimeseries
            if isinstance(raw, mrs_data_raw_uncomb.DataRawUncomb):
                d["prep"] = block_prep_fidsum.BlockPrepFidsum
            if isinstance(raw, mrs_data_raw_fidsum_uncomb.DataRawFidsumUncomb):
                d["prep"] = block_prep_fidsum.BlockPrepFidsum
            if isinstance(raw, mrs_data_raw_wbnaa.DataRawWbnaa):
                d["prep"] = block_prep_wbnaa.BlockPrepWbnaa
            if isinstance(raw, mrs_data_raw_edit_fidsum.DataRawEditFidsum):
                d["prep"] = block_prep_fidsum.BlockPrepFidsum
            block_class_specs.append(d)

        f = lambda raw, block_classes: mrs_dataset.dataset_from_raw(raw,
                                                          block_classes,
                                                   zero_fill_multiplier)
        datasets = map(f, raws, block_class_specs)

    if datasets:
        # We opened something successfully, so we check if any datasets are associated
        for i,dataset in enumerate(datasets):

            # Step 3
            #
            # Sometimes the datasets returned from the reader need to know
            # about each other. 
            
            # The PROBE-P GE data from a Pfile contains both water and water 
            # suppressed data, so it would be good if when we go to save to a 
            # VIFF file that we save both so they are available again when we open it.
            if isinstance(dataset.blocks['raw'], block_raw_probep.BlockRawProbep):
                if i == 0 and len(datasets)>=2:
                    dataset.blocks['raw'].set_associated_datasets([datasets[1]])

            # Here the edited data reader should return four datasets, one for
            # each state of editing pulses ON, OFF and calculated SUM and DIFF.
            # We associate all four files into the raw block. This will save
            # provenance for all states. Note that when we go to save the dataset
            # the copy of self that is in the associated raw datasets will be
            # filtered out.
            if isinstance(raws[0], mrs_data_raw_edit_fidsum.DataRawEditFidsum):
                dataset.blocks['raw'].set_associated_datasets([datasets[0], datasets[1], datasets[2], datasets[3]])

            # Here the cmrr slaser data reader should return 6 datasets, coil_combine 
            # (1 FID), ecc1 (2 FIDs), water1 (2 FIDs), metab64 (64 FIDs), ecc2 (2 FIDs) 
            # and water2 (2 FIDs). This will save provenance for all states. Note that 
            # when we go to save the dataset the copy of self that is in the associated 
            # raw datasets will be filtered out.
            if isinstance(raws[0], mrs_data_raw_cmrr_slaser.DataRawCmrrSlaser):
                dataset.blocks['raw'].set_associated_datasets([datasets[0], datasets[1], datasets[2], datasets[3], datasets[4], datasets[5]])
    
    return datasets, msg




#------------------------------------------------------------------------------

def open_viff_dataset_file(filenames):
    """
    VIFF - Vespa Interchange File Format - is the XML format for data
    saved from or opened up into the Analysis application. This is the
    only format that is actually 'opened' by Analysis, all other formats
    are considered 'imports'.

    Note that we only allow people to open a single VIFF file as opposed
    to DICOM, VASF or other imported formats where we allow users to
    open multiple files which are then concatenated into one Dataset
    object.

    If the open is successful (and the dimensions match to any existing
    data), the dataset is opened into a new dataset tab.

    The Dataset object is returned (or None if the user
    doesn't choose a file), along with a list of the filenames opened.
    """
    datasets = []
    for filename in filenames:
        msg = ""
        try:
            importer = util_import.DatasetImporter(filename)
        except IOError:
            msg = """I can't read the file "%s".""" % filename
        except SyntaxError:
            msg = """The file "%s" isn't valid Vespa Interchange File Format.""" % filename

        if msg:
            return [None,], msg
        
        # Time to rock and roll!
        dsets = importer.go()

        for dataset in dsets:
            # check to ensure that none of the selected files is
            # actually an Analysis Preset file
            if dataset.behave_as_preset:
                msg = "Analysis - Preset Filetype Mismatch - No data in Preset file, can't load"
                return [None,], msg
            
        for item in dsets:
            datasets.append(item)


    if datasets:

        for dataset in datasets:
            
            # Check that all datasets correspond to the first. 
            # The attributes open_dataset.raw_dims of the
            # currently open dataset(s) must match those of the
            # dataset(s) that we're trying to open.
            # To compare, we grab one of the currently open
            # datasets. It doesn't matter which one since they
            # all have matching attributes.
            #
            # Note. Dimensionality rules also apply to zerofill

            open_dataset = datasets[0]
            if (dataset.raw_dims[0] == open_dataset.raw_dims[0]) and \
               (np.round(dataset.sw,2) == np.round(open_dataset.sw,2)):
                # All is well!
                pass
            else:
                # The dimensions don't match. We can't open these files.
                return [None,], _MSG_OPEN_ATTRIBUTE_MISMATCH

            if (dataset.spectral_dims == open_dataset.spectral_dims):
                # All is well!
                pass
            else:
                # The zerofill factors don't match. We can't open these files.
                return [None,], _MSG_OPEN_ZEROFILL_MISMATCH


        for dataset in datasets:
            dataset.set_associated_datasets(datasets)
            if dataset.id == datasets[-1].id:
                dataset.dataset_filename = filename
                # dataset.filename is an attribute set only at run-time
                # to maintain the name of the VIFF file that was read in
                # rather than deriving a filename from the raw data
                # filenames with *.xml appended. But we need to set this
                # filename only for the primary dataset, not the associated
                # datasets. Associated datasets will default back to their
                # raw filenames if we go to save them for any reason
            else:
                dataset.dataset_filename = ''
                
        return datasets, ''

    else:
        if not datasets:
            return [None,], _MSG_NO_DATASETS_FOUND % filename
