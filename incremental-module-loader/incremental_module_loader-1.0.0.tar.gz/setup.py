from setuptools import setup


from os import path
HERE = path.abspath(path.dirname(__file__))
with open(path.join(HERE, 'README.md')) as f:
    long_description = f.read()
    
setup(
    name='incremental_module_loader',
    version='1.0.0',
    license='MIT',
    description='Micro-framework to allow incremental dependencies injection in inter-related modules.',
    url='https://gitlab.com/tackv/incremental-module-loader',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='William Laroche',
    author_email='william.laroche@tackv.ca',
    maintainer='William Laroche',
    maintainer_email='william.laroche@tackv.ca',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        
        'Topic :: Software Development',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
    ],
    py_modules=['incremental_module_loader'],
    package_data={
    },
    install_requires=[],
    extras_require={
    },
    setup_requires=[
    ],
    tests_require=[
        'tox',
    ],
    test_suite="tox",
)