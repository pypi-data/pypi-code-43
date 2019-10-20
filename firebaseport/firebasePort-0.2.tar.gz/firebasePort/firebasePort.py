import os, subprocess, pyrebase
class Database(object):
    def __init__(self):
        config = {
            "apiKey": "AIzaSyDehw4NuNihPM1Lezc1GbPGWE272yHOE1s",
            "authDomain": "rgb-led-control.firebaseapp.com",
            "databaseURL": "https://rgb-led-control.firebaseio.com",
            "storageBucket": "rgb-led-control.appspot.com",
            "tls": {
                "rejectUnauthorized": False
                }
            }
        self.firebase = pyrebase.initialize_app(config)
        self.db = self.firebase.database()
        
    def writeData(self, path, data):
        path = path.split('/')
        for i in path:
            self.db = self.db.child(i)
        self.db.set(data)
        