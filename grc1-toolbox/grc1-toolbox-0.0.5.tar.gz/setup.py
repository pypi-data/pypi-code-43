import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="grc1-toolbox",
    version="0.0.5",
    # Author details
    author='Auquan Team',
    author_email="qqadmins@auquan.com",
    description="Toolbox for QQ15",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?
    keywords='auquan finance trading backtesting development',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=setuptools.find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['requests', 'plotly', 'numpy', 'pandas', 'bs4', 'scipy', 'sklearn', 'lxml', 'auquan_toolbox']
)
    
