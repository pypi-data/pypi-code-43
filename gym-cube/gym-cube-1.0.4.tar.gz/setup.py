from setuptools import setup
from setuptools import find_packages

setup(name='gym-cube',
      version='1.0.4',
      author='alseambusher',
      description='Rubik\'s cube environment with OpenAI gym',
      install_requires=['gym', 'imageio', 'imageio-ffmpeg'],
      url="https://github.com/alseambusher/gym-cube",
      packages=find_packages()
      )
