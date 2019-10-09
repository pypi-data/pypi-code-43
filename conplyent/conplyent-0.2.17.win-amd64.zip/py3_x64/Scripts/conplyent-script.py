#!C:\PythonEnv\py3_x64\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'conplyent==0.2.17','console_scripts','conplyent'
__requires__ = 'conplyent==0.2.17'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('conplyent==0.2.17', 'console_scripts', 'conplyent')()
    )
