import setuptools
import os

my_classifiers = [
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
		"Programming Language :: Python :: 3.8",
		"Topic :: Software Development :: Libraries :: Application Frameworks",
		"Topic :: Multimedia :: Graphics",
		"Operating System :: OS Independent",
]

curr_path = os.path.dirname(os.path.abspath(__file__))
readmefile = os.path.join(curr_path, "PySimpleGUIDesigner", "README.md")

with open(readmefile, "r", encoding='utf-8') as ff:
	long_description = ff.read()

setuptools.setup(
	description="PySimpleGUI designer, that uses transpiler to produce code from Qt Designer xml file.",
	entry_points={"console_scripts": ["PySimpleGUIDesigner = PySimpleGUIDesigner.main:cli"]},
	url="https://github.com/nngogol/PySimpleGUI_designer",
	packages=setuptools.find_packages(),
	author_email="nngogol09@gmail.com",
	long_description=long_description,
	long_description_content_type="text/markdown",
	name="PySimpleGUIDesigner",
	author="Nikolay Gogol",
	license='GNU-GPL',
	version="0.1.4.2",
	classifiers=my_classifiers,
	package_data={'': ['*.ui']},
	install_requires=['PySimpleGUI'],
	# install_requires=['PySide2', 'click>=7.0', 'PySimpleGUI'],
	#  _            _           _
	# (_)          | |         | |
	#  _ _ __   ___| |_   _  __| | ___
	# | | '_ \ / __| | | | |/ _` |/ _ \
	# | | | | | (__| | |_| | (_| |  __/
	# |_|_| |_|\___|_|\__,_|\__,_|\___|
)