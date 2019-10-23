import oyaml as yaml
import zmq
from PyQt5.QtCore import QLocale
from oyaml import MappingNode
from pint import UnitRegistry
from pint.quantity import build_quantity_class

QLocale.setDefault(QLocale("US"))


# TODO: Make save positions group resizable
# TODO: Offer tooltip for saved comment so long comment can be seen
# TODO: Add process ID for session device

class GuiTypeError(Exception):
    pass


class WriteException(Exception):
    pass


class DeviceError(Exception):
    pass


class DeviceUnitError(DeviceError):
    pass


class CommandFormatException(DeviceError):
    pass


class DeviceServerError(DeviceError):
    pass


class DeviceClientError(DeviceError):
    pass


class DeviceUnknownError(DeviceError):
    pass


class MacroException(DeviceError):
    pass


class SetpointTimeoutException(MacroException):
    pass


def device_constructor(loader, suffix, node):
    arguments = loader.construct_mapping(node, deep=True)
    mapping_node = MappingNode(u'tag:yaml.org,2002:python/object{}'.format(suffix), [])
    new_device = loader.construct_object(mapping_node)
    new_device.__init__(**arguments)
    return new_device


yaml.add_multi_constructor(u'!Device', device_constructor)
yaml.add_multi_constructor(u'!Widget', device_constructor)

# Logging setup
SEP = "@!"  # Separator character

"""
Section of units setup, helper functions, ...
"""
units = UnitRegistry()
units.derived_units = []
q_class = build_quantity_class(units)
session = None

def pint_constructor(loader, node):
    value = loader.construct_scalar(node)
    return units.Quantity(value)


def pint_dumper(dumper, data):
    return dumper.represent_scalar('!Pint', str(data))


yaml.add_representer(units.Quantity, pint_dumper)
yaml.add_constructor(u'!Pint', pint_constructor)

# TODO: Somehow make sure, that not two instances of session are running
