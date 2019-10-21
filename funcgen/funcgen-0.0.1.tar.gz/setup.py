from setuptools import setup
from pathlib import Path

ROOT = Path(__file__).parent

about = {}
with Path(ROOT, 'funcgen', '__version__.py').open('r') as f:
    exec(f.read(), about)

classifiers = [
    'Development Status :: 1 - Planning',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Topic :: Software Development :: Testing',
    'Topic :: Software Development :: Testing :: Unit',
]

setup(
    author=about['__author__'],
    author_email=about['__author_email__'],
    description=about['__description__'],
    extras_require={
        'docs': 'sphinx==2.2.0',
        'dev': 'twine==2.0.0'
    },
    include_package_data=True,
    license=about['__license__'],
    long_description=Path(ROOT, 'README.rst').open('r').read(),
    long_description_content_type='text/x-rst',
    name=about['__title__'],
    packages=['funcgen'],
    package_data={'': ['LICENSE']},
    package_dir={'funcgen': 'funcgen'},
    project_urls={
        'Documentation': 'https://funcgen.readthedocs.io/en/latest/',
        'Source': 'https://github.com/ConradBailey/funcgen',
    },
    python_requires='>=3.6',
    url=about['__url__'],
    version=about['__version__'],
)
