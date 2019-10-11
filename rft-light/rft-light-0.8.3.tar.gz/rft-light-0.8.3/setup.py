import subprocess
import collections
import json
import sys
import os

required_packages=collections.OrderedDict()
required_packages['influx-client']={"pip_working": True, "nexus_pkg_available": True, "version": "==1.9", "description": ""}
required_packages['requests']={"pip_working": True, "nexus_pkg_available": True, "version": "==2.22.0", "pip_error": "", "description": ""}
required_packages['collections2']={"pip_working": True, "nexus_pkg_available": True, "version": "==0.3.0", "description": "A set of improved data types inspired by the standard library's collections module"}
required_packages['datetime']={"pip_working": True, "nexus_pkg_available": True, "version": "==4.3", "description": ""}
required_packages['et_xmlfile']={"pip_working": True, "nexus_pkg_available": True, "version": "==1.0.1", "description": "An implementation of lxml.xmlfile for the standard library"}
required_packages['lxml']={"pip_working": True, "version": "==4.3.3", "pip_error": "Could not find function xmlCheckVersion in library libxml2. Is libxml2 installed?", "description": "Powerful and Pythonic XML processing library combining libxml2/libxslt with the ElementTree API.", "nexus_pkg_available": True}
required_packages['robotframework']={"pip_working": True, "nexus_pkg_available": True, "version": "==3.1.1", "description": ""}
required_packages['robotframework-archivelibrary']={"pip_working": True, "nexus_pkg_available": True, "version": "==0.4.0", "description": "Robot Framework keyword library for handling ZIP files"}
required_packages['robotframework-pabot']={"pip_working": True, "nexus_pkg_available": True, "version": "== 0.86", "description": ""}
required_packages['robotframework-swift-ride']={"pip_working": True, "nexus_pkg_available": True, "version": "==1.7.4rc1.dev0", "description": "Robot Framework is a generic test automation framework for acceptance level testing. RIDE is a lightweight and intuitive editor for Robot Framework test data."}
required_packages['robotframework-seleniumlibrary']={"pip_working": True, "nexus_pkg_available": True, "version": "==3.3.1", "description": ""}
required_packages['robotframework-selenium2library']={"pip_working": True, "nexus_pkg_available": True, "version": "==3.0.0", "description": ""}
required_packages['robotframework-stringformat']={"pip_working": True, "nexus_pkg_available": True, "version": "==0.1.8", "description": "StringFormat is a string formatter for Robot Framework. This library is a python .format() wrapper."}
required_packages['selenium']={"pip_working": True, "nexus_pkg_available": True, "version": "==3.141.0", "description": "Python language bindings for Selenium WebDriver"}
required_packages['setuptools']={"pip_working": True, "nexus_pkg_available": True, "version": "==41.0.1", "description": "SetupTools."}
required_packages['six']={"pip_working": True, "nexus_pkg_available": True, "version": "==1.12.0", "description": "Python 2 and 3 compatibility utilities"}
required_packages['wheel']={"pip_working": True, "nexus_pkg_available": True, "version": "==0.33.4", "description": ""}

from sys import platform
#if platform == "win32":
	#required_packages['SendKeys']={"pip_working": True, "nexus_pkg_available": True, "version": "==0.3", "description": ""}
	

from setuptools import setup
			
def pkg_list():
	a=[]
	for package in required_packages:
		a.append(package+required_packages[package]['version'])
	return a

setup(name='rft-light',
      version='0.8.3',
      description='RobotFramework Toolkit Light',
      url='https://github.com/ludovicurbain/rft-light.git',
      author='Ludovic Urbain',
      author_email='ludovic.urbain@swift.com',
      license='MIT',
      packages=['rft-light'],
	  install_requires=[
          pkg_list(),
      ],
      zip_safe=False)