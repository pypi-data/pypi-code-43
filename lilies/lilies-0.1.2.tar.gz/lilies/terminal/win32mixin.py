from colorama import init
from colorama.initialise import deinit, reinit


class Win32Mixin(object):
    def setup(self, appstate):
        if appstate.get("colorama_init"):
            reinit()
            return
        init()
        appstate["colorama_init"] = True

    def teardown(self, appstate):
        deinit()
