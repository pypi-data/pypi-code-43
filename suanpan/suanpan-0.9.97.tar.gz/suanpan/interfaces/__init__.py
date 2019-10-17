# coding=utf-8
from __future__ import absolute_import, print_function

import argparse
import atexit
import base64
import functools
import itertools
import os
import re
import signal
import sys

from suanpan.arguments import Bool
from suanpan.log import logger
from suanpan.objects import Context, HasName


class HasArguments(object):
    ENVIRONMENT_ARGUMENTS_KEYWORD = "SP_PARAM"
    GLOBAL_ARGUMENTS = []
    ARGUMENTS = []

    @classmethod
    def dictFromList(cls, l):
        return dict(zip(l[0::2], l[1::2]))

    @classmethod
    def listFromDict(cls, d):
        return list(itertools.chain(*d.items()))

    @classmethod
    def getArgList(cls, *args, **kwargs):  # pylint: disable=unused-argument
        argDict = {}
        argDict.update(cls.dictFromList(cls.getArgListFromEnv()))
        argDict.update(cls.dictFromList(cls.getArgListFromCli()))
        argDict.update(cls.dictFromList(args))
        argDict.update({"--{}".format(k): v for k, v in kwargs.items()})
        return cls.listFromDict(argDict)

    @classmethod
    def getArgListFromCli(cls):
        return sys.argv[1:]

    @classmethod
    def getArgListFromEnv(cls):
        argStringBase64 = os.environ.get(cls.ENVIRONMENT_ARGUMENTS_KEYWORD, "")
        logger.debug(
            "{}(Base64)='{}'".format(cls.ENVIRONMENT_ARGUMENTS_KEYWORD, argStringBase64)
        )
        try:
            argString = base64.b64decode(argStringBase64).decode()
        except Exception:
            argString = argStringBase64  # temporary fix for SP_PARAM(Base64)
        logger.debug("{}='{}'".format(cls.ENVIRONMENT_ARGUMENTS_KEYWORD, argString))
        regex = r"(--[\w-]+)\s+(?:(?P<quote>[\"\'])(.*?)(?P=quote)|([^\'\"\s]+))"
        groups = re.findall(regex, argString, flags=re.S)
        argv = list(
            itertools.chain(*[(group[0], group[-2] or group[-1]) for group in groups])
        )
        return argv

    def loadFormatArguments(self, context, restArgs=None, **kwargs):
        arguments = self.getArguments(**kwargs)
        args, restArgs = self._parseArguments(arguments, restArgs=restArgs)
        self._loadArguments(args, arguments)
        self._formatArguments(context, arguments)
        return arguments, restArgs

    def loadCleanArguments(self, context, restArgs=None, **kwargs):
        arguments = self.getArguments(**kwargs)
        args, restArgs = self._parseArguments(arguments, restArgs=restArgs)
        self._loadArguments(args, arguments)
        self._cleanArguments(context, arguments)
        return arguments, restArgs

    def loadGlobalArguments(self, restArgs=None, **kwargs):
        arguments = self.getGlobalArguments(**kwargs)
        args, restArgs = self._parseGlobalArguments(arguments, restArgs=restArgs)
        self._loadArguments(args, arguments)
        self._formatArguments(Context(), arguments)
        return arguments, restArgs

    def loadComponentArguments(self, restArgs=None, **kwargs):
        arguments = self.getComponentArguments(**kwargs)
        args, restArgs = self._parseArguments(arguments, restArgs=restArgs)
        self._loadArguments(args, arguments)
        self._formatArguments(Context(), arguments)
        return arguments, restArgs

    def saveArguments(self, context, arguments, results):
        return {
            argument.key: argument.save(context, result)
            for argument, result in zip(arguments, results)
        }

    def getArguments(self, *args, **kwargs):
        raise NotImplementedError("Method not implemented!")

    def getGlobalArguments(self, *args, **kwargs):  # pylint: disable=unused-argument
        return self.GLOBAL_ARGUMENTS

    def getComponentArguments(self, *args, **kwargs):  # pylint: disable=unused-argument
        return self.ARGUMENTS

    @classmethod
    def _parseArguments(cls, arguments, restArgs=None, **kwargs):
        parser = argparse.ArgumentParser(allow_abbrev=False, **kwargs)
        for arg in arguments:
            arg.addParserArguments(parser)
        return parser.parse_known_args(restArgs)

    @classmethod
    def _parseGlobalArguments(cls, arguments, restArgs=None, **kwargs):
        parser = argparse.ArgumentParser(**kwargs)
        for arg in arguments:
            arg.addGlobalParserArguments(parser)
        return parser.parse_known_args(restArgs)

    @classmethod
    def _loadArguments(cls, args, arguments):
        return {arg.key: arg.load(args) for arg in arguments}

    @classmethod
    def _formatArguments(cls, context, arguments):
        return {arg.key: arg.format(context) for arg in arguments}

    @classmethod
    def _cleanArguments(cls, context, arguments):
        return {arg.key: arg.clean(context) for arg in arguments}

    @classmethod
    def defaultArgumentsFormat(cls, args, arguments):
        arguments = (arg.key.replace("-", "_") for arg in arguments)
        return {
            cls._defaultArgumentKeyFormat(arg): getattr(args, arg, None)
            for arg in arguments
        }

    @classmethod
    def _defaultArgumentKeyFormat(cls, key):
        return cls._toCamelCase(cls._removePrefix(key))

    @classmethod
    def _removePrefix(cls, string, delimiter="_", num=1):
        pieces = string.split(delimiter)
        pieces = pieces[num:] if len(pieces) > num else pieces
        return delimiter.join(pieces)

    @classmethod
    def _toCamelCase(cls, string, delimiter="_"):
        camelCaseUpper = lambda i, s: s[0].upper() + s[1:] if i and s else s
        return "".join(
            [camelCaseUpper(i, s) for i, s in enumerate(string.split(delimiter))]
        )

    @classmethod
    def argumentsDict(cls, arguments):
        result = {}
        for arg in arguments:
            keys = (arg.key, arg.alias)
            result.update({key: arg.value for key in keys if key})
        return result

    @classmethod
    def getArgumentValueFromDict(cls, data, arg):
        value = data.get(arg.alias)
        if value is not None:
            return value

        value = data.get(arg.key)
        if value is not None:
            return value

        return None

    @classmethod
    def hasArgumentValueFromDict(cls, data, arg):
        return arg.alias in data or arg.key in data


