from distutils.core import setup

setup(
    name='TxConnect',
    version='0.2.1',
    author='Zack Umar',
    author_email='zackumar2@gmail.com',
    packages=['txconnect'],
    url='https://pypi.org/project/TxConnect/',
    description='TxConnect Scraper for SCUC',
    long_description=open('README.txt').read(),
    install_requires=[
        "bs4==0.0.1",
        "html5lib==1.0.1",
        "requests==2.22.0",
    ],
)