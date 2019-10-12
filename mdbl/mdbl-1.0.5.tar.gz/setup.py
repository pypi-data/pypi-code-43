from setuptools import setup
import re

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

version = '1.0.5'

readme = ''
with open('README.rst') as f:
    readme = f.read()

extras_require = {
    'voice': ['PyNaCl==1.3.0'],
    'docs': [
        'sphinx==1.8.5',
        'sphinxcontrib_trio==1.1.0',
        'sphinxcontrib-websupport',
    ]
}

setup(name='mdbl',
      author='FightMan01',
      url='https://github.com/FightMan01',
      packages = ['mdbl'],
      version=version,
      license='MIT',
      description='Python API wrapper az Magyar Discord Bot Lista APIhoz.',
      long_description=readme,
      long_description_content_type="text/x-rst",
      include_package_data=True,
      install_requires=requirements,
      python_requires='>=3.5.3',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
      ]
)
