#! /usr/bin/env python

import pdb
import types
from os import path
from time import sleep
from json import dumps
from xmltodict import parse
from yaml import warnings
from ncclient import manager 
from jnpr.jsnapy import SnapAdmin

warnings({'YAMLLoadWarning': False})

def log_decorator(func):
    '''
    This decorator ensures the 'results' class instance
    is updated for each method call.
    '''

    def log(*args, title=False, chr="*"):
        Logger, msg = args[0], args[1]
        results = Logger.router.results
 
        if title:
            chrs = chr * (100 - len(args[1]))
            msg = f"\n[{msg}] {chrs}" 
  
        if "fatal" in msg: results.report["fatal"] += 1
        elif "success" in msg: results.report["successful"] += 1
        else: pass
            
        Logger.file.write(msg + "\n")
        results.log += f"{msg}\n"
        func(Logger, msg)
 
    return log

class Logger:
    '''
    The standard 'logging' library was not used
    because it interred with the Jsnapy library.
    No work around could be found.
    '''

    def __init__(self, router):
        self.router = router
 
        if router.requests.silent:
            self.debug = self.stdout_off
        else:
            self.debug = self.stdout_on

    def close(self): 
        self.file.close()

    def open(self):
        fn = f"{self.router.inventory.hostname}.log"
        self.file = open(path.join(self.router.output_dir, fn), "w") 

    @log_decorator
    def stdout_on(self, message):
        print(message)

    @log_decorator
    def stdout_off(self, message):
        return None

class Results:
    '''
    This is the object that will be returned to
    the caller. There are predefined attributes
    e.g. 'log', 'report', etc. at instantiation
    and attributes can be added after execution 
    e.g. 'self.diff', 'self.rpcs', etc.
    '''

    def __init__(self, output_dir, hostname):
        self.hostname = hostname
        self.log = ""
        self.report = {"fatal": 0, "successful": 0}
        self.healthy = {'pre': 'unknown', 'pst': 'unknown'}
        self.changed = False

    def __str__(self):
        results = ""
 
        for item in dir(self):
            if not item.startswith("__") and not item.startswith("_"):
                if isinstance(getattr(self, item), types.MethodType):
                    results += f" object.{item}()\n"
                else:
                    results += f" object.{item}\n"
 
        return results

    def __bool__(self): 
        if ( self.report["fatal"] == 0 and 
             self.report["successful"] >= 1 ):
               
            return True

        else: 
            return False

