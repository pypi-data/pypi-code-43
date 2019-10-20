from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()


setup(name='pyveplot',
      version='1.0.0',
      author='Rodrigo Garcia',
      author_email='rgarcia@iecologia.unam.mx',
      description='SVG Hiveplot Python API',
      long_description=readme(),
      long_description_content_type="text/markdown",
      url='http://gitlab.com/rgarcia-herrera/pyveplot',
      packages=['pyveplot'],      
      classifiers=[
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python :: 3.5',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering',
      ],
      license='GPLv3',
      install_requires=[ 'svgwrite' ],
      python_requires='>=3.6')
