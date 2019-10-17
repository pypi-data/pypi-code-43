from setuptools import find_packages, setup

setup(
    name='brewblox-deploy',
    use_scm_version={'root': '..', 'local_scheme': lambda v: ''},
    url='https://github.com/BrewBlox/brewblox-deployment',
    author='BrewPi',
    author_email='development@brewpi.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='brewblox deployment cli',
    packages=find_packages(exclude=['test']),
    include_package_data=True,
    install_requires=[
        'click',
    ],
    python_requires='>=3.6',
    setup_requires=['setuptools_scm'],
    entry_points={
        'console_scripts': [
            'bbdeploy = brewblox_deploy.__main__:cli',
        ]
    }
)
