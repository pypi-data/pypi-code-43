from setuptools import setup

setup(name='pyabsorb',
      version='0.2',
      description='Calculate X-ray transmission',
      author='steche',
      packages=['pyabsorb'],
      zip_safe=False,
      entry_points={'console_scripts':['azazel=pyabsorb.azazel:main']},
      include_package_data=True
      )