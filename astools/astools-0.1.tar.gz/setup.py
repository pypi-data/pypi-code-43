from setuptools import setup

setup(
    name = 'astools',
    version = '0.1',
    author = 'D. HU',
    author_email = 'dangning.hu@cea.fr',
    description = 'Python tool kit for astro uses.',
    license = 'BSD',
    keywords = 'astronomy astrophysics',
    url = 'https://github.com/kxxdhdn/Silo',

    python_requires='>=3.6',
    install_requires = ['h5py', 'reproject', ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS',
    ],
    
    ## Plugins
    entry_points={
        # Installation test with command line
        'console_scripts': [
            'astools_landing = astools:iTest',
        ],
    },

    ## Packages
    packages = ['astools'],
)
