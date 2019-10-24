from .Common import *
from .Contract import Contract
from inspect import cleandoc

class ensure(Contract):
    def checkPostCondition(self):
        if self.condition.__code__.co_argcount == 3:
            return self.condition(self.args, self.result, self.preserved)
        return self.condition(self.args, self.result)

    def makePostConditionErrorString(self):
        string = f"""
                    Ensure failed at {self.getContractFileLocation()}
                    {self.args}
                    {self.preserved}
                    Result = {self.result}
                    {self.makeFormattedDescription()}
                """
        return cleandoc(string)

    def makeFormattedDescription(self):
        return super().makeFormattedDescription(args = self.args, old = self.preserved, result = self.result)

    def preserveArguments(self, preservers):
        x = preserveValues(preservers, self.args)
        return dictToNamedTuple(x, "Old")