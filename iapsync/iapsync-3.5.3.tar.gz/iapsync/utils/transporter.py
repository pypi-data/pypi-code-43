import subprocess
from pathlib import PurePath


def get_transporter():
    xcode_root_b = subprocess.check_output(['xcode-select', '-p'])
    xcode_root = PurePath(str(xcode_root_b, 'utf-8').rstrip()).parent
    transporter_b = subprocess.check_output(['find', xcode_root.as_posix(), '-name', 'iTMSTransporter', '-print', '-quit'])
    return str(transporter_b, 'utf-8').rstrip()

transporter_path = get_transporter()

if __name__ == '__main__':
    print(transporter_path)
