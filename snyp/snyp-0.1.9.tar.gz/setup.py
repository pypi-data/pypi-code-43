import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name='snyp',
    version='0.1.9',
    author='Bujar Murati',
    author_email = 'bmurati95@gmail.com',
    description='Snyp is a command line utility that streamlines the process of creating text based documentation and programming tutorials in Markdown.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url = 'https://github.com/BujarMurati/snyp',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'Click',
        'configparser'
    ],
    package_data = {
        'snyp':['snyp.ini']
    },
    entry_points='''
        [console_scripts]   
        snyp=snyp.snyp:snyp
    ''',
)