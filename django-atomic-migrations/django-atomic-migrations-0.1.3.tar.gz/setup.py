import setuptools
import subprocess

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-atomic-migrations",
    version=subprocess.check_output(['git', 'describe', '--tags']).decode().strip(),
    author="Richard Kojedzinszky",
    author_email="richard@kojedz.in",
    description="Wraps migration step runs in transactions in Django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rkojedzinszky/django-atomic-migrations",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
