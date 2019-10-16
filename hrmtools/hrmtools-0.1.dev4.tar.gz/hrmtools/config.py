import os 
import sys 
config_path = []
## by default look in the share directory 
__module_dir__, _ = os.path.split(__file__)
__package_dir__, __pkg__ = os.path.split(__module_dir__)

config_path.append(os.path.join(__package_dir__, "share", __pkg__, "config"))
config_path.append(os.path.join(sys.prefix, "share", __pkg__, "config"))

# also include the module/config directory in case it was not installed py setup.py
config_path.append(os.path.join(__module_dir__, "config"))

