import setuptools
import re

# version fetch
with open('kinlin/__init__.py', 'r') as f:
    version = re.search('__version__ = "(.+?)"', f.read()).group(1)

setuptools.setup(
    name='kinlin',
    version=version,
    description='WIP: PyTorch based framework',  # TODO
    license='MIT',
    author='the-lay',
    author_email='ilja@gubins.lv',
    url='https://github.com/the-lay/kinlin',
    keywords = [],  # TODO
    install_requires = [  # TODO
        'pytorch', 'mrcfile', 'numpy'
    ],
    packages = ['kinlin'],
    test_suite='tests',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
    ]
)
