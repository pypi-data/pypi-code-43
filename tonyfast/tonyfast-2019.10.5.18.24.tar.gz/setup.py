import setuptools, datetime, nbconvert
from pathlib import Path

name = "tonyfast"

__version__ = None

here = Path(__file__).parent

setup_args = dict(
    name=name,
    version=datetime.datetime.now().isoformat().rpartition(':')[0].replace('-', '.').replace('T', '.').replace(':', '.'),
    author="tonyfast",
    url="https://github.com/tonyfast/gists",
    long_description=nbconvert.get_exporter('markdown')().from_filename(Path('readme.ipynb'))[0],
    long_description_content_type='text/markdown',

    python_requires=">=3.7",
    license="BSD-3-Clause",
    setup_requires=['pytest-runner'],
    tests_require=['pytest', "hypothesis", 'nbval'],
    install_requires=list(x for x in set(
            filter(bool, map(str.strip, '\n'.join(x.read_text() for x in Path().rglob('**/requirements.txt')).splitlines()))
        ) if x not in "tonyfast".split()),
    include_package_data=True,
    packages=setuptools.find_packages(),
    entry_points = {
        'pytest11': [],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: IPython",
        "Framework :: Jupyter",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",],)

if __name__ == "__main__" and '__file__' in globals():
    setuptools.setup(**setup_args)
