""" Provide classes to handle device list 'database' for friendly inline manipulation

"""

from . import api
from . import ioxls
from . import keys as K

class _FieldsHandler:
    def fields(self):
        """ iter on fields 
        
        fields can be interpreted as column name
        each oteration return a Field object 
        """
        for field_dict in self._fields.values():
            yield Field(field_dict)
    
    def field_keys(self):
        """ iter on field keys  
        
        fields can be interpreted as column name
        each oteration return a str key value 
        """
        for field_name in self._fields.keys():
            yield field_name
    
    def field_items(self):
        """ iter on field keys,Field object pairs  
        
        fields can be interpreted as column name
        each oteration return a key, Field object pair 
        """
        for field_name, field_dict in self._fields.items():
            yield field_name, Field(field_dict)
    
    def get_field(self, field_name):
        """ return a field object of the given field """
        return Field(self._fields[field_name])

class _DevicesHandler:
                    
    def devices(self):
        """ iter on device 
        
        each oteration return a Device object 
        """
        for device_dict in self._data.values():
            yield Device(device_dict, self._fields)
    
    def device_keys(self):
        """ iter on device keys  
        
        each oteration return a str device key (device unique id)
        """
        for device_name in self._data.keys():
            yield device_name
    
    def device_items(self):
        """ iter on device 
        
        each oteration return a key, Device object  pair 
        """
        for device_name,device_dict in self._data.items():
            yield device_name, Device(device_dict, self._fields)
    
    def get_device(self, device_name):
        try:
            device_dict = self._data[device_name]
        except KeyError:
            raise ValueError('device with name %r does not exists'%device_name)
        else:
            return Device(device_dict, self._fields)    
    
    def filter_device(self, field, filter):
        devices_dict = api.filter_device(self._data, field, filter)
        return Devices(devices_dict, self._fields)
    
    def filter_device_or(self, *args):
        if len(args)%2:
            raise ValueError('expecting a even number of argument got %d'%len(args))        
        data = {}        
        for field, filter in zip(args[::2], args[1::2]):
            data.update( api.filter_device(self._data, field, filter)  )
        return Devices(data, self._fields)
    
    def filter_device_and(self, *args):
        if len(args)%2:
            raise ValueError('expecting a even number of argument got %d'%len(args))        
        data = self._data
        for field, filter in zip(args[::2], args[1::2]):
            data = api.filter_device(data, field, filter)
        return Devices(data, self._fields)
        
    
    
class Devices(_FieldsHandler, _DevicesHandler):
    """ Device List object handler 
    
    The object must be initialised witj the class method `.from_xls` from a xls device list file 
    
    >>> devices = Devices.from_xls('/path/to/HRM-00485_HCS_deviceList-3.xlsx')
        
    Methods
    -------
    devices: iterator on Device objects
    device_keys: iterator on device unique names (id)
    device_items: iterator on 'device unique names'/'Device object' pair 
    get_device(device_name): return Device object of given name 
    
    fields: iterator on Field objects
    field_keys: iterator on field unique names (id)
    field_items: iterator on 'field unique names'/'Field object' pair 
    get_field(field_name): return Field object of given name     
    """
    _data = None
    _fields = None
    def __init__(self, data_dict, fields_dict):
        self._data = data_dict
        self._fields = fields_dict 
    
    def __getattr__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            pass
        
        try:
            return self.__dict__[attr]
        except KeyError:
            try:
                return self.get_device(attr)
            except ValueError:
                raise AttributeError('%r is not an attribute of Devices neither a device name'%attr)
    
    def __getitem__(self, item):        
        try:
            return self.get_device(item)
        except ValueError:
            raise KeyError('%r'%item)
    
    def __iter__(self):
        for device in self.devices():
            yield device
    
    def __dir__(self):
        return self.device_keys()
    
    def __len__(self):
        return len(self._data)
    
    def keys(self):
        return self.device_keys()
    
    @classmethod
    def from_xls(cls, file_path, version_cell=None, rules=None):
        data_dict, fields_dist = ioxls.open_device_list(file_path, version_cell=version_cell, rules=rules)
        return cls(data_dict, fields_dist)    
    
class Field:
    def __init__(self, field_dict):
        self._field = field_dict
    
    def parse(self, value):
        """ parse a new value for this field 
        
        WARNING: some field property can be changed (e.g. 'choices' or 'min', 'max')
        Use only this method just before adding a new value in the data.  
        """
        value = self._field[K.PARSER](self._field, value)
        return value
    
    @property
    def name(self):
        return self._field[K.NAME]
    
    @property
    def choices(self):
        return self._field[K.CHOICES]
        
    def __getattr__(self, attr):
        try:
            return self.__dict__[attr]
        except KeyError:
            try:
                value =  self._field[attr]
            except KeyError:
                raise AttributeError('%r is not an attribute of Field neither a property name'%attr)
            else:
                return value
    
    def __getitem__(self, item):        
        try:
            value =  self._field[item]
        except KeyError:
            raise KeyError('%r'%item)
        else:
            return value
    
    def __dir__(self):
        return self._field.keys()
    
class Device(_FieldsHandler):
    _data = None
    _fields = None
    def __init__(self, device_dict, fields_dict):
        self._data = device_dict
        self._fields = fields_dict
    
    def keys(self):
        return self.property_keys()
    
    def properties(self):
        """ iter on value properties 
        
        each iteration return a DeviceProperty object 
        """
        for field_name in self.field_keys():
            yield DeviceProperty(self._data[field_name])
    
    def property_keys(self):
        """ iter on value property keys 
        
        each iteration return a str key 
        """
        for field_name in self.field_keys():
            yield field_name
    
    def property_items(self):
        """ iter on value property keys 
        
        each iteration return a str key / DeviceProperty object  pair
        """
        for field_name in self.field_keys():
            yield field_name, DeviceProperty(self._data[field_name]) 
    
    def get_property(self, field_name):
        try:
            property_dict = self._data[field_name]            
        except KeyError:
            raise ValueError('%r is not a property of device')
            
        return DeviceProperty(property_dict)
    
    def __getattr__(self, attr):
        try:
            return self.__dict__[attr]
        except KeyError:
            try:
                deviceProperty =  self.get_property(attr)
            except ValueError:
                raise AttributeError('%r is not an attribute of Device neither a property name'%attr)
            else:
                return deviceProperty.value
    
    def __getitem__(self, item):        
        try:
            deviceProperty =  self.get_property(item)
        except ValueError:
            raise KeyError('%r'%item)
        else:
            return deviceProperty.value
    
    def __repr__(self):
        txt = []
        for property in self.properties():
            txt.append(repr(property))
        return "\n".join(txt)
        
    def __dir__(self):
        return self._fields.keys()
    
class DeviceProperty:
    def __init__(self, property_dict):
        self._data = property_dict
    
    @property
    def field(self):
        return Field(self._data[K.FIELD])        
    
    @property
    def value(self):
        return self._data[K.VALUE]
    
    @property
    def cell(self):
        return self._data[K.CELL]
    
    def __repr__(self):
        return f"{self.field.name}: {self.value}"
        
    def __dir__(self):
        return self._data[K.FIELD].keys()
    
    
    
    