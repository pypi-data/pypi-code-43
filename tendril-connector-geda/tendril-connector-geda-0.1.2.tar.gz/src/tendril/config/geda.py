

from tendril.utils.config import ConfigOption
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)

depends = ['tendril.config.core']


config_elements_geda = [
    ConfigOption(
        'GEDA_SCHEME_DIR',
        "'/usr/share/gEDA/scheme'",
        "The 'scheme' directory of the gEDA installation to use."
    ),
    ConfigOption(
        "USE_SYSTEM_GAF_BIN",
        "True",
        "Whether to use the gEDA binary located in system PATH. This config "
        "option is present to allow you to switch the gEDA instance tendril "
        "uses from your system default to a manually installed later version."
        "In order to generate schematic PDFs on a headless install, you need "
        "to have a version of gEDA that includes the `gaf` tool."
    ),
    ConfigOption(
        "GEDA_HAS_GAF",
        "True",
        "Whether you have a version of gEDA which includes the gaf utility. "
        "If it doesn't, we'll try to use gschem instead."
    ),
    ConfigOption(
        'GAF_BIN_ROOT',
        "None",
        "If system gEDA binaries are not to be used, specify the path to the "
        "'bin' folder where the correct 'gEDA' binaries go."
    ),
    ConfigOption(
        'GAF_ROOT',
        "os.path.join(os.path.expanduser('~'), 'gEDA2')",
        "The path to your gEDA gaf folder (named per the gEDA quickstart "
        "tutorial), within which you have your symbols, footprints, etc. "
    ),
    ConfigOption(
        'GEDA_SYMLIB_ROOT',
        "os.path.join(GAF_ROOT, 'symbols')",
        "The folder containing your gEDA symbols."
    ),
    ConfigOption(
        'GEDA_SUBCIRCUITS_ROOT',
        "os.path.join(GAF_ROOT, 'pieces')",
        "The folder containing schematics for your gEDA subcircuit symbols."
    ),
    ConfigOption(
        'MAKE_GSYMLIB_IMG_CACHE',
        "True",
        "Whether or not to generate the geda symbol library image cache."
    ),
]


def load(manager):
    logger.debug("Loading {0}".format(__name__))
    manager.load_elements(config_elements_geda,
                          doc="gEDA Connector Configuration")
