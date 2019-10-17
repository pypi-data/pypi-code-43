import json
import sys

from testwizard.commands_core.ResultBase import ResultBase

class WaitForColorResult(ResultBase):
    def __init__(self, json1, successMessage, failMessage):
        jsonObj = json.loads(json1)
        ResultBase.__init__(self, True if jsonObj["time"] >= 0 and jsonObj["errorCode"] == 0 else False, successMessage, failMessage)

        self.time = jsonObj["time"]
        self.similarity = jsonObj["similarity"]
        if("color" in jsonObj):
            color = jsonObj["color"]
            self.color = Color(color["r"], color["g"], color["b"])

        if(self.success):
            return

        if("errorCode" in jsonObj):
            self.message = self.getMessageForErrorCode(self.message, jsonObj["errorCode"])

class Color(object):
    def __init__(self, r, g, b):
       self.r = int(r)
       self.g = int(g)
       self.b = int(b)