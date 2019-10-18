from setuptools import setup
from pathlib import Path

about = {}
with Path(Path(__file__).parent, 'funcgen', '__version__.py').open('r') as f:
    exec(f.read(), about)

setup(
    name=about['__title__'],
    version=about['__version__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=['funcgen'],
    package_data={'': ['LICENSE']},
    package_dir={'funcgen': 'funcgen'},
    include_package_data=True,
    python_requires='>=3.6',
    extras_require={
        'docs': 'sphinx==2.2.0',
        'dev': 'twine==2.0.0'
    },
    license=about['__license__'],
    project_urls={
        'Documentation': 'https://funcgen.readthedocs.io/en/latest/',
        'Source': 'https://github.com/ConradBailey/funcgen',
    },
)
