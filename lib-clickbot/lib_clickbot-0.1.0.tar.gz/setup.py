from setuptools import setup, find_packages

setup(
    name='lib_clickbot',
    packages=find_packages(),
    version='0.1.0',
    author='Justin Furuness',
    author_email='jfuruness@gmail.com',
    url='https://github.com/jfuruness/lib_clickbot.git',
    download_url='https://github.com/jfuruness/lib_clickbot.git',
    keywords=['Furuness', 'furuness', 'pypi', 'package', 'clickbot'],  # arbitrary keywords
    test_suite='nose.collector',
    tests_require=['nose'],
    install_requires=[
        'setuptools>=40.8.0',
        'pynput>=1.4.4'
    ],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'],
    entry_points={
        'console_scripts': [
            'clickbot = lib_clickbot.__main__:main'
        ]},
)

