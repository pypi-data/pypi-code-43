import setuptools


def version():
    with open('talar/VERSION', 'r') as file:
        return file.read()


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-talar",
    version=version(),
    author="Talar",
    author_email="kamil.obstawski@rakki.xyz",
    description="Django app for [Talar.app](https://talar.app) service.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/rakki-software/django-talar/src/",
    packages=setuptools.find_packages(),
    install_requires=[
        'django >=2.1,<2.3', 'djangorestframework >=3.9,<4.0',
        'pyjwt >=1.7,<1.8',
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
