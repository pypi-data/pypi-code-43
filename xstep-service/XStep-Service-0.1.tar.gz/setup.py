import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='XStep-Service',
    version='0.1',
    description='The interface for controlling X-Step Hw over REST Api.',
    url='http://github.com/storborg/funniest',
    author='Markus Veijola, Jukka-Pekka Salminen',
    author_email='markus_veijola@mentor.com',
    license='BSD',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
