import os
from pathlib import Path


def downloadPath():
    temp = str(os.path.expanduser('~') + '/Downloads')
    fin_path = str(os.path.join(str(temp)))
    print(fin_path)


def filePath(file_name):
    root_path = Path(__file__).parent.parent.parent.parent.parent
    temp = (os.path.join(root_path, 'file', file_name))
    fin_path = os.path.join(str(temp))
    return fin_path
