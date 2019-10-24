from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.readlines()

with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(
        name ='annofetch',
        version ='1.0.0',
        author ='Sarah Kasemann',
        author_email ='sarah.kasemann@uni-bielefeld.de',
        url ='',
        description ='Command Line Script to fetch annotations.',
        long_description = long_description,
        long_description_content_type ="text/markdown",
        license ='GPL',
        packages = ['annofetch', 'annofetch.lib', 'annofetch.lib.database', 'annofetch.lib.exception', 'annofetch.lib.configuration'],
        entry_points ={
            'console_scripts': [
                'annofetch = annofetch.main:main'
            ]
        },
        include_package_data=True,
        package_data={
        'annofetch/lib/configuration':['annofetch/lib/configuration/config.ini'],
        'annofetch/lib/database':['cognames_function.tab','fun2003-2014.tab']
        },
        data_files=[('annofetch/Example', ['annofetch/Example/test_accessions.txt','annofetch/Example/README.md'])
                    ],
        classifiers =(
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ),
        keywords ='accession fetching annotations',
        install_requires = requirements,
)
