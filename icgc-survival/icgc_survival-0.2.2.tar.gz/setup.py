from setuptools import setup

with open('README.md') as f:
    readme = f.read()

setup(
  name='icgc_survival',         # How you named your package folder (MyLib)
  packages=['icgc_survival'],   # Chose the same as "name"
  version='0.2.2',      # Start with a small number and increase it with every change you make
  license="MIT License",        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  long_description=readme,
  long_description_content_type="text/markdown",
  description='A framework for survival prediction and analysis of ICGC datasets',   # Give a short description about your library
  author='Julian Späth',                   # Type in your name
  author_email='spaethju@posteo.de',      # Type in your E-Mail
  url='https://github.com/julianspaeth/icgc-survival',   # Provide either the link to your github or to your website
  download_url='https://github.com/julianspaeth/icgc-survival/archive/v0.1.tar.gz',    # I explain this later on
  keywords=['survival-analysis', 'survival-prediction', 'machine-learning', 'random-survival-forest', 'icgc'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'requests',
          'pandas',
          'lifelines',
          'numpy',
          'random-survival-forest'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',    'License :: OSI Approved :: MIT License',   # Again, pick a license    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)