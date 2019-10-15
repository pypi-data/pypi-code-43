#! /usr/bin/env python3.7

import pdb
import sys
from glob import glob
from json import dumps
from time import strftime
from shutil import rmtree
from types import MethodType
from nornir import InitNornir
from shutil import make_archive
from copy import copy, deepcopy
from collections import OrderedDict
from recordclass import recordclass
from os import path, remove, makedirs
from multiprocessing import Process, Queue
from yaml import load, SafeLoader, FullLoader
from nams.core import JuniperAgent, CiscoAgent
from nams.arguments import available_args, \
                           available_kwargs, \
                           arg_docstring, \
                           terminal_input

def PP(item):
    print(dumps(item, indent=4, sort_keys=True))

class RouterInfo:
    '''
    Create router info for each host. This
    will be passed into the netconf operations
    module. 'queue' and 'output_dir' will be the 
    same for all hosts. 'inventory' will always
    be different. 'requests' class attribute will
    be used only of a 'host specific' operation is
    used e.g. 'host_config', 'host_rpcs'. If these
    are present, each RouterInfo object will be its
    own copy of requests, because they'll be unique
    to the device.
    '''
 
    requests = None
    output_dir = None
    queue = None

    def __init__(self, inventory, request=None):
        # host specific inventory
        self.inventory = recordclass('inventory', inventory.keys())\
                                               (**inventory)

        #host specific requests 
        if request is not None:
            self.requests = request
 
    def __str__(self):
        return self.inventory.hostname

