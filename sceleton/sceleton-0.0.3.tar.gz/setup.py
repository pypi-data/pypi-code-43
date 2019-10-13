from setuptools import setup
import os
import sys


current_path = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_path, 'README.rst'), encoding='utf-8') as file:
      long_description = file.read()

data_files_path = os.path.join(current_path, 'sceleton', 'structure', 'project')
skeletons = os.listdir(os.path.join(data_files_path, 'skeleton'))
licenses = os.listdir(os.path.join(data_files_path, 'licenses'))

skeleton_files = [os.path.join(data_files_path, 'skeleton', file) for file in skeletons]
license_files = [os.path.join(data_files_path, 'licenses', file) for file in licenses]

subpackages_path = os.path.join(current_path, 'sceleton')


subpackages = []
parent = 'sceleton'
for subdir, _, _ in os.walk(subpackages_path):
      subdirs = subdir.split(os.sep)
      parent_index = subdirs.index(parent) + 1
      subpackages.append('.'.join(subdirs[parent_index:]))

setup(name='sceleton',
      version='0.0.3',
      description='CLI tool for creating packages in python3.',
      long_description=long_description,
      url='https://github.com/monzita/sceleton',
      author='Monika Ilieva',
      author_email='email@example.com',
      license='MIT License',
      keywords='python3 sceleton package manager',
      packages=[*subpackages],
      package_dir={'sceleton' : 'sceleton'},
      py_modules=['sceleton'],
      package_data={'sceleton': [*skeleton_files, *license_files]},
      install_requires = ['docopt', 'twine'],
      entry_points = {
        'console_scripts': [
          'sceleton=sceleton.cli:main'
        ],
      },
      classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3 :: Only',
            'Topic :: Utilities',
            'License :: OSI Approved :: MIT License',
      ],
      zip_safe=True)