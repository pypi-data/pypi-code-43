
# python setup.py bdist_egg     # 生成类似 edssdk-0.0.1-py2.7.egg，支持 easy_install 
# python setup.py sdist         # 生成类似 edssdk-0.0.1.tar.gz，支持 pip
# 打包后的dist上传到PyPi服务器
# python setup.py sdist upload
#############################################
from setuptools import setup, find_packages,Extension
from kcw.config import confkcw
import os
def get_file(folder='./',lists=[]):
    lis=os.listdir(folder)
    for files in lis:
        if not os.path.isfile(folder+"/"+files):
            if files!='__pycache__':
                lists.append(folder+"/"+files)
            get_file(folder+"/"+files,lists)
        else:
            pass
    return lists
b=get_file("kcw",['kcw'])
setup(
    name = confkcw["name"],
    version = confkcw["version"], #版本号
    description = confkcw["description"],
    author_email = confkcw["author_email"],
    packages =  b,
    install_requires = confkcw["install_requires"] #这是一个数组，里边包含的是咱的pip项目引用到的第三方库，如果你的项目有用到第三方库，要在这里添上第三方库的包名，如果用的第三方版本不是最新版本，还要有版本号。
)