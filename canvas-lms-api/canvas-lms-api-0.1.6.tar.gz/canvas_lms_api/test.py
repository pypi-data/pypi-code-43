import yaml
import os
from canvas import Canvas
import time
import requests

def load_config(path='.'):
    _organization_name = "gatech"
    config_file_name = _organization_name + "-conf.yml"
    _config = ""
    with open(os.path.join(path, config_file_name)) as config_file:
        config = yaml.load(config_file)
        _config= config
    return _config

_config = load_config('../../tmp')
grader = Canvas(base=_config["base"], token=_config["canvas_api"], course=_config["canvas_course"])

#for conference in grader.GetConferences():
#    if len(conference["recordings"]) > 0:
#        for i in conference["recordings"]:
#            print (i["recording_id"])

print (grader.GetAllStudentUserNames())