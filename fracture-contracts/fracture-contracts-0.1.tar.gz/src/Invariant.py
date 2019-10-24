from .Common import *
from .Contract import Contract
from inspect import cleandoc, getsourcelines, ismethod, isfunction

#Taken from dpcontracts
def shouldApplyInvariant(name, func, cls):
    exceptions = ("__getitem__", "__setitem__", "__lt__", "__le__", "__eq__",
                  "__ne__", "__gt__", "__ge__", "__init__")

    if name.startswith("__") and name.endswith("__") and name not in exceptions:
        return False

    if not ismethod(func) and not isfunction(func):
        return False

    if getattr(func, "__self__", None) is cls:
        return False

    return True


def getMethodActualFirstLine(func):
    sourceLines = getsourcelines(func)
    line = sourceLines[1]
    sourceLines = sourceLines[0]
    while not sourceLines[0].strip().startswith('def'):
        sourceLines = sourceLines[1:]
        line += 1
    return line


class InvariantCheck(Contract):
    def __init__(self, condition, description, callerFrame):
        super().__init__(condition, description)
        self.callerFrame = callerFrame

    def checkPreCondition(self):
        if self.func.__name__ != '__init__':
            return self.condition(self.args[0])
        return True

    def checkPostCondition(self):
        return self.condition(self.args[0])

    def makePreConditionErrorString(self):
        string = f"""
            PreCheck Invariant failed at {self.getContractFileLocation()}
            During method at {self.getMethodFileLocation()}
            {self.args}
            {self.makeFormattedDescription(self = self.args[0], old = None, result = None)}
        """
        return cleandoc(string)

    def makePostConditionErrorString(self):
        string = f"""
            PreCheck Invariant failed at {self.getContractFileLocation()}
            During method at {self.getMethodFileLocation()}
            {self.args}
            {self.preserved}
            Result = {self.result}
            {self.makeFormattedDescription(self = self.args[0], old = self.preserved, result = self.result)}
        """
        return cleandoc(string)

    def getMethodFileLocation(self):
        methodLine = getMethodActualFirstLine(self.func)
        return makeFileLocationString(self.callerFrame.filename, methodLine)

    def preserveArguments(self, preservers):
        x = preserveValues(preservers, self.args)
        return dictToNamedTuple(x, "Old")

class invariant(Contract):
    def __call__(self, cls):
        class InvariantContractor(cls):
            def __repr__(self):
                return repr(cls)

        for name, value in [(name, getattr(cls, name)) for name in dir(cls)]:
            if shouldApplyInvariant(name, value, cls):
                setattr(InvariantContractor, name,
                        InvariantCheck(self.condition, self.description, self.callerFrame)(value))

        return InvariantContractor