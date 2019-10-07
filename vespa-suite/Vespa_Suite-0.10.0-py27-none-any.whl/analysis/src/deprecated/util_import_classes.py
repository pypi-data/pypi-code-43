# Python modules
from __future__ import division
import os
import imp
import abc

# 3rd party modules
import wx

# Our modules
import vespa.analysis.src.fileio.bruker as fileio_bruker
import vespa.analysis.src.fileio.ge_probe as fileio_ge_probe
import vespa.analysis.src.fileio.dicom_siemens as fileio_dicom_siemens
import vespa.analysis.src.fileio.dicom_siemens_fidsum as fileio_dicom_siemens_fidsum
import vespa.analysis.src.fileio.dicom_siemens_timeseries as fileio_dicom_siemens_timeseries
import vespa.analysis.src.fileio.siemens_rda as fileio_siemens_rda
import vespa.analysis.src.fileio.philips_spar as fileio_philips_spar
import vespa.analysis.src.fileio.philips_fidsum as fileio_philips_fidsum
import vespa.analysis.src.fileio.varian as fileio_varian
import vespa.analysis.src.fileio.vasf as fileio_vasf
import vespa.analysis.src.fileio.vasf_fidsum as fileio_vasf_fidsum

import vespa.common.menu as common_menu
import vespa.common.util.config as util_common_config
import vespa.common.util.misc as util_misc
import vespa.common.configobj as configobj
import vespa.common.wx_gravy.common_dialogs as common_dialogs



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
    





