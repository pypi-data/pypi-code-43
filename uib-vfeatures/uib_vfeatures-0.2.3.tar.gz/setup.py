# coding=utf-8
from setuptools import setup

setup(name='uib_vfeatures',
      version='0.2.3',
      description='Vision features of generalistic use',
      url='https://gitlab.com/miquelca32/features',
      author="Miquel Miró Nicolau, Bernat Galmés Rubert, Dr. Gabriel Moyà Alcover",
      author_email='miquelca32@gmail.com, bernat_galmes@hotmail.com, gabriel_moya@uib.es',
      license='MIT',
      packages=['uib_vfeatures'],
      keywords=['Features extraction', 'Machine Learning', 'Computer Vision'],
      install_requires=[
          'scikit-image',
          'opencv-python==4.1.1.26',
          'matplotlib',
          'scipy',
          'scikit-image',
          'numpy'
      ],
      zip_safe=False)
