import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="conapp",
    version="0.0.4",
    author="drew887 Andrew Mcdonald",
    author_email="drew887121@gmail.com",
    description="A simple config applier",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/drew887/conapp/src/master/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'conapp = conapp.__main__:main'
        ]
    },
)
