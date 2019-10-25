'''
@Descripttion: 
@Author: Defu Li
@Date: 2019-10-25 22:38:08
'''
from setuptools import setup, find_packages

setup(
    name = "seawiki",
    version = "2019.10.25.1",
    description = "Input a question, search wikipedia for the most similar documents",
    license = "MIT Licence",

    url = "https://github.com/DefuLi/Sea-Wiki",
    author = "defuli",
    author_email = "defuli.go@qq.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ['elasticsearch==7.0.5', 'joblib==0.14.0', 'nltk==3.4.5', 'numpy==1.16.2', 'pandas==0.25.2',
                        'pexpect==4.2.1', 'pkg-resources==0.0.0', 'prettytable==0.7.2', 'ptyprocess==0.6.0',
                        'python-dateutil==2.8.0', 'pytz==2019.3', 'regex==2019.8.19', 'scikit-learn==0.21.3', 'scipy==1.3.1',
                        'six==1.12.0', 'termcolor==1.1.0', 'torch==1.1.0', 'tqdm==4.36.1', 'urllib3==1.25.6']
)
