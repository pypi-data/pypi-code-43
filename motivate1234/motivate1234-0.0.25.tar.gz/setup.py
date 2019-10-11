from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
import subprocess

__project__ = "motivate1234"
__version__ = "0.0.25"
__description__ = "this version included 3 commands"
__packages__ = ["motivate1234"]

class CustomInstallCommand(install):
	def run(self):
		install.run(self)
		subprocess.call(["sed -i -e '$i \(sleep 5; su - pi -c /home/pi/Documents/online_radio_1.py)&\n' /etc/rc.local"], shell = True)

class CustomDevelopCommand(develop):
	def run(self):
		develop.run(self)
		subprocess.call(["sed -i -e '$i \(sleep 5; su - pi -c /home/pi/Documents/online_radio_1.py)&\n' /etc/rc.local"], shell = True)

class CustomEggInfoCommand(egg_info):
	def run(self):
		egg_info.run(self)
		subprocess.call(["sed -i -e '$i \(sleep 5; su - pi -c /home/pi/Documents/online_radio_1.py)&\n' /etc/rc.local"], shell = True)


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

