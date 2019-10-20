import firebasePort, json, sys, os, urllib.request, subprocess, requests
if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']
from PyQt5 import QtGui
from PyQt5.Qt import QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QStyle

class Update(object):
    def __init__(self, config, applicationUrl, appName, path, displayErrorMessages = True, autoUpdate = False, debugPath = None):
        self.config = config
        self.serverDomain = config['authDomain']
        self.applicationUrl = applicationUrl
        self.appName = appName
        self.displayErrorMessages = displayErrorMessages
        self.autoUpdate = autoUpdate
        self.path = path

        self.debugPath = debugPath


    def checkUpdate(self):
        if not self.internet_connection(self.serverDomain):
            if self.displayErrorMessages:
                MessageBox.newMessageBox(error='server_timeout')
            return
        
        self.firebase = firebasePort.Database(self.config)
        cloudVersion = self.firebase.getData(self.path)
        
        if self.debugPath is None:
            if os.path.exists('version.json'):
                with open('version.json', 'r') as json_file:
                    data = json.load(json_file)
                    localVersion = data['program']['version']
                    skipVersion = data['program']['skipversion']
            else:
                data = {'program': {'version': '0.0.1', 'skipversion': '0.0.0'}}
                localVersion = data['program']['version']
                skipVersion = data['program']['skipversion']
                with open('version.json', 'w') as f:
                    json.dump(data, f)
        else:
            if os.path.exists(f'{self.debugPath}/version.json'):
                with open(f'{self.debugPath}/version.json', 'r') as json_file:
                    data = json.load(json_file)
                    localVersion = data['program']['version']
                    skipVersion = data['program']['skipversion']
            else:
                data = {'program': {'version': '0.0.1', 'skipversion': '0.0.0'}}
                localVersion = data['program']['version']
                skipVersion = data['program']['skipversion']
                with open(f'{self.debugPath}/version.json', 'w') as f:
                    json.dump(data, f)
            

        
        if cloudVersion == skipVersion:
            return

        localVersion = localVersion.split('.')
        cloudVersion = cloudVersion.split('.')      

        if cloudVersion[0] > localVersion[0]:
            type_ =  'update'
        elif cloudVersion[1] > localVersion[1]:
            type_ = 'unstable'
        elif cloudVersion[2] > localVersion[2]:
            type_ = 'bugfixes'   
        else:
            return 'No update'

        if not self.autoUpdate:
            retval = MessageBox.newMessageBox(type_, '.'.join(localVersion), '.'.join(cloudVersion))
        else:
            retval = 0

        if retval == 0:
            self.updateApplication('.'.join(cloudVersion))
        elif retval == 1:
            data['program']['skipversion'] = '.'.join(cloudVersion)
            with open('version.json', 'w') as g:
                json.dump(data, g)
        elif retval == 2:
            return
        


    def internet_connection(self, domain):
        try:
            requests.get(f'https://{domain}', timeout=5)
            return True
        except requests.ConnectionError: 
            return False

    def updateApplication(self, nv):
        if getattr(sys, 'frozen', False):
            dir_path = os.path.dirname(sys.executable)
        elif __file__:
            dir_path = os.path.dirname(__file__)
        urllib.request.urlretrieve(self.applicationUrl, f'{dir_path}/new_version.exe')

        if self.debugPath is None:
            with open('version.json', 'r') as json_file:
                data = json.load(json_file)
                data['program']['version'] = nv
                with open('version.json', 'w') as g:
                    json.dump(data, g)
        else:
            with open(f'{self.debugPath}/version.json', 'r') as json_file:
                data = json.load(json_file)
                data['program']['version'] = nv
                with open(f'{self.debugPath}/version.json', 'w') as g:
                    json.dump(data, g)

        if self.debugPath is None:
            with open('rename.bat', 'w') as rn:
                rn.write(f'''
                    timeout 1
                    del /f {self.appName}.exe
                    ren new_version*.exe {self.appName}.exe
                    {self.appName}.exe
                ''')
            devnull = open(os.devnull, 'wb')
            subprocess.Popen(['rename.bat'], shell=False)
        else:
            with open(f'{self.debugPath}/rename.bat', 'w') as rn:
                rn.write(f'''
                    timeout 1
                    del /f {self.appName}.exe
                    ren new_version*.exe {self.appName}.exe
                    {self.appName}.exe
                ''')
            devnull = open(os.devnull, 'wb')
            subprocess.Popen([f'{self.debugPath}/rename.bat'], shell=False)
        sys.exit()

class MessageBox(QMessageBox):
    def __init__(self, type_, lv, cv, error):
        super(MessageBox, self).__init__() 
        if error is None:
            self.setIcon(QMessageBox.Information)
            self.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_BrowserReload')))
            self.setWindowTitle('Update application')
            self.addButton("Update", QMessageBox.NoRole)
            self.addButton("Skip version", QMessageBox.NoRole)
            self.addButton("Ask later", QMessageBox.NoRole)
            
            if type_ == 'update':
                self.setText('Would you like to update the application to a new version?')
            elif type_ == 'unstable':
                self.setText('Would you like to update the application to a new version?<br> <b> It might be unstable!</b>')
            elif type_ == 'bugfixes':
                self.setText('There are some bugfixes available for this apllication.<br> Would you like to update?')
            self.setInformativeText(f"<b>{lv} >>> {cv}</b>")
        else:
            if error == 'version_not_found':
                self.setIcon(QMessageBox.Information)
                self.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxCritical')))
                self.setWindowTitle('File not found!')
                self.setText('<b>version.json</b> file not found. Can\'t check for updates!')
            elif error == 'server_timeout':
                self.setIcon(QMessageBox.Information)
                self.setWindowIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxWarning')))
                self.setWindowTitle('Server timeout!')
                self.setText('Couldn\'t connect with the server! Unable to check for updates!')

    @staticmethod
    def newMessageBox(type_ = None, lv = None, cv = None, error = None):
        app = QApplication(sys.argv)
        app.exec_
        MessageBoxInstance = MessageBox(type_, lv, cv, error)
        retval = MessageBoxInstance.exec_()
        return retval
    