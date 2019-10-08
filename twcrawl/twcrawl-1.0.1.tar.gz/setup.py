import setuptools
import src.twcrawl as project

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as fh:
    requirements = fh.readlines()

setuptools.setup(
    name="twcrawl",
    version=project.version,
    author="Michael Hohl",
    author_email="me@michaelhohl.net",
    description="Twitter crawler to download a followers graph and statuses into a local database.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hohl/twcrawl",
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    entry_points={
        'console_scripts': [
            'twcrawl = twcrawl.cli:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=requirements,
    zip_safe=False
)
