import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django_tfactory",
    version="0.0.1",
    author="Ashish Sahu",
    author_email="spiraldeveloper@gmail.com",
    description="A Django template factory",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SpiralDeveloper/django_tfactory",
    packages=setuptools.find_packages(),
    install_requires=[
          'beautifulsoup4',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)