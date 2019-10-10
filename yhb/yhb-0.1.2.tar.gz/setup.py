from setuptools import setup, find_packages

setup(
    name='yhb',
    version='0.1.2',
    description='A package for quick using utils',
    packages=find_packages(),
    url='https://github.com/Jiramew/spoon',
    license='BSD License',
    author='Jiramew',
    author_email='hanbingflying@sina.com',
    maintainer='Jiramew',
    maintainer_email='hanbingflying@sina.com',
    platforms=["all"],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        'pymysql>=0.8.0',
        'requests',
        'pycryptodomex'
    ]
)
