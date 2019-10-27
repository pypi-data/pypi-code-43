import setuptools, platform, distutils, sys, os
from distutils.cmd import Command
from distutils.util import execute
from setuptools.command.install import install

import shutil
from subprocess import call


with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

class PostInstallCommand(install):
	"""
	modified installer.
	A custom command to install udev (for Linux) or devd (for FreeBSD) rules. credit : terrapi package
	to allow KuttyPy hardware to access the dialout group.
	"""
	print('post install command class!',install.user_options)
	description = "install udev or devd rules (pip must be run as root)"
	user_options = install.user_options

	udev_reload = ['udevadm', 'control', '--reload-rules']
	udev_trigger = ['udevadm', 'trigger', '--subsystem-match=usb',
		  '--attr-match=idVendor=1A86', '--action=add']
	devd_restart = ['service', 'devd', 'restart']
	linux_create_group = ['groupadd', 'dialout']
	fbsd_create_group = ['pw', 'groupadd', 'sispmctl']

	def run(self):
		if 'sdist' not in sys.argv:
			print('installing rules for accessing KuttyPy hardware...', sys.argv)
			system = platform.system()
			if os.getuid() != 0 and system in ['Linux', 'FreeBSD']:
				raise OSError(
						'You must have root privileges to install udev/devd rules! sudo pip3 install kuttyPy')
			if system == 'Linux':
				shutil.copy('resources/99-kuttypy-pip.rules', '/etc/udev/rules.d/')
				execute(lambda: call(self.linux_create_group), [],
						"Creating dialout group")
				execute(lambda: call(self.udev_reload), [], "Reloading udev rules")
				execute(lambda: call(self.udev_trigger), [], "Triggering udev rules")
			elif system == 'FreeBSD':
				shutil.copy('resources/sispmctl.conf', '/usr/local/etc/devd/')
				execute(lambda: call(self.fbsd_create_group), [],
						"Creating sispmctl group")
				execute(lambda: call(self.devd_restart), [], "Restarting devd")
			else:
				print("Not Linux, nothing to do.")
		install.run(self)


setuptools.setup(
    name="kuttyPy",
    version="1.0.14",
    install_requires=requirements,
    author="Jithin B.P",
    author_email="jithinbp@gmail.com",
    description="Python package for KuttyPy AVR trainer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/csparkresearch/kuttypy-gui",
    packages=setuptools.find_packages(exclude=['contrib', 'tests']),
    package_data = {
        '': ['*.c','*.qss','*.rules','*.conf'],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Intended Audience :: Education',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
    'console_scripts': [
        'kuttypy=kuttyPyGui.KuttyPyGUI:run',
        'kuttypyNano=kuttyPyGui:KuttyPyNano.run',
    		],
	},
    cmdclass={
        'install': PostInstallCommand,
    },
    keywords = 'atmega32 trainer data-acquisition',
    python_requires='>=3',
    project_urls={  # Optional
        'Source': 'https://github.com/csparkresearch/kuttypy-gui',
        'Read The Docs': 'https://kuttypy.readthedocs.io',
        'Buy Hardware': 'https://csparkresearch.in/kuttypy',
    },
)
