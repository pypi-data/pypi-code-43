import setuptools

# 读取项目的readme介绍
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="HeadersToDict",
    version="1.0.3",
    author="lyg", # 项目作者
    author_email="",
    description="把headers转化成为dict", # 项目的一句话描述
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    install_requires=[],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)