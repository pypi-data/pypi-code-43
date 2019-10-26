from distutils.core import setup
import os,alphaqso.__init__
from glob import glob

def get_data_names(root):
    '''
    Return list of all filenames (not directories) under root.
    '''
    temp = [root+'/*']
    for dirpath, dirnames, filenames in os.walk(root):
        temp.extend((os.path.join(dirpath, d, '*') for d in dirnames))
    names = []
    for path in temp:
        if any(os.path.isfile(f) for f in glob(path)):
            names.append(path.replace('alphaqso/',''))
    return names

package_data = {'alphaqso' : get_data_names('alphaqso/data')}

setup(
    name="alphaqso",
    version=alphaqso.__version__,
    author="Vincent Dumont",
    author_email="vincentdumont11@gmail.com",
    packages=["alphaqso"],
    requires=["numpy","matplotlib","scipy","astropy"],
    package_data = package_data,
    include_package_data=True,
    scripts = glob('bin/*'),
    url="https://astroquasar.gitlab.io/programs/alphaqso",
    description="Fine-structure constant measurement and distortion analysis tools.",
    install_requires=[]
)
