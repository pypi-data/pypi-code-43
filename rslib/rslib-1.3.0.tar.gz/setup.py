import codecs
from setuptools import find_packages, setup

with codecs.open('README.md', 'r', 'utf8') as reader:
    long_description = reader.read()

# with codecs.open('requirements.txt', 'r', 'utf8') as reader:
#     install_requires = list(map(lambda x: x.strip(), reader.readlines()))

setup(
    name='rslib',
    version='1.3.0',
    packages=find_packages(),
    url='https://gitlab.leihuo.netease.com/userpersona/diting/rslib',
    license='MIT',
    author='wangkai02',
    author_email='wangkai02@corp.netease.com',
    description='offline train framework in diting group',
    # install_requires=install_requires,
    long_description=long_description,
    long_description_content_type='text/markdown'
)
