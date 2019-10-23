from os import path
try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

install_reqs = parse_requirements("./requirements.txt", session='hack')
reqs = [str(ir.req) for ir in install_reqs]

# Get the long description from the README file
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(
    name="cerebralcortex-restclient",

    version='3.1.0r1',

    description='REST client for CerebralCortex-APIServer.',
    long_description=long_description,

    author='MD2K.org',
    author_email='dev@md2k.org',

    license='BSD2',
    url = 'https://github.com/MD2Korg/CerebralCortex-RESTClient/',

    classifiers=[

        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',

        'License :: OSI Approved :: BSD License',

        'Natural Language :: English',

        'Programming Language :: Python :: 3',

        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: System :: Distributed Computing'
    ],

    keywords='mHealth machine-learning data-analysis',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=reqs,


    entry_points={
        'console_scripts': [
            'main=main:main'
        ]
    },
)
