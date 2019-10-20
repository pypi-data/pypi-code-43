from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='heurispy',
      version='1.0.1',
      description='Framework for heuristic exploration of local search heuristics in discrete optimization problems.',
      long_description=long_description,
	  long_description_content_type="text/markdown",
	  url='https://gitlab.com/escamilla.een/heurispy',
      author='Esteban Escamilla Navarro',
      author_email='escamilla.een@gmail.com',
      license='',
      packages=['heurispy', 'heurispy.heuristicas'],
      install_requires=['pathos', 'tqdm', 'numpy', 'pandas', 'fpdf', 'matplotlib', 'pypdf2', 'xlrd'],
      include_package_data=True,
      zip_safe=False)
