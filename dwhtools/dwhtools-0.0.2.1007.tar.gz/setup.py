import os
from setuptools import setup, find_packages

def read(filename):
	return open(os.path.join(os.path.dirname(__file__), filename)).read()
	
setup(
	name='dwhtools',#Dieser name muss beim installieren (zB pip install) angegeben werden
	#version='0.0.2.16',
	version=read("Version.txt"),
	author="Bejamin Weber",
	author_email="b.weber@oraylis.de",
	packages=find_packages('src'),
	package_dir = {'': 'src'},
	description = 'Dies ist eine kurze Beschreibung',
	long_description=read('README.md'),
	install_requires=[]	
)