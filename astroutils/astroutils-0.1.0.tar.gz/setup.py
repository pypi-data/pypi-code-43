import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="astroutils",
    version="0.1.0",
    author="Xinlun Cheng",
    author_email="chengxinlun@gmail.com",
    description="Many utility functions for astronomical research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chengxinlun/astroutils",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)
