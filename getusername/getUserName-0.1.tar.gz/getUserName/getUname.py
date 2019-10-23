import getpass
import os

def getUSERname():
    print('hello'+getpass.getuser()+'how are you?')
    print('Hello, ' + os.getlogin() + '! How are you?')
