import os
import datetime
import time
import ynitdb

class Wall:
    def __init__(self, name, base_dir="/opt/"):
        self.base_dir = base_dir + name + ".wall/"
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
        self.planks = {}

    def create_plank(self, name, nails, path=None):
        self.planks[name] = Plank(self, name, nails)
        return self.planks[name]
        
class Plank:
    def __init__(self, wall, name, nails, timeformat="%Y-%d-%b %H:%M:%S", path=None):
        self.name = name
        self.timeformat = timeformat
        self.wall = wall
        self.nails = nails
        if(path):
            self.path = path
        else:
            self.path = self.wall.base_dir + name + ".plank"
        self.file = ynitdb.Database(path=self.path)
        for nail, value in self.nails.items():
            if not(nail in self.file):
                self.file[nail] = []

    def hammer(self, nail_id, data):
        cdata = {}
        for key, value in data.items():
            if(key in self.nails[nail_id]["collect"]):
                cdata[key] = value
        cdata["_PLANKS_time"] = int(time.time())
        cdata["_PLANKS_strtime"] = time.strftime(self.timeformat, time.gmtime(cdata["_PLANKS_time"]))
        print(self.nails[nail_id]["message"].format(**cdata))
        self.file[nail_id].append(cdata)
        self.file.write()

