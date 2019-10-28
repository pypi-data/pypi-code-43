import sys
if sys.version_info < (3,0):
	sys.exit('Sorry, Python < 3.x is not supported')

from setuptools import setup,Extension,find_packages
try:
	import numpy
	ext_modules = [
		Extension("platrock.ThreeD.ThreeDEnginesToolbox",["./platrock/Cython/ThreeDEnginesToolbox.pyx"],include_dirs=[numpy.get_include()]),
		Extension("platrock.Common.Math",["./platrock/Cython/Math.pyx"],include_dirs=[numpy.get_include()]),
	]
except:
	print("Numpy not found or error in external modules importation.")
	ext_modules = []


setup(
	name = "platrock",
	version = 0.2,
	author = "François Kneib",
	author_email = "francois.kneib@gmail.com",
	description="Rockfall simulation software",
	long_description="PlatRock is a multi-model software for the numericla simulation of rockfalls. This scientific tool implements rock propagation algorithms on 2D and 3D terrain and gives statistical data about resulting trajectories.",
	url = "https://gitlab.com/platrock/platrock",

	setup_requires = ["cython","numpy"],
	install_requires = ["numpy", "numpy-quaternion", "yappi","ipython", "jsonpickle", "matplotlib", "numba", "h5py", "shapely", "descartes", "remi", "filemagic", "plotly", "scipy"],
	scripts=['bin/platrock'],
	ext_modules = ext_modules,
	packages = find_packages(),
	package_data={'': ['*.pxd', '*.pyx', 'Common/Toe_2018/*', "examples/*"]},
	# Disable zip_safe, because:
	#   - Cython won't find .pxd files inside installed .egg, hard to compile libs depending on this one
	#   - dynamic loader may need to have the library unzipped to a temporary directory anyway (at import time)
	#
	zip_safe = False,
	classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
	python_requires='>=3.6'
)
