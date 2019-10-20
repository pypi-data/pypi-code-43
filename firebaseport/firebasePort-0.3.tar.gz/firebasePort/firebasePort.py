import os, subprocess, pyrebase
class Database(object):
    def __init__(self, config):
        
        self.firebase = pyrebase.initialize_app(config)
        self.db = self.firebase.database()
        
    def writeData(self, path, data):
        path = path.split('/')
        self.db = self.firebase.database()
        for i in path:
            self.db = self.db.child(i)
        self.db.set(data)
    def getData(self, path):
        path = path.split('/')
        self.db = self.firebase.database()
        for i in path:
            self.db = self.db.child(i)
        return(self.db.get().val())
        
        