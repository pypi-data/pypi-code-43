from setuptools import setup, find_packages

setup(
    name='OGAIO_RMQ',
    version='0.0.1',
    packages=find_packages(),
    author='Nimond',
    author_email='a.zhiltsov@ongrid.pro',
    url='https://github.com/OnGridSystems/aiorpc_rmq',
    install_requires=['aio-pika'],
)