class NetconfAgent:

    def __init__(self, device_info):
        self.queue = device_info.queue
        self.inventory = device_info.inventory
        self.requests = device_info.requests
        self.output_dir = device_info.output_dir
        self.hostname = self.inventory.hostname

    def __call__(self):
        self.results = Results(self.output_dir, 
                               self.hostname)
        self.file_prefix = path.join(self.output_dir, 
                                     self.hostname)
        self.logger = Logger(self)
        self.instance = "pre"
        self.awaiting = False

        def return_results():
            if self.requests.silent: self.queue.put(self.results)
            else: return self.results
  
        try: self.nc_connect()
        except RuntimeError: return return_results() 
  
        if self.requests.capabilities:
            self.nc_capabilities()
            
        if self.requests.schemas:
            self.nc_schemas()
            
        if self.requests.rpcs:
            self.nc_get()
            
        if ( self.requests.jsnapy and 
             not self.requests.skip_check ):
 
            self.nc_snapshot()
        
        if ( self.requests.config or 
             self.requests.rollback or
             self.requests.diff ):
 
            self.nc_edit()
            
        if ( self.results.changed and 
             self.requests.jsnapy ):
 
            self.nc_snapshot()
            
        if ( self.results.changed and 
             self.requests.rpcs ):
 
            self.nc_get()
            
        if ( self.results.changed and 
             self.requests.confirm ):
 
            self.nc_edit()
           
        self.nc_disconnect()
 
        return return_results()

    def nc_connect(self):
        self.logger.open()
        self.logger.debug(f"start {self.hostname}", title=True, chr="#")
        self.logger.debug(f"connect to host", title=True)
        
        try:
            self.connection = manager.connect(
                host = self.inventory.hostname, 
                username = self.inventory.username, 
                password = self.inventory.password,
                device_params = {"name": self.inventory.platform},
                port = "830",
                timeout = 5,
                hostkey_verify = False)
        
        except Exception as e:
            self.logger.debug(f"fatal: connecting via netconf -> {e}")
            raise RuntimeError
        else:
            self.logger.debug(f"success: connecting via netconf")

    def nc_disconnect(self):
        self.logger.debug("disconnect from host", title=True)
        
        try:
            self.connection.close_session()
        except Exception as e:
            self.logger.debug(f"fatal: disconnecting netconf -> {e}")
        else:
            self.logger.debug(f"success: disconnecting netconf")
            self.logger.debug(f"finish {self.hostname}", title=True, chr="#")
        finally:
            self.logger.close()

    def nc_capabilities(self):
        self.logger.debug("netconf capabilities", title=True)
 
        # collect
        try:
            capabilities = self.connection.server_capabilities._dict
        except Exception as e:
            return self.logger.debug(f"fatal: collecting capabilities -> {e}")
        else:
            self.logger.debug(f"success: collecting capabilities")
       
        self.results.capabilities = capabilities
 
        # save
        try:
            fn = f"{self.file_prefix}_capabilities.txt"
            with open(fn, "w") as f:
                for capability in capabilities:
                    f.write(f"{capability}\n")
        except Exception as e:
            return self.logger.debug(f"fatal: saving capabilities -> {e}")
        else:
            self.logger.debug(f"success: saving capabilities")

    def nc_schemas(self):            
        self.logger.debug("netconf schemas", title=True)
        
        # collect
        schemas = {}
    
        for item in self.requests.schemas:
            try:
                schemas[item] = self.connection.get_schema(item).data
            except Exception as e:
                self.logger.debug(f"fatal: collecting schema {item} -> {e}")
            else: 
                self.logger.debug(f"success: collecting schema {item}")
    
        self.results.schemas = schemas
              
        # save
        try:
            for desc, data in schemas.items():
                fn = f"{self.file_prefix}_schemas_{desc}.yang"
                with open(fn, "w") as f:
                    f.write(f"{data}")
        except Exception as e:
            self.logger.debug(f"fatal: saving schemas -> {e}")
        else:
            self.logger.debug(f"success: saving schemas")
        
        self.results.schemas = {}
        self.results.schemas.update(schemas)

    def nc_get(self):  
        self.logger.debug("netconf get", title=True)    
   
        self.results.rpcs = {self.instance: {}}           

        def try_rpc(*args):
            '''
            Requires a method ('rpc') to call on the ncclient 
            object and any args ('desc') to pass to the method.
            '''
 
            rpc = args[0] 
            desc = args[1]
 
            if self.requests.xml: ext = "xml"
            else: ext = "json"
 
            # collect
            try:
                result = rpc(*args[2:])
            except Exception as e:
                self.logger.debug(f"fatal: collecting rpc {desc} -> {e}")
                raise RuntimeError
            else:
                self.logger.debug(f"success: collecting rpc {desc}")
               
            # parse               
            if hasattr(result, "xml"):
                if self.requests.xml: result = result.xml
                else: result = parse(result.xml)
            elif hasattr(result, "data_xml"):
                if self.requests.xml: result = result.data_xml
                else:
                    result = parse(result.data_xml)["rpc-reply"]
                    if "configuration-information" in result:
                        result = result["configuration-information"]\
                                       ["configuration-output"]
                        ext = "txt"
            else:
                raise RuntimeError
                self.logger.debug(f"fatal: get attribute unknown")  
            
            if self.requests.xml: 
                result = result.lstrip(r'"').rstrip(r'"')
 
            self.results.rpcs[self.instance].update({desc: result})
            
            
            # save
            fn = f"{self.file_prefix}_rpcs_{self.instance}_{desc}.{ext}"
 
            try:
                with open(fn, "w") as f:
                    if ext == "txt":
                        for line in result: f.write(line)
                    elif ext == "xml":
                        f.write(result)
                    elif ext == "json":
                        f.write(dumps(result, indent=4, sort_keys=True))      
                    else:
                        print(f"fatal: unknown extention saving rpc {desc}")
            except Exception as e:
                self.logger.debug(f"fatal: saving rpc {desc} -> {e}")     
            else:
                self.logger.debug(f"success: saving rpc {desc}")     
           
        # rpc   
        for desc, item in self.requests.rpcs.items():
            try:
                if item["type"] == "get":
                    rpc = self.connection.get
                    try_rpc(rpc, desc, item["data"])
                elif item["type"] == "get_config":
                    rpc = self.connection.get_config
                    try_rpc(rpc, desc, "running")
                elif item["type"] == "rpc":
                    rpc = self.connection.rpc
                    try_rpc(rpc, desc, item["data"])
                elif item["type"] == "command":
                    rpc = self.connection.command
                    try_rpc(rpc, desc, item["data"])
                else:
                    self.logger.debug((f"success: rpc type '{desc}' "
                                       f"is unknown"))
            except RuntimeError:
                pass

