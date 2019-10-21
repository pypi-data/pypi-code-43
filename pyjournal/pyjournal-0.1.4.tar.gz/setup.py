from setuptools import setup, find_packages

setup(name='pyjournal',
      version='0.1.4',
      description='An app for personal journaling',
      packages=find_packages(),
      entry_points = {
      'console_scripts':[
      	'journal = pyjournal.__main__:write',
      	]
      })