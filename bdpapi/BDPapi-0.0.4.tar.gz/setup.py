from setuptools import setup, find_packages      

setup(
    name = "BDPapi",   
    version = "0.0.4",  
    keywords = ["pip", "BDPapi"],
    description = "BDP api",
    long_description = "BDP api",
    license = "MIT Licence",

    url = "https://github.com/haizhiml/BDP.git",     
    author = "blue",
    author_email = "xuguozheng@haizhi.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["numpy", "requests"]
)
