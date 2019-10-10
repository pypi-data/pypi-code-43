#!/usr/bin/python3

from enum import Enum
import numpy as np


class AttributeType(Enum):
    String    = 0
    Integer32 = 1
    Integer64 = 2
    Float     = 3
    Double    = 4
    Boolean   = 5


def GetTypesList():
    return list(map(GetTypeNameString, AttributeType))


def GetTypeNameString(attType):
    if attType == AttributeType.String:
        return "String"
    elif attType == AttributeType.Integer32:
        return "Integer32"
    elif attType == AttributeType.Integer64:
        return "Integer64"
    elif attType == AttributeType.Float:
        return "Float32"
    elif attType == AttributeType.Double:
        return "Float64"
    elif attType == AttributeType.Boolean:
        return "Boolean"
    else:
        return "Unknown"


def GetTypeDefaultValue_strType(attTypeStr):
    if attTypeStr == GetTypeNameString(AttributeType.String):
        return ""
    elif attTypeStr == GetTypeNameString(AttributeType.Integer32):
        return "0"
    elif attTypeStr == GetTypeNameString(AttributeType.Integer64):
        return "0"
    elif attTypeStr == GetTypeNameString(AttributeType.Float):
        return "0"
    elif attTypeStr == GetTypeNameString(AttributeType.Double):
        return "0"
    elif attTypeStr == GetTypeNameString(AttributeType.Boolean):
        return "False"
    else:
        return "Unknown"


class Attribute:
    def __init__(self, type, name, value, islocked, isvaluelocked):
        self.Value = value
        self.Type  = type
        self.Name  = name
        self.isLocked = islocked
        self.isValueLocked = isvaluelocked

    def asDict(self):
        return {"value": self.Value,
                "type": self.Type,
                "name": self.Name,
                "isLocked": self.isLocked,
                "isValueLocked": self.isValueLocked}

    def print(self):
        print(self.asDict())


def ApplyAttributeType(attrStr, attType):
    if attType == GetTypeNameString(AttributeType.String):
        return str(attrStr)
    elif attType == GetTypeNameString(AttributeType.Boolean):
        if attrStr.lower() == "false" or attrStr.lower() == "0" or attrStr.lower() == "no":
            return False
        else:
            return True
    elif attType == GetTypeNameString(AttributeType.Float):
        return np.float32(attrStr)
    elif attType == GetTypeNameString(AttributeType.Double):
        return np.float64(attrStr)
    elif attType == GetTypeNameString(AttributeType.Integer32):
        return np.int32(attrStr)
    elif attType == GetTypeNameString(AttributeType.Integer64):
        return np.int64(attrStr)
    else:
        raise ValueError("Bad casting. Cannot cast " + attrStr + " to " + attType)
