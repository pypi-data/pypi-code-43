
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
    version = confkcw["version"],
    description = confkcw["description"],
    author = confkcw["author"],
    author_email = confkcw["author_email"],
    maintainer = confkcw["maintainer"],
    maintainer_email = confkcw["maintainer_email"],
    url=confkcw['url'],
    packages =  b,
    install_requires = confkcw["install_requires"],
    package_data = {
        '': ['*.html', '*.js','*.css','*.jpg','*.png','*.gif'],
        'kcw/file/dist': ['*']
    }
)