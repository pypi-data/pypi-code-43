from setuptools import setup

setup(name='pyabsorb',
      version='0.3',
      description='Calculate X-ray transmission',
      author='steche',
      author_email='scr10438@gmx.ca',
      packages=['pyabsorb'],
      zip_safe=False,
      entry_points={'console_scripts':['azazel=pyabsorb.azazel:main']},
      include_package_data=True
      )