from setuptools import setup, find_packages

import mq_consumer

setup(
    name='mq_consumer',
    version=mq_consumer.__version__,
    author='Ruzzy Rullezz',
    author_email='ruslan@lemimi.ru',
    packages=find_packages(),
    package_dir={'mq_consumer': 'mq_consumer'},
    install_requires=[
        'pika==1.1.0',
    ],
)