class CiscoAgent(NetconfAgent):

    def nc_edit(self):
        self.logger.debug("netconf edit", title=True)  

        def prepare():
            try:
                self.connection.discard_changes()
                self.connection.lock("candidate")
            except Exception as e:
                self.logger.debug((f"fatal: discarding and locking candidate "
                                   f"database -> {e}"))
                raise RuntimeError
            else:
                self.logger.debug((f"success: discarding and locking "
                                   f"candidate database"))

        def edit():
            try:
                self.loaded = self.connection.edit_config\
                                      (target="candidate", 
                                       config=self.requests.config, 
                                       format="xml")
            except Exception as e:
                self.logger.debug(f"fatal: editing configuration -> {e}")
                raise RuntimeError
            else:
                if "<ok/>" in self.loaded.xml:
                    self.logger.debug(f"success: editing configuration")  

        def validate():
            try:
                self.validate = self.connection.validate()
            except Exception as e:
                self.logger.debug((f"fatal: validating configuration "
                                   f"-> {e}"))
                raise RuntimeError
            else:
                if "<ok/>" in self.validate.xml:
                    self.logger.debug(f"success: validating configuration")
                else:
                    return self.logger.debug(("fatal: validating configuration"
                                              "-> self.validate.xml"))

        def commit():
            try: 
                kwargs = {}
                self.connection.commit(**kwargs)
            except Exception as e:
                self.connection.discard_changes()
                self.logger.debug(f"fatal: committing configuration -> {e}")
                raise RuntimeError
            else:
                self.results.changed = True
                self.instance = "pst"
                self.logger.debug(f"success: committing configuration")    
 
        # execution
        try: prepare(), edit(), validate(), commit()
        except RuntimeError: return

