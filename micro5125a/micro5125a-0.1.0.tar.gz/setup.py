# Set __version__ in the setup.py
with open('micro5125a/version.py') as f: exec(f.read())

from setuptools import setup

setup(name='micro5125a',
      version=__version__,
      description='Handle Microsemi (former Symmetricom, former Timing Solutions) 5125a/5120a/5115a/5110a Phase Noise Test Set device (driver + cli script)',
      author='Benoit Dubois',
      author_email='benoit.dubois@femto-st.fr',
      url='http://femto-engineering.fr',
      packages=['micro5125a'],
      scripts=["bin/micro-5125a"],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering'],)

