import subprocess

from . import sceleton


def ignore(project_name=None):
    gitignore = sceleton('gitignore.txt')
    gitignore.append("{}.egg-info".format(project_name))
    gitignore = ''.join(gitignore)
    return gitignore


def init(project_path=None):
    subprocess.run(['git', 'init', project_path])