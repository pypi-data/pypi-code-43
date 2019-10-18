from setuptools import setup, find_packages,Command
import sys, os, glob
from pathlib import Path

class CleanCommand(Command):
    
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        os.system('rmdir /Q /S build dist rokuality-python.egg-info')
        user_paths = sys.path 
        for path in user_paths:
            if Path(path).is_dir():
                os.chdir(path)
                for name in glob.glob(path+'/rokuality-python-*.*.egg'):
                    os.remove(name)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="rokuality-python",
    version="1.1.0",
    author="rokualitydevs@rokuality.com",
    author_email="rokualitydevs@rokuality.com",
    description="Python bindings for the rokuality platform. End to end automation for Roku, Xbox, and more!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rokuality/rokuality-python",
    packages=find_packages(),
    install_requires=['requests','pytest'],
    python_requires='>=3.6.5',
    cmdclass={'clean': CleanCommand,}
)