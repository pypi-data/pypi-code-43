import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tworavens_preprocess",
    version="0.1.4",
    author="Two Ravens team",
    author_email="raman_prasad@harvard.edu",
    description="TwoRavens Preprocess package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TwoRavens/raven-metadata-service",

    packages=['raven_preprocess',
              'raven_preprocess.basic_utils'
              ],

    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # These classifiers are *not* checked by 'pip install'. See instead
        # 'python_requires' below.
        'Programming Language :: Python :: 3.6'
        ],

        keywords='tworavens preprocess metadata',  # Optional

        python_requires='>=3.6',

        install_requires=[
            'pandas>=0.22.0',
            'scipy>=1.0.0',
            'simplejson>=3.13.2',
            'xlrd>=1.1.0',
            'jsonschema>=2.6.0',
        ],
)
