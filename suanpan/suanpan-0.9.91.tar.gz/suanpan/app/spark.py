# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.app.base import BaseApp
from suanpan.spark import SparkComponent as Handler


class SparkApp(BaseApp):
    def __init__(self, *args, **kwargs):
        super(SparkApp, self).__init__(*args, **kwargs)
        self.handler = None

    def __call__(self, *args, **kwargs):
        if not self.handler:
            raise Exception("{} is not ready".format(self.name))
        self.handler(*args, **kwargs)  # pylint: disable=not-callable
        self.handler.beforeInitHooks.extend(self.beforeInitHooks)
        self.handler.afterInitHooks.extend(self.afterInitHooks)
        self.handler.beforeCallHooks.extend(self.beforeCallHooks)
        self.handler.afterSaveHooks.extend(self.afterCallHooks)
        self.handler.beforeExitHooks.extend(self.beforeExitHooks)
        return self

    def start(self, *args, **kwargs):
        if not self.handler:
            raise Exception("{} is not ready".format(self.name))
        self.handler.start(*args, **kwargs)
        return self

    def input(self, argument):
        def _dec(funcOrApp):
            funcOrApp = self.handler if isinstance(funcOrApp, SparkApp) else funcOrApp
            self.handler = Handler.input(argument)(funcOrApp)
            return self

        return _dec

    def output(self, argument):
        def _dec(funcOrApp):
            funcOrApp = self.handler if isinstance(funcOrApp, SparkApp) else funcOrApp
            self.handler = Handler.output(argument)(funcOrApp)
            return self

        return _dec

    def param(self, argument):
        def _dec(funcOrApp):
            funcOrApp = self.handler if isinstance(funcOrApp, SparkApp) else funcOrApp
            self.handler = Handler.param(argument)(funcOrApp)
            return self

        return _dec

    def column(self, argument):
        def _dec(funcOrApp):
            funcOrApp = self.handler if isinstance(funcOrApp, SparkApp) else funcOrApp
            self.handler = Handler.column(argument)(funcOrApp)
            return self

        return _dec
