from setuptools import find_packages, setup

setup(
    name="nd_project",
    version="9.9.7",
    author="Nicola Dobner",
    author_mail="nicola.dobner@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    package_dir={'':'.'},
    description="HELLO DESCRIPTION FTW!"
)