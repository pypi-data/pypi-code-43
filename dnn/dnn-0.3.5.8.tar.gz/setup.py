"""
Hans Roh 2015 -- http://osp.skitai.com
License: BSD
"""
import re
import sys
import os
import shutil, glob
from warnings import warn
try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

with open('dnn/__init__.py', 'r') as fd:
	version = re.search(r'^__version__\s*=\s*"(.*?)"',fd.read(), re.M).group(1)

if sys.argv[-1] == 'publish':
	buildopt = ['sdist', 'upload']
	if os.name == "nt":
		buildopt.insert (0, 'bdist_wheel')
	os.system('python setup.py %s' % " ".join (buildopt))
	#os.system('twine upload dist/aquests-%s*' % version)
	for each in os.listdir ("dist"):
		os.remove (os.path.join ('dist', each))
	sys.exit()

classifiers = [
  'License :: OSI Approved :: MIT License',
  'Development Status :: 3 - Alpha',
	'Environment :: Console',
	'Topic :: Software Development :: Libraries :: Python Modules',
	'Topic :: Scientific/Engineering :: Artificial Intelligence',
	'Intended Audience :: Developers',
	'Intended Audience :: Science/Research',
	'Programming Language :: Python',
	'Programming Language :: Python :: 3'
]

packages = [
	'dnn',
	'dnn.audio',
	'dnn.video',
	'dnn.image',
	'dnn.text',
	'dnn.similarity',
	'dnn.costs',
]

package_dir = {'dnn': 'dnn'}

package_data = {
	"dnn": []
}

install_requires = [
	"rs4",
	"matplotlib",
	"sklearn",
	"scikit-image",
	"imageio",
	"future",
	"networkx",
	"tqdm",
	"librosa",
	"soundfile",
	"colorama",
    "hyperopt",
	"protobuf"
]

with open ('README.rst', encoding='utf-8') as f:
	long_description = f.read ()

setup(
	name='dnn',
	version=version,
	description='Deep Neural Network Library',
	long_description = long_description,
	url = 'https://gitlab.com/hansroh/dnn',
	author='Hans Roh',
	author_email='hansroh@gmail.com',
	packages=packages,
	package_dir=package_dir,
	package_data = package_data,
	license='MIT',
	platforms = ["posix",],
	download_url = "https://pypi.python.org/pypi/dnn",
	install_requires = install_requires,
	classifiers=classifiers
)
