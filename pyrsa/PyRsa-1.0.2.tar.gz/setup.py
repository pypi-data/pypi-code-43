import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyRsa",
    version="1.0.2",
    author="张协涛",
    author_email="zxt502838517@gmail.com",
    description="python enables rsa encryption",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hibiscustoyou/pyrsa",
    packages=setuptools.find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'PyRsa=PyRsa:main'
        ],
    },
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)