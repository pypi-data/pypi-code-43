from .Common import *
from functools import wraps

PRESERVER_ATTRIBUTE = '__contract_preserved_values__'

class Contract:
    def __init__(self, condition, description = ""):
        self.callerFrame = getCallerData()
        self.condition = condition
        self.description = description
        self.func = None
        self.args = None
        self.preserved = None
        self.result = None

    def __call__(self, func):
        self.func = func
        @wraps(func)
        def inner(*args, **kwargs):
            self.args = self.getCompleteArguments(*args, **kwargs)

            self.preserved = self.preserveArguments(getattr(inner, PRESERVER_ATTRIBUTE, []))

            if not self.checkPreCondition():
                self.preConditionFailure()

            self.result = self.runFunction()

            if not self.checkPostCondition():
                self.postConditionFailure()

            return self.result

        return inner

    def getCompleteArguments(self, *args, **kwargs):
        completeArgs = makeCompleteArgumentDict(self.func, args, kwargs)
        completeArgs = dictToNamedTuple(completeArgs, "Args")
        return completeArgs

    def preserveArguments(self, preservers):
        return dictToNamedTuple({}, "Old")

    def checkPreCondition(self):
        return True

    def preConditionFailure(self):
        raise PreConditionError(self.makePreConditionErrorString())

    def makePreConditionErrorString(self):
        return "PreCondition Failure"

    def runFunction(self):
        return self.func(*self.args)

    def checkPostCondition(self):
        return True

    def postConditionFailure(self):
        raise PostConditionError(self.makePostConditionErrorString())

    def makePostConditionErrorString(self):
        return "PostCondition Failure"

    def getContractFileLocation(self):
        return makeFileLocationString(self.callerFrame.filename, self.callerFrame.lineno)

    #called _self so self can be passed in without conflict
    def makeFormattedDescription(_self, **kwargs):
        try:
            return _self.description.format(**kwargs)
        except Exception as e:
            return "Description formatting failed: " + str(e)

class PreConditionError(AssertionError):
    pass

class PostConditionError(AssertionError):
    pass