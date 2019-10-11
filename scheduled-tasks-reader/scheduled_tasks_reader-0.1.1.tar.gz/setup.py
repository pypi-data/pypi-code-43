from setuptools import setup, find_packages
from os import path

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="scheduled_tasks_reader",
    version="0.1.1",
    author="UL15",
    author_email="FerienInThailand15@protonmail.com",
    description="A program to various information of scheduled tasks.",
    license="MIT",
    packages=["."],
    package_data={
        '.': ['*.html'],
    },
    entry_points={
        'console_scripts': [
            'scheduled_tasks_reader = scheduled_tasks_reader:main'
        ],
    },
    install_requires=["xmltodict==0.12.0", "pandas==0.25.0"],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
