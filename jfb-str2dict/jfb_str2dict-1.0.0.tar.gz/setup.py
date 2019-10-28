'''
@File       :   setup.py
@Author     :   Jiang Fubang
@Time       :   2019-10-28 16:40
@Version    :   1.0
@Contact    :   luckybang@163.com
@Dect       :   None
'''

from setuptools import setup, find_packages

setup(
    name = "jfb_str2dict",
    version = "1.0.0",
    keywords = ("str", "jfb_str2dict","dict"),
    description = "String to dictionary tool",
    long_description = "This tool converts a dictionary for a string",
    license = "MIT Licence",

    url = "https://github.com/jiangfubang/jfb_str2dict",     #项目相关文件地址，一般是github
    author = "Jiang Fubang",
    author_email = "luckybang@163.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any"
)