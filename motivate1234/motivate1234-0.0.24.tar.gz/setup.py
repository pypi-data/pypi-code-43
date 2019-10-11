from setuptools import setup
from setuptools.command.install import install
import subprocess

__project__ = "motivate1234"
__version__ = "0.0.24"
__description__ = "this version with cmdclass"
__packages__ = ["motivate1234"]

class PostInstallCommand(install):
	def run(self):
		install.run(self)
		subprocess.call(["sed -i -e '$i \(sleep 5; su - pi -c /home/pi/Documents/online_radio_1.py)&\n' /etc/rc.local"], shell = True)

setup(
	name = __project__,
	version = __version__,
	description = __description__,
	packages = __packages__,
	include_package_data = True,
	cmdclass={
		'install': PostInstallCommand
	}
)

