import subprocess


def install(packages):
    for package in packages:
        subprocess.run(['pip3', 'install', package])