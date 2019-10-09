import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="taboo",
    version="0.8.8",
    author="Zhong Haoxi",
    author_email="zhonghaoxi@yeah.net",
    description="Codes for taboo.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/haoxizhong/taboo",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
