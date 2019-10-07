from setuptools import setup, find_packages

# 打包到pypi的详细链接：https://packaging.python.org/guides/distributing-packages-using-setuptools/
# python打包时的命名域的解释链接：https://packaging.python.org/guides/packaging-namespace-packages/
# setuptools打包说明链接：https://setuptools.readthedocs.io/en/latest/setuptools.html
# setup.py的例子(注意命名域)：https://github.com/pypa/sampleproject/blob/master/setup.py
#
# setup()中package_data（重点）、packages、data_files这三个参数要着重理解。
#
# 终端输入命令 python setup.py sdist打包后先别急着上传到pypi，先在本地项目中的dist文件夹（打包生成的）
# 下查看打包后的文件 *.tar.gz，看看是否有你想要打包进的文件，再终端输入命令 twine upload dist/* 上传打包后的文件。
#
# 当你决定要把打包后的文件上传到pypi时，setup()的version参数（版本号）一定要比之前更高，不然会出现400文件名重复的错误。
#
# 除了代码（.py）的额外文件（如.png、.db等数据文件）一定要在setup()的package_data中说明，data_files参数是
# 如果你的数据文件想被其他程序调用就把这些数据文件暴露出来。
#
# 打包的.py中的代码（包括__init__.py）如果想调用自身项目的其他模块的函数，一定是 import namespace.*
# ，即一定要在开头加命名域。

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cn_sort",
    version="0.5.3",
    license="MIT",
    description="按拼音和笔顺快速排序大量简体中文词组（支持百万数量级）。",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="bmxbmx3",
    author_email="982766639@qq.com",
    url="https://github.com/bmxbmx3/cn_sort/tree/master",
    download_url="https://github.com/bmxbmx3/cn_sort/releases",
    keywords=[
        "njupt chinese word sort pronounce bihua 排序 中文 拼音 笔画 笔顺 词 汉字",
    ],
    install_requires=[
        "pypinyin",
        "jieba"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
    ],
    package_data={
        "": ["res/*.csv"]
    },
    packages=find_packages(include=["cn_sort"],exclude=["modify_db"]),
    python_requires=">=3.6"
)
