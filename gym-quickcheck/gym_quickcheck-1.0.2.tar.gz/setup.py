import subprocess
import sys
from pathlib import Path

from setuptools import setup, find_packages

here = Path(__file__).absolute().parent

error = subprocess.call(['make', 'meta'])
if error:
      print(f"failed to run 'make meta' with error: {error}")
      sys.exit(-1)

with open(here / Path('README.md'), encoding='utf-8') as f:
      long_description = f.read().replace('\r\n', '\n')

_version = {}
with open(here / Path('gym_quickcheck/_version.py', mode='r')) as f:
      exec(f.read(), _version)

setup(
      name='gym_quickcheck',
      version=_version['__version__'],
      description='Gym environments that allow for coarse but fast testing of AI agents.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/SwamyDev/gym-quickcheck',
      author='Bernhard Raml',
      author_email='pypi-reinforcment@googlegroups.com',
      classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Topic :: Scientific/Engineering :: Artificial Intelligence',
            'Topic :: Software Development :: Testing',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
      ],
      packages=find_packages(exclude=['build', 'dist', 'reinforcement.egg-info', 'assets', 'scrips', 'tests']),
      install_requires=['gym'],
      extras_require={'test': ['pytest']},
      keywords='OpeanAI gym testing continuous integration',
      project_urls={
            'Bug Reports': 'https://github.com/SwamyDev/gym-quickcheck/issues',
            'Source': 'https://github.com/SwamyDev/gym-quickcheck',
      },
)
