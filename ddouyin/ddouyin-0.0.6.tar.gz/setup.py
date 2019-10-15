import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ddouyin",
    version="0.0.6",
    author="冷大大猫",
    author_email="yang2210670@163.com",
    description="一个下载抖音无水印视频的包",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yang2210670/py_study",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
