import getpass
import os
from os.path import abspath, dirname, isdir
from shutil import copyfile

from cryptography.fernet import Fernet

CWD = abspath(dirname(__file__)) 
HOME = f'/Users/{getpass.getuser()}'

if __name__ == "__main__":
    
    # generate encryption key
    key = Fernet.generate_key()
    with open(f'{HOME}/.chat-app.key', 'wb') as f:
        f.write(key)
    
    # get user info
    os.system("stty -echo")
    password = input('Password: ')
    os.system("stty echo")
    print()
   
    bytes_info = password.encode("utf-8")
    fernet = Fernet(key)
    encrypted = fernet.encrypt(bytes_info)

    with open(f'{HOME}/.chat-app-user-secrets', 'wb') as f:
        f.write(encrypted)

    # create ~/bin dir if it doesn't already exist
    bin_dir = f"{HOME}/bin"

    if not isdir(bin_dir):
        os.mkdir(bin_dir)

    # copy python files to bin
    copyfile(CWD + "/client.py", bin_dir + "/client.py")
    copyfile(CWD + "/server.py", bin_dir + "/server.py")
    
    # create executable to run script
    script = """
#!/bin/bash
if [ $1 = "server" ]; then
    python3 ~/bin/server.py
elif [ $1 = "client" ]; then
    python3 ~/bin/client.py
fi
"""
    with open(f"{bin_dir}/chat-app", "w+") as f:
        f.write(script)
    
    # give permission to executable
    os.system("chmod +x ~/bin/chat-app") 
    
