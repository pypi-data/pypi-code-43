import re


def removeNewLine(v):
    if type(v) == str:
        return re.sub("(\r|\n)", "", v.strip())
    else:
        return v
