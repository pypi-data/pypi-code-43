# -*- coding: utf-8 -*-

"""
@author: GuYouda (guyouda@baidu.com)
@date: 2019/10/15 19:49
@desc: 
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gyd-test",  # 包名称
    version="0.0.2",  # 包版本
    author="Gu Youda",  # 作者
    license='MIT',  # 协议简写
    author_email="guyouda@qq.com",  # 作者邮箱
    description="A small example package",  # 工具包简单描述
    long_description=long_description,  # readme 部分
    long_description_content_type="text/markdown",  # readme 文件类型
    install_requires=[  # 工具包的依赖包
        'requests>=2.22.0',
        'urllib3>=1.25.3',
    ],
    url="https://www.baidu.com/",  # 包的开源链接
    platforms="any",
    packages=setuptools.find_packages(),  # 不用动，会自动发现
    classifiers=[  # 给出了指数和点子你的包一些额外的元数据
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