class JuniperAgent(NetconfAgent):

    def nc_snapshot(self):
        self.logger.debug("jsnapy", title=True)  
        
        # sleep
        if self.results.changed and self.awaiting :
            sleep_timer = int(self.requests.confirm) / 2 
            msg = ("\nnotice: sleeping for half the commit time\n"
                  f"  commit time: {self.requests.confirm}s\n"
                  f"  sleep time: {sleep_timer}s\n")
            self.logger.debug(msg)
            sleep(sleep_timer)
 
        # input                 
        js_input = f"""
                    hosts:
                      - device: {self.inventory.hostname}
                        username: {self.inventory.username}
                        passwd: {self.inventory.password}
                    tests:
                      - {self.requests.tests_file}
                    """
 
        js = SnapAdmin()
        js.set_verbosity(50) # disables output, bypasses bug
 
        # jsnapy compare
        if self.requests.jsnapy == "compare":
            # snap
            js_results = js.snap(js_input, 
                                 self.instance, 
                                 folder=self.output_dir)[0]
 
            # print
            for test in js_results.test_included:
                self.logger.debug(f"test: {test:<20} captured: True")
 
            # check
            if self.results.changed:
                js_results = js.check(js_input, 
                                      "pre", 
                                      "pst", 
                                      folder=self.output_dir)[0]
                
                # store
                self.health_tests = {}
                self.health_tests["results"] = js_results.result
                self.health_tests["verbose"] = js_results.test_results 
 
        # jsnapy check
        if self.requests.jsnapy == "check":
            # snap
            js_results = js.snapcheck(js_input, 
                                      file_name=self.instance, 
                                      folder=self.output_dir)[0]
 
            # print
            for test, result in js_results.result_dict.items():
                self.logger.debug(f"test: {test:<20} passed: {result}")
                
            # store
            self.health_tests = {}
            self.health_tests["results"] = js_results.result
            self.health_tests["verbose"] = js_results.test_results 
            
        # comparison
        if self.requests.jsnapy == "compare" and self.instance == "pre":
            pass
        else:
            if self.health_tests["results"] == "Passed":
                self.results.healthy[self.instance] = True
                self.logger.debug(f"\nsuccess: node is healthy")
            else:
                self.results.healthy[self.instance] = False
                self.logger.debug(f"\nfatal: node unhealthy")
 
            try:
                fn = f"{self.file_prefix}_jsnapy_results.json"
                with open(fn, "w") as f: 
                    f.write(dumps(self.health_tests["verbose"], 
                                  indent=4, 
                                  sort_keys=True))
            except Exception as e:
                return self.logger.debug(f"fatal: saving jsnapy -> {e}")
            else:
                self.logger.debug(f"success: saving jsnapy")

    def nc_edit(self):
        self.logger.debug("netconf edit", title=True)  

        def prepare():
            try:
                self.connection.discard_changes()
                self.connection.lock("candidate")
            except Exception as e:
                self.logger.debug((f"fatal: discarding and locking "
                                   f"candidate database -> {e}"))
                raise RuntimeError
            else:
                self.logger.debug((f"success: discarding and locking "
                                   f"candidate database"))

        def edit():            
            try:
                if self.requests.rollback:
                    self.loaded = self.connection.rollback\
                                  (rollback=self.requests.rollback) 
                else:
                    self.loaded = self.connection.load_configuration\
                                                  (action='set', 
                                                   config=self.requests.config)
            except Exception as e:
                self.logger.debug(f"fatal: loading configuration -> {e}")
                raise RuntimeError
            else:
                if "<ok/>" in self.loaded.data_xml:
                    self.logger.debug(f"success: loading configuration")
                else:
                    self.logger.debug((f"fatal: loading configuration -> "
                                       f"{self.loaded.data_xml}"))

        def validate():
            try:
                self.validate = self.connection.validate()
            except Exception as e:
                self.logger.debug(f"fatal: validating configuration -> {e}")
                raise RuntimeError
            else:
                if "<ok/>" in self.validate.data_xml:
                    self.logger.debug(f"success: validating configuration")
                else:
                    return self.logger.debug((f"fatal: validating configuration "
                                              f"-> self.validate.data_xml"))

        def diff():
            # diff 
            try:
                result = self.connection.compare_configuration()
            except Exception as e:
                self.logger.debug(f"fatal: comparing configuration -> {e}")
                raise RuntimeError
            else:   
                self.logger.debug(f"success: comparing configuration")
              
            if hasattr(result, "xml"):
                diff = parse(result.xml)["rpc-reply"]\
                                        ["configuration-information"]\
                                        ["configuration-output"]
            elif hasattr(result, "data_xml"):
                diff = parse(result.data_xml)["rpc-reply"]\
                                             ["configuration-information"]\
                                             ["configuration-output"]
            else:
                self.logger.debug((f"fatal: diff attribute unknown -> "
                                   f"{result.__name__}"))
                raise RuntimeError
 
            if not diff:      
                self.logger.debug(f"differences:")
                self.logger.debug(f"\n{diff}\n")
                raise RuntimeError
            else:
                self.results.diff = diff
          
            # diff - save and display          
            try:
                fn = f"{self.file_prefix}_diff.txt" 
                with open(fn, "w") as f:
                    f.write(diff) 
            except Exception as e:
                self.logger.debug(f"fatal: saving diff -> {e}")
                raise RuntimeError
            else:
                self.logger.debug(f"success: saving diff")
                self.logger.debug(f"differences:")
                self.logger.debug(f"\n{diff}\n")

        def commit_confirm():
            try:
                kwargs = { "confirmed": True, 
                           "timeout": self.requests.confirm, 
                           "comment": self.requests.comment }
                self.connection.commit(**kwargs)
            except Exception as e:
                self.connection.discard_changes()
                self.logger.debug(f"fatal: committing configuration -> {e}")
                raise RuntimeError
            else:
                self.results.changed = True
                self.awaiting = True
                self.instance = "pst"
                self.logger.debug((f"success: committing configuration "
                                   f"(confirmation required)"))

        def commit():
            try:
                # if confirming
                if self.instance == "pst":
                    comment = self.requests.comment + "_CONFIRMATION"
                else: comment = self.requests.comment
                kwargs = { "comment": comment }
                self.connection.commit(**kwargs)
            except Exception as e:
                self.connection.discard_changes()
                self.logger.debug(f"fatal: committing configuration -> {e}")
                raise RuntimeError
            else:
                if self.awaiting:
                    self.logger.debug(f"success: confirming the configuration")
                else:
                    self.results.changed = True
                    self.instance = "pst"
                    self.logger.debug(f"success: committing configuration")

        def commit_changes():
            # health check
            if self.results.healthy["pre"] is not False:
                pass
            else:
                self.connection.discard_changes()
                self.logger.debug((f"fatal: node not healthy "
                                   f"(commit not allowed)"))
                raise RuntimeError

            # prompt
            if self.requests.commit:
                pass
            elif self.requests.diff:
                self.connection.discard_changes()
                self.logger.debug(f"notice: diff performed")
                raise RuntimeError
            else:
                user_input = input("Commit (y / n):")
                if user_input == "y":
                    if self.requests.comment:
                        self.logger.debug((f"\nnotice: comment="
                                           f"{self.requests.comment}"))
                    else:
                        self.requests.comment = input("Enter a comment:")
                else:
                    self.logger.debug(f"\nnotice: '{user_input}' received")
                    raise RuntimeError
                
            # commit
            if self.requests.confirm: commit_confirm()
            else: commit()
        
        # confirmation
        if self.awaiting and self.results.healthy["pst"] is True:
            return commit()
        elif self.awaiting and self.results.healthy["pst"] is not True:
            return self.logger.debug((f"notice: node is unhealthy. "
                                      f"commit not confirmed"))
        else:
            pass    
        
        # execution
        try: prepare(), edit(), validate(), diff(), commit_changes()
        except RuntimeError: return
