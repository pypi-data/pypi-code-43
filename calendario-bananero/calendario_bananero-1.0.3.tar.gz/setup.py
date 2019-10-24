import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="calendario_bananero",
    version="1.0.3",
    author="Sebastian Caceres",
    author_email="chevass@protonmail.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PinkFLoyd92/date_helper",
    packages=['calendario_bananero'],
    py_modules=['calendario_bananero'],
    install_requires=['pytz'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
