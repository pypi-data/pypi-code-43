'''
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
'''

import importlib.util

# Simple class to hold lists of callbacks associated with a key.


class HookSet:
    # Helper class to provide controlled access to the HookSet to the loading module.
    class Registrar:
        def __init__(self, hook_set):
            self.hooks = hook_set

        def register(self, hook, cb):
            self.hooks.register(hook, cb)

    def __init__(self):
        self.hooks = {}
        self.modules = []
        self.registrar = HookSet.Registrar(self)
        # Define all the valid hooks here.
        for item in ['ReadRequestHook']:
            if isinstance(item, list):
                hook = item[0]
                label = item[1]
            else:
                hook = label = item
            exec("HookSet.{} = '{}'".format(label, hook))
            exec("HookSet.Registrar.{} = '{}'".format(label, hook))
            self.hooks[hook] = []

    def load(self, source):
        try:
            spec = importlib.util.spec_from_file_location('Observer', source)
            mod = importlib.util.module_from_spec(spec)
            mod.Hooks = self.registrar
            spec.loader.exec_module(mod)
        except ImportError:
            print("Failed to import {}".format(source))
        else:
            self.modules.append(mod)

    # Add a callback cb to the hook.
    # Error if the hook isn't defined.
    def register(self, hook, cb):
        if hook in self.hooks:
            self.hooks[hook].append(cb)
        else:
            raise ValueError("{} is not a valid hook name".format(hook))

    # Invoke a hook. Pass on any additional arguments to the callback.
    def invoke(self, hook, *args, **kwargs):
        cb_list = self.hooks[hook]
        if cb_list is None:
            raise ValueError(
                "{} is not a valid hook name to invoke".format(hook))
        else:
            for cb in cb_list:
                cb(*args, **kwargs)
