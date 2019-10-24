from .Common import *
from .Contract import Contract
from inspect import cleandoc

def getArgumentTypeMismatch(args, requirments):
    mismatches = {}
    for (k, v) in requirments.items():
        if k == 'RESULT':
            pass
        elif type(args.__getattribute__(k)) != v:
            mismatches[k] = (args.__getattribute__(k), v)
    return mismatches

class types(Contract):
    def __init__(self, **requirements):
        super().__init__(None)
        self.callerFrame = getCallerData()
        self.requirements = requirements
        self.mismatches = None

    def checkPreCondition(self):
        self.mismatches = getArgumentTypeMismatch(self.args, self.requirements)
        return len(self.mismatches) == 0

    def checkPostCondition(self):
        if 'RESULT' in self.requirements:
            return type(self.result) == self.requirements['RESULT']
        return True

    def makePreConditionErrorString(self):
        string = f"""
            Type check failed at {self.getContractFileLocation()}
            {self.args}
            {self.makeMismatchErrorString()}
            {self.makeFormattedDescription(args = self.args)}
        """
        return cleandoc(string)

    def makePostConditionErrorString(self):
        string = f"""
            Type check failed at {self.getContractFileLocation()}
            {self.args}
            {self.preserved}
            Result = {self.result}, type {type(self.result)}.  Expected type {self.requirements['RESULT']}
            {self.makeFormattedDescription(args = self.args, old = self.preserved, result = self.result)}
        """
        return cleandoc(string)

    def makeMismatchErrorString(self):
        return '\n'.join(f"{k} = {v}, which is type {type(v)}, expected type {t}"
                         for k, (v, t) in self.mismatches.items())