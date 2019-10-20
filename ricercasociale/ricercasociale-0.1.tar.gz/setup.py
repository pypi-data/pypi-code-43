from setuptools import setup

setup(name='ricercasociale',
      version='0.1',
      description='analisi monovariata e bivariata per le scienze sociali',
      url='https://github.com/scarsellifi/ricercasociale.git',
      author='Marco Scarselli',
      author_email='scarselli@gmail.com',
      license='MIT',
      packages=['ricercasociale'],
      install_requires=[
          'numpy',
          'pandas',
          'matplotlib',
          'seaborn'
      ],
      zip_safe=False)