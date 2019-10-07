# -*- coding: utf-8 -*-

from lbdrabbit import App, AppConfig, Constant, Derivable


class MyAppConfig(AppConfig):
    pass


app = App("example_app", app_config=MyAppConfig())
