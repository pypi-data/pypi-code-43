import os
import shutil
from subprocess import Popen

try:
    shutil.rmtree("dist")
    shutil.rmtree("build")
    shutil.rmtree("git_python.egg-info")
except Exception:
    pass

Popen("python setup.py sdist bdist_wheel", shell=True).wait()
Popen("python -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*", shell=True).wait()