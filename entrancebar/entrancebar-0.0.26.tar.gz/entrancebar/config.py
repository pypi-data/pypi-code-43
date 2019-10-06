import os
import os.path
import json

def fileObject():
    if os.path.exists(os.path.join(os.getcwd(), "./entrancebar.config.json")):
        if os.path.isfile(os.path.join(os.getcwd(), "./entrancebar.config.json")):
            return open(os.path.join(os.getcwd(), "./entrancebar.config.json"), encoding="utf-8")

def fileContent():
    fo = fileObject()
    content = fo.read()
    fo.close()
    return content

def config():
    return json.loads(fileContent())