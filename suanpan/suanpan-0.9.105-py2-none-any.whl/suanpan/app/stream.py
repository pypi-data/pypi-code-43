# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.app.base import BaseApp
from suanpan.model.arguments import HotReloadModel
from suanpan.stream import Handler, Stream
from suanpan.utils import functional


class TriggerApp(BaseApp):
    def __init__(self, streamApp, *args, **kwargs):
        super(TriggerApp, self).__init__(*args, **kwargs)
        self.streamApp = streamApp
        self.handler = None
        self.interval = None
        self.loop = None

    def __call__(self, interval=None, loop=None):
        self.interval = interval
        self.loop = self._initLoop(loop)

        def _dec(funcOrApp):
            funcOrApp = (
                self.handler
                if isinstance(funcOrApp, TriggerApp)
                else functional.instancemethod(funcOrApp)
            )
            self.handler = Handler.use(funcOrApp)
            return self

        return _dec

    def _initLoop(self, loop):
        if loop is None:
            return None
        if callable(loop):
            return functional.instancemethod(loop)
        return lambda obj: loop

    def input(self, argument):
        if self.streamApp.isComponentArgument(argument):
            return self.componentParam(argument)

        def _dec(funcOrApp):
            funcOrApp = (
                self.handler
                if isinstance(funcOrApp, TriggerApp)
                else functional.instancemethod(funcOrApp)
            )
            self.handler = Handler.input(argument)(funcOrApp)
            return self

        return _dec

    def output(self, argument):
        if isinstance(argument, HotReloadModel):
            raise Exception("{} can't be set as output!".format(argument.name))

        def _dec(funcOrApp):
            funcOrApp = (
                self.handler
                if isinstance(funcOrApp, TriggerApp)
                else functional.instancemethod(funcOrApp)
            )
            self.handler = Handler.output(argument)(funcOrApp)
            return self

        return _dec

    def param(self, argument):
        if self.streamApp.isComponentArgument(argument):
            return self.componentParam(argument)

        self.streamApp.globalArguments.append(argument)

        def _dec(funcOrApp):
            funcOrApp = (
                self.handler
                if isinstance(funcOrApp, TriggerApp)
                else functional.instancemethod(funcOrApp)
            )
            self.handler = Handler.use(funcOrApp)
            return self

        return _dec

    def column(self, argument):
        if self.streamApp.isComponentArgument(argument):
            return self.componentParam(argument)

        self.streamApp.globalArguments.append(argument)

        def _dec(funcOrApp):
            funcOrApp = (
                self.handler
                if isinstance(funcOrApp, TriggerApp)
                else functional.instancemethod(funcOrApp)
            )
            self.handler = Handler.use(funcOrApp)
            return self

        return _dec

    def componentParam(self, argument):
        self.streamApp.arguments.append(argument)

        def _dec(funcOrApp):
            funcOrApp = (
                self.handler
                if isinstance(funcOrApp, TriggerApp)
                else functional.instancemethod(funcOrApp)
            )
            self.handler = Handler.use(funcOrApp)
            return self

        return _dec

    def send(self, *args, **kwargs):
        self.streamApp.stream.send(*args, **kwargs)


class StreamApp(BaseApp):
    COMPONENT_ARGUMENT_CLASSES = (HotReloadModel,)

    def __init__(self, *args, **kwargs):
        super(StreamApp, self).__init__(*args, **kwargs)
        self.triggerApp = TriggerApp(self)
        self.stream = None
        self.handler = None
        self.arguments = []
        self.globalArguments = []

    def __call__(self, *args, **kwargs):
        attrs = {
            "GLOBAL_ARGUMENTS": self.globalArguments,
            "ARGUMENTS": self.arguments,
            "INTERVAL": self.trigger.interval,
            "loop": self.trigger.loop,
            "call": self.handler,
            "trigger": self.trigger.handler,
            "beforeInitHooks": self.beforeInitHooks + self.trigger.beforeInitHooks,
            "afterInitHooks": self.afterInitHooks + self.trigger.afterInitHooks,
            "beforeExitHooks": self.beforeExitHooks + self.trigger.beforeExitHooks,
            "beforeCallHooks": self.beforeCallHooks,
            "afterCallHooks": self.afterCallHooks,
            "beforeTriggerHooks": self.trigger.beforeCallHooks,
            "afterTriggerHooks": self.trigger.afterCallHooks,
        }
        attrs = {k: v for k, v in attrs.items() if v is not None}
        ADSteam = type("ADSteam", (Stream,), attrs)
        self.stream = ADSteam(*args, **kwargs)
        return self

    @property
    def trigger(self):
        return self.triggerApp

    def start(self, *args, **kwargs):
        if not self.stream:
            raise Exception("{} is not ready".format(self.name))
        self.stream.start(*args, **kwargs)
        return self

    def input(self, argument):
        if self.isComponentArgument(argument):
            return self.componentParam(argument)

        def _dec(funcOrApp):
            funcOrApp = (
                self.handler
                if isinstance(funcOrApp, StreamApp)
                else functional.instancemethod(funcOrApp)
            )
            self.handler = Handler.input(argument)(funcOrApp)
            return self

        return _dec

    def output(self, argument):
        if isinstance(argument, HotReloadModel):
            raise Exception("{} can't be set as output!".format(argument.name))

        def _dec(funcOrApp):
            funcOrApp = (
                self.handler
                if isinstance(funcOrApp, StreamApp)
                else functional.instancemethod(funcOrApp)
            )
            self.handler = Handler.output(argument)(funcOrApp)
            return self

        return _dec

    def param(self, argument):
        if self.isComponentArgument(argument):
            return self.componentParam(argument)

        self.globalArguments.append(argument)

        def _dec(funcOrApp):
            funcOrApp = (
                self.handler
                if isinstance(funcOrApp, StreamApp)
                else functional.instancemethod(funcOrApp)
            )
            self.handler = Handler.use(funcOrApp)
            return self

        return _dec

    def column(self, argument):
        if self.isComponentArgument(argument):
            return self.componentParam(argument)

        self.globalArguments.append(argument)

        def _dec(funcOrApp):
            funcOrApp = (
                self.handler
                if isinstance(funcOrApp, StreamApp)
                else functional.instancemethod(funcOrApp)
            )
            self.handler = Handler.use(funcOrApp)
            return self

        return _dec

    def componentParam(self, argument):
        self.arguments.append(argument)

        def _dec(funcOrApp):
            funcOrApp = (
                self.handler
                if isinstance(funcOrApp, StreamApp)
                else functional.instancemethod(funcOrApp)
            )
            self.handler = Handler.use(funcOrApp)
            return self

        return _dec

    def isComponentArgument(self, argument):
        return isinstance(argument, self.COMPONENT_ARGUMENT_CLASSES)

    def send(self, *args, **kwargs):
        self.stream.send(*args, **kwargs)
