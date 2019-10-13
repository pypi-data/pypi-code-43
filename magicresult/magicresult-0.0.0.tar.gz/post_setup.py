from distutils.sysconfig import get_python_lib
from shutil import copyfile
from os import path

def main():
    here = path.abspath(path.dirname(__file__))
    print("Copying 'macro.pth' to %s" % get_python_lib())
    copyfile(
        path.join(here, 'macro.pth'),
        path.join(get_python_lib(), 'macro.pth')
    )

if __name__ == '__main__':
    main()