class HasLogger(HasName):
    def __init__(self):
        super(HasLogger, self).__init__()
        logger.setLogger(self.name)

    @property
    def logger(self):
        return logger


class HasDevMode(HasArguments):
    DEV_ARGUMENTS = [Bool(key="debug", default=False)]

    def getGlobalArguments(self, *args, **kwargs):
        arguments = super(HasDevMode, self).getGlobalArguments(*args, **kwargs)
        return arguments + self.DEV_ARGUMENTS


class HasInitHooks(object):
    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        super(HasInitHooks, self).__init__()
        self.beforeInitHooks = getattr(self, "beforeInitHooks", [])
        self.afterInitHooks = getattr(self, "afterInitHooks", [])

    def beforeInit(self, *args, **kwargs):
        pass

    def callBeforeInitHooks(self, *args, **kwargs):
        self.beforeInit(*args, **kwargs)
        for hook in self.beforeInitHooks:
            hook(*args, **kwargs)

    def addBeforeInitHooks(self, *hooks):
        self.beforeInitHooks.extend(hooks)
        return self

    def afterInit(self, *args, **kwargs):
        pass

    def callAfterInitHooks(self, *args, **kwargs):
        self.afterInit(*args, **kwargs)
        for hook in self.afterInitHooks:
            hook(*args, **kwargs)

    def addAfterInitHooks(self, *hooks):
        self.afterInitHooks.extend(hooks)
        return self


class HasSaveHooks(object):
    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        super(HasSaveHooks, self).__init__()
        self.beforeSaveHooks = getattr(self, "beforeSaveHooks", [])
        self.afterSaveHooks = getattr(self, "afterSaveHooks", [])

    def beforeSave(self, *args, **kwargs):
        pass

    def callBeforeSaveHooks(self, *args, **kwargs):
        self.beforeSave(*args, **kwargs)
        for hook in self.beforeSaveHooks:
            hook(*args, **kwargs)

    def addBeforeSaveHooks(self, *hooks):
        self.beforeSaveHooks.extend(hooks)
        return self

    def afterSave(self, *args, **kwargs):
        pass

    def callAfterSaveHooks(self, *args, **kwargs):
        self.afterSave(*args, **kwargs)
        for hook in self.afterSaveHooks:
            hook(*args, **kwargs)

    def addAfterSaveHooks(self, *hooks):
        self.afterSaveHooks.extend(hooks)
        return self


class HasCallHooks(object):
    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        super(HasCallHooks, self).__init__()
        self.beforeCallHooks = getattr(self, "beforeCallHooks", [])
        self.afterCallHooks = getattr(self, "afterCallHooks", [])

    def beforeCall(self, *args, **kwargs):
        pass

    def callBeforeCallHooks(self, *args, **kwargs):
        self.beforeCall(*args, **kwargs)
        for hook in self.beforeCallHooks:
            hook(*args, **kwargs)

    def addBeforeCallHooks(self, *hooks):
        self.beforeCallHooks.extend(hooks)
        return self

    def afterCall(self, *args, **kwargs):
        pass

    def callAfterCallHooks(self, *args, **kwargs):
        self.afterCall(*args, **kwargs)
        for hook in self.afterCallHooks:
            hook(*args, **kwargs)

    def addAfterCallHooks(self, *hooks):
        self.afterCallHooks.extend(hooks)
        return self


class HasTriggerHooks(object):
    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        super(HasTriggerHooks, self).__init__()
        self.beforeTriggerHooks = getattr(self, "beforeTriggerHooks", [])
        self.afterTriggerHooks = getattr(self, "afterTriggerHooks", [])

    def beforeTrigger(self, *args, **kwargs):
        pass

    def callBeforeTriggerHooks(self, *args, **kwargs):
        self.beforeTrigger(*args, **kwargs)
        for hook in self.beforeTriggerHooks:
            hook(*args, **kwargs)

    def addBeforeTriggerHooks(self, *hooks):
        self.beforeTriggerHooks.extend(hooks)
        return self

    def afterTrigger(self, *args, **kwargs):
        pass

    def callAfterTriggerHooks(self, *args, **kwargs):
        self.afterTrigger(*args, **kwargs)
        for hook in self.afterTriggerHooks:
            hook(*args, **kwargs)

    def addAfterTriggerHooks(self, *hooks):
        self.afterTriggerHooks.extend(hooks)
        return self


class HasExitHooks(object):
    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        super(HasExitHooks, self).__init__()
        self.beforeExitHooks = getattr(self, "beforeExitHooks", [])

    def beforeExit(self, *args, **kwargs):
        pass

    def callBeforeExitHooks(self, *args, **kwargs):
        self.beforeExit(*args, **kwargs)
        for hook in self.beforeExitHooks:
            hook(*args, **kwargs)

    def addBeforeExitHooks(self, *hooks):
        self.beforeExitHooks.extend(hooks)
        return self

    def registerBeforeExitHooks(self, *args, **kwargs):
        atexit.register(self.callBeforeExitHooks, *args, **kwargs)
        signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(1))
        return self
