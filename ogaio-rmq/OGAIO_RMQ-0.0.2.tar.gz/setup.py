from setuptools import setup, find_packages

setup(
    name='OGAIO_RMQ',
    description="OnGrid Aio json-rpc over RMQ lib for microservices",
    version='0.0.2',
    packages=find_packages(),
    author='Nimond',
    author_email='a.zhiltsov@ongrid.pro',
    url='https://github.com/OnGridSystems/aiorpc_rmq',
    install_requires=['aio-pika'],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python :: 3.7",
    ],
)