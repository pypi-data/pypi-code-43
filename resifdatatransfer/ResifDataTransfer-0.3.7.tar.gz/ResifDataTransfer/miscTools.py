"""
Miscellaneous utilities tools
"""

import os
import sys
import stat
import platform
import configparser


def bit_count(myInteger):
    """
  returns the number of bits set to 1
  http://stackoverflow.com/questions/9829578/fast-way-of-counting-bits-in-python
  """
    return bin(myInteger).count("1")


def check_python(min, max):
    """
  returns True if running Python version is between
  min and max version, else returns False
  """
    myversion = sys.version_info[0] + float("0." + str(sys.version_info[1]))
    return min <= myversion <= max


def check_platform(validatedPlatforms):
    """
  returns True if current running system is in validatedPlatforms, else False
  """
    return platform.system() in validatedPlatforms


def running_under_root():
    """
  returns True if it can be determined that we'running
  under root. False otherwise.
  """
    if getattr(os, "geteuid"):
        return os.geteuid() == 0
    return False


def load_registry(myConfigurationFile, CONFIG, paranoid=False, ghost=True):
    """
    load parameters from configuration file
    and put it in a registry-like object.
    paranoid : set True to ensure config file not readable by others
    ghost : don't raise exception if missing parameters in file   
    """
    myParser = configparser.SafeConfigParser()
    if not myParser.read(myConfigurationFile):
        raise Exception("Cannot read " + myConfigurationFile)
    # check file permissions
    if paranoid:
        mode = os.stat(myConfigurationFile)[stat.ST_MODE]
        if bool(mode & stat.S_IROTH):
            raise Exception(
                "Configuration file is readable by other users. Tip for Unix systems : chmod 600 "
                + myConfigurationFile
            )
    # for every sections and options,
    for section in CONFIG:
        for option in list(CONFIG[section].keys()):
            # if the option is found in the config file,
            if myParser.has_option(section, option):
                fieldtype = CONFIG[section][option][0]
                # get the option value according to field type
                try:
                    if fieldtype == str:
                        value = myParser.get(section, option, raw=True)
                        if value == "":
                            value = None
                    elif fieldtype == int:
                        value = myParser.getint(section, option)
                    elif fieldtype == float:
                        value = myParser.getfloat(section, option)
                    elif fieldtype == bool:
                        value = myParser.getboolean(section, option)
                    else:
                        raise Exception("Unknown type declared in registry.")
                    # if the value is not blank, update the registry
                    if value is not None:
                        CONFIG[section][option][1] = value
                # FIXME if the field is not well formatted, just ignore : use default value instead
                except ValueError:
                    pass
            # if the option was not found in the config file,
            else:
                if not ghost:
                    raise Exception(
                        "Configuration file : parameter '%s' missing in section [%s]"
                        % (option, section)
                    )


if __name__ == "__main__":
    pass
