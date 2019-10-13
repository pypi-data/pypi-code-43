import os
import subprocess
import sys
import re

from sceleton.decorators.missing_file import missing

def init(project_path):
    venv = os.path.join(project_path, 'venv')

    if not os.path.exists(venv):
        os.makedirs(venv)
    subprocess.run(['python3', '-m', 'venv', venv, '--without-pip'])
