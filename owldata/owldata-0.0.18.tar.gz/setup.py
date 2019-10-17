from setuptools import setup
from owldata.__version__ import __version__
import io

with open('requirements.txt', encoding='utf-8') as fid:
    requires = [line.strip() for line in fid]
    
# with open("README.md", encoding='utf-8') as f:
#     long_description = f.read()

def read(path):
    with io.open(path, mode='r', encoding='utf-8') as f:
        return f.read()

packages = [
    'owldata'
]

setup(
    name = 'owldata',
    version = __version__,
    description = 'Testing version',
    long_description = read('README.md'),
    long_description_content_type = "text/markdown",
    author = 'Owl Corp.',
    author_email = 'owldb@cmoney.com.tw',
    install_requires = requires,
    url = 'https://owl.cmoney.com.tw/Owl/',
    packages = packages
)
