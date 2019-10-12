import setuptools

# 读取项目的readme介绍
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bestpkg_001",# 项目名称，保证它的唯一性，不要跟已存在的包名冲突即可
    version="0.0.1",
    author='Zhong Lei',
    author_email='625015751@qq.com',
    description="一个牛逼的程序", # 项目的一句话描述
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/hylinux1024/niubiproject",# 项目地址
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
    ],
)