class Initializer:
    __doc__ = arg_docstring

    def __init__(self, *args, **kwargs):
 
        self._device_filters = [ "devices",
                                 "device_groups" ] 
 
        self._host_filters = [   "host_configs",
                                 "host_rollbacks",
                                 "host_rpcs",
                                 "host_tests" ]
 
        kwargs = self._set_default_kwargs(args, kwargs) 
        self._convert_kwargs(kwargs)
        self._validate_kwargs()
        self._validate_inventory()
        self._create_log_path()
        self._load_requests()
        self._detect_duplicate_hosts()
        self._select_devices()

    def __str__(self):
        '''
        Print the class object to display 
        available attributes and methods.
        '''
 
        line = "Available attributes and methods:\n\n"
        for item in dir(self):
            if not item.startswith("__") and not item.startswith("_"):
                if isinstance(getattr(self, item), MethodType):
                    line += f" object.{item}()\n"
                else:
                    line += f" object.{item}\n"
        return line

    def __call__(self):
        routers = self._execute()
        return routers

    def _set_default_kwargs(self, args, kwargs):
        '''
        Changes args to kwargs and sets defaults 
        of all kwargs to 'None'.
        '''
        
        # merge default's args to kwargs and set default values
        default_args = { arg["name"]:False for arg in available_args }
        default_kwargs = { kwarg["name"]:None for kwarg in available_kwargs }
        default_kwargs.update(default_args)
        
        if __name__ == "__main__": default_kwargs.update({"imported": False})
        else: default_kwargs.update({"imported": True})
 
        # merge user's args to kwargs
        args = { arg:True for arg in args }
        kwargs.update(args)
        
        # merge user and default kwargs
        result = {}
        result.update(default_kwargs)
        result.update(kwargs)         
 
        return result

    def _convert_kwargs(self, kwargs):
        '''
        Convert different object types that may be
        passed in via shell arguments.
        '''
 
        #- convert to list
        if not kwargs["devices"]: pass
        elif ( kwargs["devices"]  and   
                isinstance(kwargs["devices"], list) ):
 
            pass
        else:
            kwargs["devices"] = kwargs["devices"].split(",")
 
        # convert to dict
        if not kwargs["device_groups"]: pass
        elif ( kwargs["device_groups"]  and
               isinstance(kwargs["device_groups"], dict) ):
 
            pass
        else:
            d = {}
            filters = kwargs["device_groups"].split(",")
            for filter in filters:
                k,v = filter.split("=")
                d[k]=v
            kwargs["device_groups"] = d
  
        # change to record class object
        kwargs = recordclass('kwargs', kwargs.keys())(**kwargs)
 
        self._kwargs = kwargs

    def _validate_kwargs(self):
        ''' 
        Prevent faulty input combinations like multiple
        host filtering methods or 'commit' or without
        a configuration.
        '''
        
        # require inventory
        if  ( not self._kwargs.inventory ):
            err = "inventory file required e.g. 'config.yaml'"
            raise AssertionError(err)
               
        # allow show inventory
        if  self._kwargs.show_inventory:
            self._validate_inventory()
            PP(self.inventory)
            err = ("notice: 'show_inventory' disallows "
                   "additional tasks\n")
            raise RuntimeError(err)
            
        # shell requirements
        if not self._kwargs.imported:
        
            # require args
            if all( not v for k,v in self._kwargs.items()
                              if ( k != "inventory" and
                                   k != "imported" and 
                                   k != "silent" ) ):
                                   
              err = "more arguments needed"
              raise AssertionError(err)
 
        # require a filter
        if ( not any( [ df for df in self._device_filters 
                              if self._kwargs[df] ] ) and 
             not any( [ hf for hf in self._host_filters 
                              if self._kwargs[hf] ] ) ): 
 
             err = ("'devices', 'device_groups', 'host_configs', "
                   "'host_rollbacks', 'host_tests'  or 'host_rpcs' "
                   "is required")
 
             raise AssertionError(err)
 
        '''
        Halt if devices and device groups are both used.
        Halt if devices or device groups is used with host filters.
        Allow multiple host filters.
        '''
        potential_combos = [ ["devices","device_groups" ] ]
 
        for df in self._device_filters:
           for hf in self._host_filters:
               potential_combos.append([df, hf])
 
        for (x, y) in potential_combos:
            if ( ( self._kwargs[x] and self._kwargs[y] ) or
                 ( self._kwargs[y] and self._kwargs[x] ) ):
 
                err = f"'{x}' and '{y}' are mutually exclusive"
                raise AssertionError(err)
     
        # bugs
        if  ( self._kwargs.diff and
            ( self._kwargs.jsnapy or 
              self._kwargs.tests_file ) ):
              
            err = "'diff' and 'jsnapy' are not supported together (bug)"
            raise AssertionError(err)
        
        # output type
        if  ( self._kwargs.silent and 
              ( self._kwargs.config or
                self._kwargs.host_configs or
                self._kwargs.rollback or
                self._kwargs.host_rollbacks ) and 
              ( not self._kwargs.commit and
                not self._kwargs.diff ) ):
      
            err = ("configuring with 'silent' is not allowed "
                   "without 'commit' or 'diff'")
            raise AssertionError(err)
 
        # editing
        if  ( self._kwargs.config and
              self._kwargs.rollback ):
              
            err = "'config' and 'rollback' are mutually exclusive"
            raise AssertionError(err)
 
        if  ( self._kwargs.config and
            ( self._kwargs.host_configs or 
              self._kwargs.rollback or
              self._kwargs.host_rollbacks ) ):
              
            err = "'config' not allow with other configuration argument(s)"
            raise AssertionError(err)
 
        if  ( self._kwargs.confirm and 
            ( not self._kwargs.jsnapy and 
              not self._kwargs.tests_file ) ):
              
            err = "'confirm' requires 'jsnapy' and 'tests_file'"    
            raise AssertionError(err)
            
        if  ( self._kwargs.confirm and
            ( not self._kwargs.config and 
              not self._kwargs.host_configs and
              not self._kwargs.rollback and
              not self._kwargs.host_rollbacks ) ):
              
            err = "'confirm' requires a change"    
            raise AssertionError(err)
 
        if  ( self._kwargs.diff and
            ( not self._kwargs.config and 
              not self._kwargs.host_configs and 
              not self._kwargs.rollback and 
              not self._kwargs.host_rollbacks ) ):
              
            err = "'diff' requires configuration"    
            raise AssertionError(err)
            
        if  ( self._kwargs.diff and 
            ( self._kwargs.commit or 
              self._kwargs.comment ) ):
              
            err = "'diff' not allowed with 'commit' or 'comment'"    
            raise AssertionError(err)
 
        if  ( self._kwargs.comment and 
            ( not self._kwargs.config and 
              not self._kwargs.host_configs and 
              not self._kwargs.rollback and 
              not self._kwargs.host_rollbacks  ) ):
              
            err = "'comment' not allowed without configuration"
            raise AssertionError(err)
            
        if  ( self._kwargs.commit and 
            ( self._kwargs.config or 
              self._kwargs.host_configs or 
              self._kwargs.rollback or 
              self._kwargs.host_rollbacks ) and
              not self._kwargs.comment ):
              
            err = ("configuring with 'commit' not allowed "
                   "without 'comment'")
            raise AssertionError(err)
 
        # jsnapy
        if  ( self._kwargs.skip_check and
              self._kwargs.jsnapy != "check" ):
 
            err = "'skip_check' requires 'jsnapy' a value of 'check'"
            raise AssertionError(err)
 
        if  ( self._kwargs.jsnapy or 
              self._kwargs.tests_file or
              self._kwargs.host_tests ):
        
            if ( not self._kwargs.jsnapy ):
               
                err = ( "'jsnapy' is required with 'tests_file' "
                        "or 'host_tests'" )
                raise AssertionError(err)
                
            if ( not self._kwargs.tests_file and 
                 not self._kwargs.host_tests ):
               
                err = ( "'tests_file' or 'host_tests' " 
                        "is required with 'jsnapy'" )
                raise AssertionError(err)
 
            if ( self._kwargs.jsnapy != "check" and 
                 self._kwargs.jsnapy != "compare" ):
                 
                err = (f"'check' or 'compare' required "
                        "with jsnapy argument")
                raise AssertionError(err)

    def _validate_inventory(self):
        ''' 
        Import the inventory and verify that
        certain k,v pairs are set. 
        
        i.e. 'platform', 'username' and 'password'
        '''
        
        inv = self._kwargs.inventory
        nornir_inv = InitNornir(config_file=inv)
 
        inventory = {}
        
        for device in nornir_inv.inventory.hosts.values():
            inventory[device.name] = dict(device.items()) 
            inventory[device.name]["hostname"] = device.name
            
        inventory_OK = True
        for device, info in inventory.items():
 
            try: info["hostname"]
            except KeyError:
                print((f"notice: inventory device '{device}' "
                        "requires 'hostname'")) 
                inventory_OK = False
 
            try: info["username"]
            except KeyError:
                print((f"notice: inventory device '{device}' "
                        "requires 'username'"))
                inventory_OK = False
 
            try: info["password"]
            except KeyError:
                print((f"notice: inventory device '{device}' "
                        "requires 'password'"))
                inventory_OK = False
 
            try: info["platform"]
            except KeyError:
                print((f"notice: inventory device '{device}' "
                        "does not have a 'platform' defined"))
            else:                
                if ( not info["platform"] == "junos" and
                     not info["platform"] == "iosxr" and
                     not info["platform"] == "iosxe" ):
                     
                    print((f"notice: inventory device '{device}' "
                            "requires 'junos', 'iosxr' or 'iosxe' "
                            "as platform"))

            '''
            Hyphens not allowed in key because these are 
            converted into class attributes.  Attributes
            cannot contain '-'.
            '''
            for item in info:
                if "-" in info:
                    print((f"notice: inventory device '{device}' "
                            "key {info} contains '-'. Hyphens not allowed"))
                    inventory_OK = False

        if not inventory_OK:
            err = f"inventory is misconfigured"
            raise AssertionError(err)
 
        self.inventory = inventory 

    def _create_log_path(self):
        '''
        Create the default directories for windows,
        linux virtual environments. The home directory
        '~/' is used for logging, because 'pip install' 
        does not have access to '/var/log/'
        '''

        def dirs(locations):
            '''
            'makedirs' will create all dirs in the
            path if they do not exist and if they
            do exist, it will not delete the items.
            '''
 
            try:
                for location in locations:
                    if path.exists(location):
                        continue
                    if "log" in location: 
                        location = path.join(location, "archive")
                    mode = 0o777
                    makedirs(location, mode=mode)
            except Exception as e:
                err = f"creating main logging directories --> {e}"
                raise RuntimeError(err)

        def cfgs(location):
            '''
            Create a default configuration file.
            '''
 
            try:
                fn = path.join(location, "nams.cfg")
                with open(fn, 'w') as f:
                    comment = ('[defaults]')
                    f.write(comment)
                    f.close()
            except Exception as e:
                err = f"creating default configuration file --> {e}"
                raise RuntimeError(err)
 
        # virtual env
        if hasattr(sys, "real_prefix"):
            cfg_path = path.join(sys.prefix, "nams", "cfg")
            log_path = path.join(sys.prefix, "nams", "log" )
        # windows
        elif "win32" in sys.platform:
            cfg_path = path.join(path.expanduser("~"), "nams", "cfg")
            log_path = path.join(path.expanduser("~"), "nams", "log")
        # linux
        else:
            cfg_path = path.join(path.expanduser("~"), "nams", "cfg")
            log_path = path.join(path.expanduser("~"), "nams", "log")
 
        dirs([cfg_path, log_path]), cfgs(cfg_path)
 
        try:
            # custom output dir                
            if self._kwargs.dir_name:
                output_dir = path.join(log_path, self._kwargs.dir_name)
                if path.exists(output_dir):  
                    print((f"notice: custom output directory exists. " 
                            "overwriting"))
                    files = glob(path.join(output_dir, "*"))
                    for item in files:
                        if path.isfile(item):
                            remove(item)
                        elif path.isdir(item):
                            rmtree(item, ignore_errors=True) 
                    makedirs(path.join(output_dir, "snapshots"))
                else:
                    makedirs(path.join(output_dir, "snapshots"))
                   
            # default output dir
            else:
                time_info = strftime(f"%Y%m%d_%H%M.%S")
                output_dir = path.join(log_path, time_info)
                if not path.isdir(output_dir):            
                        makedirs(path.join(output_dir, "snapshots"))
 
        except Exception as e:
            err = f"creating output directory --> {e}"
            raise RuntimeError(err)
        else: 
            # update RouterInfo class attribute 
            setattr(RouterInfo, "output_dir", output_dir)
 
            # self instance attr 
            self.output_dir = output_dir
            self._log_path = log_path

    def _load_requests(self):
        '''
        Create a new attribute called 'self._requests' which
        contains all keys from 'self._kwargs' but with a
        value that is the loaded data e.g. the value of
        self._kwargs['config'] will contain the configuration
        rather than the path to the configuration file.  Any
        kwarg that does not require 'loading' data from a 
        source will retain the original 'self._kwargs' value.
        '''

        def read_yaml(file):
            try:
                return load(open(file), Loader=FullLoader)   
            except Exception as e:
                err = f"error reading file: {file} --> {e}"
                raise RuntimeError(err)

        def read_text(file):
            try:
                return open(file, "r").read()
            except Exception as e:
                err = f"error reading file: {file} --> {e}"
                raise RuntimeError(err)

        def load_host_files(kwarg, file_type):
            ''' 
            Load host specific files and replace
            replace the self._kwargs with a dict of 
            host specific files.
 
            e.g. {hostname1: data, hostname2: data}
            '''
 
            file_dir = self._kwargs[kwarg]
            if not path.exists(file_dir):
               err = f"{file_dir} directory does not exist"
               raise RuntimeError(err)
 
            file_dir = path.split(file_dir)
            files = glob(path.join(*file_dir, "*"))
            results = OrderedDict()
            for file in sorted(files):
                hostname = path.split(file)[-1]
                # load the text file
                if file_type == "text": data = read_text(file)
                # load the yaml file
                elif file_type == "yaml": data = read_yaml(file)
                # only load the file path
                elif file_type == "jsnapy_test": data = file 
                else: pass
                results.update({hostname: data})
   
            return results
 
        requests = deepcopy(self._kwargs)
 
        #-- schemas
        if requests["schemas"] is None:
            pass
        elif ( requests["schemas"] and 
               isinstance(requests["schemas"], list) ):
            pass
        else:
            requests["schemas"] = read_yaml(requests["schemas"])
 
        #-- rpcs
        if requests["rpcs"] is None:
            pass
        elif ( requests["rpcs"] and 
               isinstance(requests["rpcs"], dict) ):
            pass
        else:
            requests["rpcs"] = read_yaml(requests["rpcs"])
 
        #-- tests file
        if requests["tests_file"] is None:
            pass
        else:
            read_yaml(requests["tests_file"])
            
        #-- config
        if requests["config"] is None:
            pass
        elif ( requests["config"] and
               not requests["imported"] ):
 
            requests["config"] = read_text(requests["config"])
             
        elif ( requests["config"] and 
               requests["imported"] and
               ".txt" in requests["config"] ):
 
            requests["config"] = read_text(requests["config"]) 
 
        elif ( requests["config"] and 
               requests["imported"] ):
            
            pass
        else:
            err = "unknown 'config' type"
            raise RuntimeError(err)
 
        #-- host configs
        if requests["host_configs"] is None:
            pass
        elif ( requests["host_configs"] and 
               isinstance(requests["host_configs"], dict) ):
            pass
        else:
            requests["host_configs"] = load_host_files("host_configs", "text")
 
        #-- host requests
        if requests["host_rpcs"] is None:
            pass
        elif ( requests["host_rpcs"] and 
               isinstance(requests["host_rpcs"], dict) ):
            pass
        else:
            requests["host_rpcs"] = load_host_files("host_rpcs", "yaml")
 
        #-- host tests
        if requests["host_tests"] is None:
            pass
        elif ( requests["host_tests"] and 
               isinstance(requests["host_tests"], dict) ):
            pass
        else:
            requests["host_tests"] = load_host_files("host_tests", "jsnapy_test")
 
        #-- host rollbacks
        if requests["host_rollbacks"] is None:
            pass
        elif ( requests["host_rollbacks"] and 
               isinstance(requests["host_rollbacks"], dict) ):
            pass
        else:
            err = ("'host_rollbacks' as type " 
                  f"{type(requests['host_rollbacks'])} not allowed")
            raise RuntimeError(err)
 
        # self instance attr 
        self._requests = requests

    def _detect_duplicate_hosts(self):
        '''
        To allow the use of multiple host filters together,
        a check must be performed to validate that the 
        same hosts are present in every host filter. In an
        early method, host filters were converted to dicts.
        '''
        hfs = {}
        for hf in self._host_filters:
            if self._kwargs[hf] is None:
                pass
            else:
                d = {hf: sorted(self._requests[hf].keys())}
                hfs.update(d)
 
        for hf_x in hfs:
            for hf_y in hfs:
                if hfs[hf_x] != hfs[hf_y]:
                    err = ("multiple host filters requires "
                           "same hosts. see below:\n\n"
                            f"{hf_x}:\n"
                            f"{hfs[hf_x]}\n\n"
                            f"{hf_y}:\n"
                            f"{hfs[hf_y]}")
                    raise RuntimeError(err)

    def _select_devices(self):       
        ''' 
        Create a list of new class instances that will be
        passed to the netconf handler. A class instance
        will be created for each device that the tasks will 
        perform on. The filtering of devices takes place here.
        The class instance will contain class variables 
        '''

        def host_specific_requests(host_request, new_key):
            '''
            This allows host specific requests.  i.e.
            specifying configurations or rpcs unique to a device
            via files. It creates a unique request per host. 
 
            For example, if the 'host_configs' (i.e. 
            'host_request') is passed, the host specfic 
            request 'config' (i.e. 'new_key') will changed.
            Additionally, global requests like 'schemas' or 
            'rpcs' will still be performed on the host.
            '''
 
            for device in self._requests[host_request]:
                '''
                Indexing on the class object 'device.inventory' 
                is not supported. A second 'for' loop with 'else'
                overcomes this. 
                '''
                for existing_device in devices:
                    '''
                    If the RouterInfo object for the device
                    has already been created, only update
                    the specific request and don't create another 
                    RouterInfo instance for the same device.
                    '''
                    if device != existing_device.inventory.hostname:
                        pass
                    else:
                        data = self._requests[host_request][device]
                        setattr(existing_device.requests, new_key, data)
                        break
                else: 
                    '''
                    If the device is not already in the list,
                    construct a new RouterInfo object. Pass in
                    default arguments first and then update
                    the host-specific attributes.
                    '''
                    try:
                        # instantiate
                        inventory = self.inventory[device]
                        # must deep copy
                        router = deepcopy(RouterInfo(inventory, self._requests))
                        # overwrite specific attributes
                        data = self._requests[host_request][device]
                        setattr(router.requests, new_key, data)
                        # finish 
                        devices.append(router)
                    except KeyError: 
                        print(f"notice: {device} not in self.inventory")      
  
        
        devices = []

        if self._kwargs.devices is not None:
            setattr(RouterInfo, "requests", self._requests)
            for device in self._kwargs.devices:
                try:
                    inventory = self.inventory[device]
                    router = RouterInfo(inventory)
                    devices.append(router)
                except KeyError: 
                    print(f"notice: {device} not in self.inventory")      
 
        if self._kwargs.device_groups is not None:
            setattr(RouterInfo, "requests", self._requests)
            for device, info in self.inventory.items():
                try: 
                    for k,v in self._kwargs.device_groups.items(): 
                         if info[k] != v: raise 
                except:  continue
                else: 
                    inventory = self.inventory[device]
                    router = RouterInfo(inventory)
                    devices.append(router)
 
        if self._kwargs.host_configs is not None:
            host_specific_requests("host_configs", "config")
 
        if self._kwargs.host_rpcs is not None:
            host_specific_requests("host_rpcs", "rpcs")
 
        if self._kwargs.host_tests is not None:
            host_specific_requests("host_tests", "tests_file")
 
        if self._kwargs.host_rollbacks is not None:
            host_specific_requests("host_rollbacks", "rollback")
 
        # internal devices object
        self._devices = devices
 
        # presentable, public devices object
        self.devices = { device.inventory.hostname:\
                         self.inventory[device.inventory.hostname]
                         for device in self._devices } 

    def _execute(self):
        '''
        This performs the actual 'call' / execution of
        each device. It will use the multiprocessing
        module if 'silent' is specific.  If not, execution
        will be linear. Depending on the platform, a different
        subclassed object will be instantiated.
        '''
 
        # exit if no devices
        if not len(self._devices) > 0: 
            err = "no devices selected"
            raise RuntimeError(err)
 
        # multiprocessing queue
        self._queue = Queue()
 
        # update RouterInfo class attribute
        setattr(RouterInfo, "queue", self._queue)
 
        # instantiate the netconf objects
        routers = []
 
        for device in self._devices:
            
            if device.inventory.platform == "junos":
                router = JuniperAgent(device)
                routers.append(router) 
 
            elif ( device.inventory.platform == "iosxe" or
                   device.inventory.platform == "iosxr" ):
 
                router = CiscoAgent(device)
                routers.append(router) 
           
            else:
                err = ( "device platform '{device.platform}'"
                        "does not match any NetconfAgent objects" )
                raise RuntimeError(err)
 
        results = []
 
        if self._kwargs.silent:
            for router in routers:
                p = Process(target=router)
                p.start()
           
            tasks = len(routers)
            while tasks:
                try: results.append(self._queue.get())
                except self._queue.Empty: pass
                else: tasks -= 1
        else:
             for router in routers:
                 results.append(router())
        
        # create a summary object
        self.summary = {"summary": {}}
        
        for router in results:
            d = {router.hostname: {}}
            d[router.hostname].update({"fatal": 
                                          router.report['fatal'],
                                       "successful": 
                                          router.report['successful']})
 
            self.summary["summary"].update(d)
        
        # create a json summary report
        with open(path.join(self.output_dir, "summary.json"), "w") as f:
            f.write(dumps(self.summary, indent=4, sort_keys=True))  
 
        # create an archive of the entire log directory
        archive_name = self.output_dir.split("/")[-1:][0]
        make_archive(path.join(self._log_path, archive_name),
                     'zip', 
                     self.output_dir)
 
        self.results = results
 
        return results
